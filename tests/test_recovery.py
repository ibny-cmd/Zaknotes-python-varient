import pytest
from unittest.mock import MagicMock, patch, call
from src.bot_engine import AIStudioBot, process_job
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

@pytest.fixture
def mock_bot_with_driver():
    with patch('src.bot_engine.BrowserDriver') as mock_driver_class, \
         patch('src.bot_engine.PdfConverter'):
        
        mock_driver = mock_driver_class.return_value
        bot = AIStudioBot()
        bot.page = MagicMock()
        return bot, mock_driver

def test_process_job_restarts_browser_on_interaction_failure(mock_bot_with_driver):
    bot, mock_driver = mock_bot_with_driver
    
    # Mock job
    job = {"name": "Test Job", "url": "http://test.com", "status": "queue"}
    mock_manager = MagicMock()
    
    # Simulate select_model failing on first attempt, succeeding on second
    # We use a side_effect on the bot instance itself
    with patch.object(bot, 'select_model') as mock_select_model, \
         patch.object(bot, 'ensure_connection'), \
         patch.object(bot, 'select_system_instruction'), \
         patch.object(bot, 'generate_notes', return_value=("text", "path.pdf")), \
         patch.object(bot, 'restart_session') as mock_restart, \
         patch('src.bot_engine.download_audio', return_value="test.mp3"), \
         patch('time.sleep'):
        
        mock_select_model.side_effect = [Exception("First Fail"), None]
        
        process_job(bot, mock_manager, job)
        
        # Verify restart_session was called once
        mock_restart.assert_called_once()
        # Verify select_model was called twice
        assert mock_select_model.call_count == 2
        # Verify job is completed
        assert job['status'] == 'completed'

def test_process_job_fails_after_max_attempts(mock_bot_with_driver):
    bot, mock_driver = mock_bot_with_driver
    job = {"name": "Test Job", "url": "http://test.com", "status": "queue"}
    mock_manager = MagicMock()
    
    with patch.object(bot, 'select_model', side_effect=Exception("Permanent Fail")), \
         patch.object(bot, 'ensure_connection'), \
         patch.object(bot, 'restart_session'), \
         patch('src.bot_engine.download_audio', return_value="test.mp3"), \
         patch('time.sleep'):
        
        process_job(bot, mock_manager, job)
        
        assert job['status'] == 'failed'
        assert "Permanent Fail" in job['error']
