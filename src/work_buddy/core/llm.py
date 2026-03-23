"""LLM Factory for supporting multiple LLM providers.

Supports:
- OpenAI (default)
- DashScope/Qwen (OpenAI-compatible API)
"""

import os
from typing import Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from work_buddy.core.config import AppConfig


def get_llm(
    config: Optional[AppConfig] = None,
    temperature: float = 0.0,
    **kwargs
) -> ChatOpenAI:
    """Create an LLM instance based on the configured provider.

    Args:
        config: Application configuration. If not provided, loads from app.yaml
        temperature: Temperature for the LLM responses
        **kwargs: Additional arguments passed to ChatOpenAI

    Returns:
        ChatOpenAI instance configured for the appropriate provider

    Raises:
        ValueError: If required API key is not set
    """
    if config is None:
        from work_buddy.core.config import load_app_config
        config = load_app_config()

    provider = config.llm_provider.lower()
    model = config.llm_model

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            **kwargs
        )

    elif provider == "dashscope":
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY environment variable is not set")

        # DashScope provides an OpenAI-compatible API
        # Default model for DashScope is qwen-plus if not specified
        if model.startswith("gpt"):
            # User hasn't changed the model, use a sensible default for Qwen
            model = "qwen-plus"

        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            **kwargs
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported providers: openai, dashscope"
        )


def get_embeddings(config: Optional[AppConfig] = None) -> OpenAIEmbeddings:
    """Create an embeddings instance based on the configured provider.

    Args:
        config: Application configuration. If not provided, loads from app.yaml

    Returns:
        OpenAIEmbeddings instance configured for the appropriate provider

    Raises:
        ValueError: If required API key is not set
    """
    if config is None:
        from work_buddy.core.config import load_app_config
        config = load_app_config()

    provider = config.llm_provider.lower()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=api_key
        )

    elif provider == "dashscope":
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY environment variable is not set")

        # DashScope embeddings via OpenAI-compatible API
        return OpenAIEmbeddings(
            model="text-embedding-v3",
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported providers: openai, dashscope"
        )