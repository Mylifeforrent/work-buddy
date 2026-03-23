## ADDED Requirements

### Requirement: Support multiple LLM providers
The system SHALL support multiple LLM providers through a unified factory interface, enabling seamless switching between providers (OpenAI, DashScope/Qwen) via configuration without code changes.

#### Scenario: Use OpenAI as LLM provider
- **WHEN** user configures `llm_provider: openai` in app.yaml and sets `OPENAI_API_KEY` environment variable
- **THEN** the system uses OpenAI API with the configured model (gpt-4o, gpt-4-turbo, gpt-3.5-turbo)

#### Scenario: Use DashScope/Qwen as LLM provider
- **WHEN** user configures `llm_provider: dashscope` in app.yaml and sets `DASHSCOPE_API_KEY` environment variable
- **THEN** the system uses DashScope API with OpenAI-compatible endpoint and the configured model (qwen-turbo, qwen-plus, qwen-max)

### Requirement: LLM Factory Pattern
The system SHALL implement a factory pattern for LLM instantiation that:
- Accepts configuration object specifying provider and model
- Returns a LangChain-compatible ChatOpenAI instance configured for the appropriate provider
- Handles provider-specific API endpoints and authentication

#### Scenario: Factory returns correct LLM instance
- **WHEN** an agent requests an LLM via `get_llm(config, temperature)`
- **THEN** the factory returns a properly configured ChatOpenAI instance with correct base_url, api_key, and model

#### Scenario: Missing API key raises clear error
- **WHEN** an agent requests an LLM but the required API key is not set
- **THEN** the system raises a clear ValueError indicating which environment variable is missing

### Requirement: Embeddings Factory Pattern
The system SHALL implement a factory pattern for embeddings instantiation that:
- Supports same providers as LLM factory
- Returns LangChain-compatible OpenAIEmbeddings instance
- Uses provider-appropriate embedding models

#### Scenario: Factory returns correct embeddings instance
- **WHEN** an agent requests embeddings via `get_embeddings(config)`
- **THEN** the factory returns a properly configured OpenAIEmbeddings instance with correct base_url and model

### Requirement: Provider-specific endpoint configuration
The system SHALL configure provider-specific API endpoints:
- OpenAI: Default endpoint (api.openai.com)
- DashScope: OpenAI-compatible endpoint (dashscope.aliyuncs.com/compatible-mode/v1)

#### Scenario: DashScope uses OpenAI-compatible endpoint
- **WHEN** provider is dashscope
- **THEN** the system configures base_url as `https://dashscope.aliyuncs.com/compatible-mode/v1`

### Requirement: Default model selection per provider
The system SHALL provide sensible default models per provider:
- OpenAI: gpt-4o
- DashScope: qwen-plus (when config specifies a gpt-* model)

#### Scenario: Auto-select appropriate default model
- **WHEN** user configures dashscope provider but leaves llm_model as default gpt-4o
- **THEN** the system automatically uses qwen-plus instead

### Requirement: Configuration schema for LLM settings
The system SHALL support the following configuration in app.yaml:

```yaml
llm_provider: openai | dashscope
llm_model: <model-name>
```

#### Scenario: Load LLM config from app.yaml
- **WHEN** the application starts
- **THEN** it loads llm_provider and llm_model from configs/app.yaml

### Requirement: Environment variable security
The system SHALL read API keys from environment variables only, never from config files.

#### Scenario: API key from environment only
- **WHEN** the system needs an API key
- **THEN** it reads from environment variable (OPENAI_API_KEY or DASHSCOPE_API_KEY)
- **AND** never reads or stores API keys in YAML config files

### Requirement: Extensibility for new providers
The system SHALL be designed to easily add new LLM providers by:
- Adding new provider branch in factory function
- Implementing provider-specific endpoint and model defaults
- No changes required to agent code

#### Scenario: Add new provider without agent changes
- **WHEN** a new provider is added to the factory
- **THEN** all existing agents automatically support the new provider without code changes