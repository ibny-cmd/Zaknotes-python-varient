import sys
import os
from unittest.mock import patch, MagicMock

# Add root to sys.path
sys.path.append(os.getcwd())

@patch('src.bot_engine.AIStudioBot')
@patch('src.bot_engine.process_job')
@patch('builtins.input')
def test_start_note_generation_call(mock_input, mock_process_job, mock_bot):
    # Mocking the menu choice and then Name/URL inputs
    mock_input.side_effect = ['1', 'test_name', 'test_url', '4'] 
    
    # We also need to mock JobManager to return a pending job
    with patch('src.job_manager.JobManager.get_pending_from_last_150') as mock_get_pending:
        mock_get_pending.return_value = [{'name': 'test_name', 'url': 'test_url', 'status': 'queue'}]
        
        import zaknotes
        try:
            zaknotes.main_menu()
        except SystemExit:
            pass
            
    # Verify that AIStudioBot was instantiated and process_job was called
    mock_bot.assert_called_once()
    mock_process_job.assert_called_once()
