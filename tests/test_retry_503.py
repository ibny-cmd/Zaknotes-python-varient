import os
import sys
import pytest
import time
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gemini_api_wrapper import GeminiAPIWrapper
from src.api_key_manager import APIKeyManager

@pytest.fixture
def api_setup():
    manager = MagicMock(spec=APIKeyManager)
    manager.get_available_key.return_value = "test-key"
    wrapper = GeminiAPIWrapper(key_manager=manager)
    return manager, wrapper

def test_retry_on_503(api_setup):
    """Test that it retries after a 10-minute wait on 503 error."""
    manager, wrapper = api_setup
    
    with patch("google.genai.Client") as mock_client_class, \
         patch("time.sleep") as mock_sleep:
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # First call fails with 503, second call succeeds
        error_503 = Exception("Model Overloaded")
        error_503.code = 503
        
        mock_client.models.generate_content.side_effect = [
            error_503,
            MagicMock(text="success response")
        ]
        
        result = wrapper.generate_content("prompt", model_type="note")
        
        assert result == "success response"
        assert mock_client.models.generate_content.call_count == 2
        mock_sleep.assert_called_once_with(600)
