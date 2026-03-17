import pytest
import json
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.gemini_api_wrapper import GeminiAPIWrapper

@pytest.mark.anyio
async def test_generate_content_empty_retry(monkeypatch):
    # Mock ConfigManager, AuthService, UsageTracker
    mock_config = MagicMock()
    mock_config.get.side_effect = lambda k, default=None: {
        "api_timeout": 300,
        "api_max_retries": 1,
        "api_retry_delay": 0.1, # Short delay for testing
    }.get(k, default)
    
    mock_auth = MagicMock()
    mock_auth.accounts = [{"email": "test@example.com", "status": "valid", "projectId": "p1", "access": "token"}]
    mock_auth.get_next_account.return_value = mock_auth.accounts[0]
    async def mock_get_valid(acc): return acc
    mock_auth.get_valid_account = mock_get_valid
    
    mock_usage = MagicMock()
    
    wrapper = GeminiAPIWrapper(config=mock_config, auth_service=mock_auth, usage_tracker=mock_usage)
    # Set short max_delay for backoff to speed up test
    wrapper.backoff_manager.max_delay = 0.5
    
    # Mock httpx.AsyncClient
    responses = [
        # First response: Empty SSE data
        AsyncMock(status_code=200, iter_lines=MagicMock(return_value=[b"data: {}\n"])),
        # Second response: Whitespace only
        AsyncMock(status_code=200, iter_lines=MagicMock(return_value=[b'data: {"response": {"candidates": [{"content": {"parts": [{"text": "   "}]}}]}}\n'])),
        # Third response: Success
        AsyncMock(status_code=200, iter_lines=MagicMock(return_value=[b'data: {"response": {"candidates": [{"content": {"parts": [{"text": "Hello world"}]}}]}}\n']))
    ]
    
    call_count = 0
    async def mock_post(*args, **kwargs):
        nonlocal call_count
        resp = responses[call_count]
        call_count += 1
        return resp

    # We need to mock the context manager __aenter__
    mock_client = AsyncMock()
    mock_client.post = mock_post
    mock_client.__aenter__.return_value = mock_client
    
    with patch("httpx.AsyncClient", return_value=mock_client):
        text = await wrapper.generate_content_async("test prompt")
        assert text == "Hello world"
        assert call_count == 3
