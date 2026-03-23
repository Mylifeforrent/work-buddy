"""Tests for LLM factory functions."""

import os
import pytest
from unittest.mock import patch, MagicMock

from work_buddy.core.llm import get_llm, get_embeddings
from work_buddy.core.config import AppConfig


class TestGetLLM:
    """Tests for get_llm factory function."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-openai-key"})
    def test_openai_provider_returns_chat_openai(self):
        """Test that OpenAI provider returns correctly configured ChatOpenAI."""
        config = AppConfig(llm_provider="openai", llm_model="gpt-4o")

        llm = get_llm(config, temperature=0.5)

        assert llm is not None
        assert llm.model_name == "gpt-4o"
        assert llm.temperature == 0.5

    @patch.dict(os.environ, {"DASHSCOPE_API_KEY": "test-dashscope-key"})
    def test_dashscope_provider_uses_openai_compatible_endpoint(self):
        """Test that DashScope provider uses OpenAI-compatible endpoint."""
        config = AppConfig(llm_provider="dashscope", llm_model="qwen-plus")

        llm = get_llm(config)

        assert llm is not None
        assert llm.model_name == "qwen-plus"
        # DashScope uses OpenAI-compatible endpoint
        assert llm.openai_api_base == "https://dashscope.aliyuncs.com/compatible-mode/v1"

    @patch.dict(os.environ, {"DASHSCOPE_API_KEY": "test-dashscope-key"})
    def test_dashscope_auto_selects_qwen_model(self):
        """Test that DashScope auto-selects qwen-plus when gpt model is configured."""
        config = AppConfig(llm_provider="dashscope", llm_model="gpt-4o")

        llm = get_llm(config)

        # Should auto-switch from gpt-4o to qwen-plus
        assert llm.model_name == "qwen-plus"

    def test_openai_missing_api_key_raises_error(self):
        """Test that missing OpenAI API key raises clear error."""
        config = AppConfig(llm_provider="openai", llm_model="gpt-4o")

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_llm(config)

            assert "OPENAI_API_KEY" in str(exc_info.value)

    def test_dashscope_missing_api_key_raises_error(self):
        """Test that missing DashScope API key raises clear error."""
        config = AppConfig(llm_provider="dashscope", llm_model="qwen-plus")

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_llm(config)

            assert "DASHSCOPE_API_KEY" in str(exc_info.value)

    def test_unsupported_provider_raises_error(self):
        """Test that unsupported provider raises clear error."""
        config = AppConfig(llm_provider="unknown-provider", llm_model="model")

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_llm(config)

            assert "Unsupported LLM provider" in str(exc_info.value)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_loads_config_if_not_provided(self):
        """Test that config is loaded from app.yaml if not provided."""
        with patch("work_buddy.core.config.load_app_config") as mock_load:
            mock_load.return_value = AppConfig(llm_provider="openai", llm_model="gpt-4o")

            llm = get_llm()

            mock_load.assert_called_once()
            assert llm is not None


class TestGetEmbeddings:
    """Tests for get_embeddings factory function."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-openai-key"})
    def test_openai_embeddings(self):
        """Test that OpenAI provider returns correctly configured embeddings."""
        config = AppConfig(llm_provider="openai")

        embeddings = get_embeddings(config)

        assert embeddings is not None
        assert embeddings.model == "text-embedding-3-small"

    @patch.dict(os.environ, {"DASHSCOPE_API_KEY": "test-dashscope-key"})
    def test_dashscope_embeddings(self):
        """Test that DashScope provider returns correctly configured embeddings."""
        config = AppConfig(llm_provider="dashscope")

        embeddings = get_embeddings(config)

        assert embeddings is not None
        # DashScope uses text-embedding-v3 model
        assert embeddings.model == "text-embedding-v3"
        # Should use OpenAI-compatible endpoint
        assert embeddings.openai_api_base == "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def test_embeddings_missing_api_key_raises_error(self):
        """Test that missing API key for embeddings raises clear error."""
        config = AppConfig(llm_provider="openai")

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_embeddings(config)

            assert "OPENAI_API_KEY" in str(exc_info.value)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_embeddings_loads_config_if_not_provided(self):
        """Test that config is loaded from app.yaml if not provided."""
        with patch("work_buddy.core.config.load_app_config") as mock_load:
            mock_load.return_value = AppConfig(llm_provider="openai")

            embeddings = get_embeddings()

            mock_load.assert_called_once()
            assert embeddings is not None