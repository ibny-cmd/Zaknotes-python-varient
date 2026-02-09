import os
import sys
import time
import pytest
import httpx
from unittest.mock import patch, MagicMock
from google.genai import errors, types

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gemini_api_wrapper import GeminiAPIWrapper
from src.config_manager import ConfigManager

@pytest.fixture
def mock_config():
    config = MagicMock(spec=ConfigManager)
    config.get.side_effect = lambda key, default=None: {
        "api_timeout": 5,
        "api_max_retries": 2,
        "api_retry_delay": 1
    }.get(key, default)
    return config

@pytest.fixture
def mock_key_manager():
    manager = MagicMock()
    manager.get_available_key.return_value = "test-key"
    return manager

@patch('google.genai.Client')
@patch('time.sleep')
def test_gemini_api_timeout_retries(mock_sleep, mock_client_class, mock_key_manager, mock_config):
    """Verify that GeminiAPIWrapper retries on timeout."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    # Simulate timeout twice, then success
    timeout_error = httpx.ReadTimeout("Timeout", request=MagicMock())
    mock_client.models.generate_content.side_effect = [
        timeout_error,
        timeout_error,
        MagicMock(text="Success")
    ]
    
    wrapper = GeminiAPIWrapper(key_manager=mock_key_manager, config=mock_config)
    
    response = wrapper.generate_content("test prompt")
    
    assert response == "Success"
    assert mock_client.models.generate_content.call_count == 3
    assert mock_sleep.call_count == 2

@patch('google.genai.Client')
@patch('time.sleep')
def test_gemini_api_timeout_exhaustion(mock_sleep, mock_client_class, mock_key_manager, mock_config):
    """Verify that GeminiAPIWrapper marks key exhausted after max retries."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    # Simulate timeout indefinitely
    timeout_error = httpx.ReadTimeout("Timeout", request=MagicMock())
    mock_client.models.generate_content.side_effect = timeout_error
    
    # We want to stop after max_retries + 1 (initial try + 2 retries = 3 total)
    # But since we have a loop in GeminiAPIWrapper that continues to next key, 
    # we need to make get_available_key return None after first key is exhausted.
    mock_key_manager.get_available_key.side_effect = ["key-1", None]
    
    wrapper = GeminiAPIWrapper(key_manager=mock_key_manager, config=mock_config)
    
    with pytest.raises(Exception, match="No API keys available"):
        wrapper.generate_content("test prompt")
    
    # Total calls for key-1: 1 (initial) + 2 (retries) = 3
    assert mock_client.models.generate_content.call_count == 3
    mock_key_manager.mark_exhausted.assert_called_with("key-1", "gemini-3-flash-preview")
    assert mock_sleep.call_count == 2

@patch('google.genai.Client')
@patch('time.sleep')
def test_generate_content_with_file_timeout(mock_sleep, mock_client_class, mock_key_manager, mock_config):
    """Verify that generate_content_with_file retries on timeout."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    # Mock file upload
    mock_file = MagicMock(name="files/test-file")
    mock_file.state = "ACTIVE"
    mock_client.files.upload.return_value = mock_file
    mock_client.files.get.return_value = mock_file
    
    # Simulate timeout on generate_content (after upload)
    timeout_error = httpx.ReadTimeout("Timeout", request=MagicMock())
    mock_client.models.generate_content.side_effect = [
        timeout_error,
        MagicMock(text="Success")
    ]
    
    wrapper = GeminiAPIWrapper(key_manager=mock_key_manager, config=mock_config)
    
    response = wrapper.generate_content_with_file("path/to/file", "test prompt")
    
    assert response == "Success"
    assert mock_client.models.generate_content.call_count == 2
    assert mock_sleep.call_count == 1

@patch('google.genai.Client')
@patch('time.sleep')
def test_gemini_api_503_retry(mock_sleep, mock_client_class, mock_key_manager, mock_config):
    """Verify that GeminiAPIWrapper waits and retries on 503."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    # Mock 503 error
    error_503 = errors.ClientError(503, {"error": {"message": "Service Unavailable"}})
    mock_client.models.generate_content.side_effect = [
        error_503,
        MagicMock(text="Success")
    ]
    
    wrapper = GeminiAPIWrapper(key_manager=mock_key_manager, config=mock_config)
    
    response = wrapper.generate_content("test prompt")
    
    assert response == "Success"
    assert mock_client.models.generate_content.call_count == 2
    # Should wait 600 seconds for 503
    mock_sleep.assert_called_with(600)


