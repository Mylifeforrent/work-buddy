import os
from typing import List, Dict, Tuple, Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from work_buddy.services.confluence_service import ConfluenceService
from work_buddy.core.config import load_app_config


class ConfluenceRagAgent:
    """Agent that retrieves and answers questions based on Confluence documentation using RAG."""
    
    def __init__(self, confluence: ConfluenceService, persist_directory: str = ".chroma_db"):
        self.confluence = confluence
        self.app_config = load_app_config()
        self.persist_directory = persist_directory
        
        # In a constrained mock environment, API keys might be missing, 
        # so instantiation happens but might fail if called without keys
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.llm = ChatOpenAI(model=self.app_config.llm_model, temperature=0.0)
        
        os.makedirs(persist_directory, exist_ok=True)
        self.vectorstore = Chroma(
            collection_name="confluence_docs",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    async def ingest_documents(self, space_key: str = None, term: str = "") -> int:
        """Fetch documents from Confluence and ingest them into ChromaDB.

        Args:
            space_key: Optional Confluence space key to limit ingestion
            term: Optional search term to filter pages

        Returns:
            Number of document chunks ingested
        """
        # Fetch pages - use list_pages if space_key provided, otherwise search
        if space_key:
            pages = await self.confluence.list_pages(space_key, limit=50)
        else:
            pages = await self.confluence.search_pages(term, space_key, limit=50)

        if not pages:
            return 0

        docs = []
        for page in pages:
            # Handle both SearchResult (from search) and ConfluencePage (from list_pages)
            if hasattr(page, 'page'):
                # It's a SearchResult
                page_obj = page.page
            else:
                # It's a ConfluencePage
                page_obj = page

            # Fetch full page content if not already present
            if not page_obj.body:
                full_page = await self.confluence.get_page_content(page_obj.id)
                if full_page:
                    page_obj = full_page

            if page_obj and page_obj.body:
                doc = Document(
                    page_content=page_obj.body,
                    metadata={
                        "source": page_obj.url or f"confluence://{page_obj.id}",
                        "title": page_obj.title,
                        "id": page_obj.id,
                        "space_key": page_obj.space_key
                    }
                )
                docs.append(doc)

        if not docs:
            return 0

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        # Add to vectorstore
        if splits:
            self.vectorstore.add_documents(documents=splits)

        return len(splits)

    async def query_support_docs(self, query: str) -> Tuple[str, List[str]]:
        """Query the RAG engine for troubleshooting help. Returns (Answer, List of Source URLs)."""
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})

        system_prompt = (
            "You are a helpful support engineering assistant. "
            "Use the following pieces of retrieved context to answer the troubleshooting query. "
            "If you don't know the answer or the context doesn't contain the answer, "
            "just say that you don't find relevant information in the documentation. "
            "Always include links to the source documentation if applicable."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt + "\n\nContext: {context}"),
            ("human", "{input}"),
        ])

        # Use LCEL to build the RAG chain
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": retriever | format_docs, "input": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        response = rag_chain.invoke(query)

        # Also retrieve docs to get sources
        docs = retriever.invoke(query)
        sources = []
        for doc in docs:
            src = doc.metadata.get("source")
            if src and src not in sources:
                sources.append(src)

        answer = response
        # Append sources to the answer
        if sources:
            answer += "\n\n**Sources:**\n"
            for src in sources:
                answer += f"- {src}\n"

        return answer, sources

    def _rerank_documents(self, query: str, documents: List[Document], top_k: int = 3) -> List[Document]:
        """Re-rank documents based on relevance to the query using LLM scoring.

        Args:
            query: The user's query
            documents: List of retrieved documents
            top_k: Number of top documents to return

        Returns:
            Re-ranked list of top_k documents
        """
        if len(documents) <= top_k:
            return documents

        # Use LLM to score each document's relevance
        scored_docs = []
        for doc in documents:
            score_prompt = ChatPromptTemplate.from_messages([
                ("system", "Score the relevance of this document to the query on a scale of 0-10. "
                          "Return ONLY the numeric score, nothing else."),
                ("human", "Query: {query}\n\nDocument title: {title}\nDocument excerpt: {content}")
            ])

            chain = score_prompt | self.llm
            try:
                response = chain.invoke({
                    "query": query,
                    "title": doc.metadata.get("title", ""),
                    "content": doc.page_content[:500]  # Use first 500 chars for scoring
                })
                score = float(response.content.strip())
            except (ValueError, AttributeError):
                score = 0.0

            scored_docs.append((score, doc))

        # Sort by score descending and return top_k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored_docs[:top_k]]

    async def search_with_reranking(self, query: str, top_k: int = 5) -> Tuple[str, List[Dict]]:
        """RAG search pipeline with re-ranking: query -> embed -> retrieve -> re-rank -> respond.

        Args:
            query: The search query
            top_k: Number of initial documents to retrieve before re-ranking

        Returns:
            Tuple of (answer string, list of source info dicts)
        """
        # Step 1: Retrieve more documents than needed for re-ranking
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": top_k * 2})
        initial_docs = retriever.invoke(query)

        # Step 2: Re-rank documents
        reranked_docs = self._rerank_documents(query, initial_docs, top_k=top_k)

        # Step 3: Generate answer from re-ranked context
        context_text = "\n\n".join([
            f"Document: {doc.metadata.get('title', 'Unknown')}\n{doc.page_content}"
            for doc in reranked_docs
        ])

        answer_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that answers questions based on Confluence documentation. "
                      "Use the provided context to give accurate, helpful answers. "
                      "If the context doesn't contain enough information, say so clearly. "
                      "Always cite the document titles you used in your answer."),
            ("human", "Query: {query}\n\nContext:\n{context}")
        ])

        chain = answer_prompt | self.llm
        response = chain.invoke({"query": query, "context": context_text})

        # Collect source information
        sources = []
        for doc in reranked_docs:
            sources.append({
                "title": doc.metadata.get("title", ""),
                "url": doc.metadata.get("source", ""),
                "id": doc.metadata.get("id", "")
            })

        return response.content, sources

    async def summarize_document(self, page_id: str) -> Optional[Dict]:
        """Summarize a Confluence document using LLM.

        Args:
            page_id: The Confluence page ID to summarize

        Returns:
            Dict with summary, key_points, and source info, or None if page not found
        """
        # Fetch the full page content
        page = await self.confluence.get_page_content(page_id)
        if not page or not page.body:
            return None

        # Generate summary using LLM
        summary_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a technical documentation summarizer. "
                      "Create a concise summary highlighting the key points of this document. "
                      "Format your response as:\n"
                      "**Summary:** <1-2 sentence overview>\n\n"
                      "**Key Points:**\n- <point 1>\n- <point 2>\n- <etc>"),
            ("human", "Document title: {title}\n\nDocument content:\n{content}")
        ])

        chain = summary_prompt | self.llm

        # Truncate content if too long (avoid token limits)
        max_content = 8000
        content = page.body[:max_content] if len(page.body) > max_content else page.body

        response = chain.invoke({
            "title": page.title,
            "content": content
        })

        return {
            "title": page.title,
            "url": page.url,
            "id": page.id,
            "summary": response.content
        }

    async def suggest_alternative_terms(self, query: str) -> List[str]:
        """Suggest alternative search terms when no results found.

        Args:
            query: The original search query

        Returns:
            List of suggested alternative search terms
        """
        suggest_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a search assistant. Given a search query that returned no results, "
                      "suggest 3-5 alternative search terms that might find related documentation. "
                      "Return only the alternative terms, one per line, no numbering or bullets."),
            ("human", "{query}")
        ])

        chain = suggest_prompt | self.llm
        response = chain.invoke({"query": query})

        # Parse the response into a list
        suggestions = [
            line.strip()
            for line in response.content.strip().split("\n")
            if line.strip()
        ]

        return suggestions[:5]  # Limit to 5 suggestions
