import sys
import os
import shutil
from unittest.mock import patch, MagicMock

# Add root to sys.path
sys.path.append(os.getcwd())

@patch('shutil.rmtree')
@patch('src.browser_driver.BrowserDriver.launch_browser')
@patch('builtins.input')
def test_refresh_browser_profile_call(mock_input, mock_launch, mock_rmtree):
    # Choice 2, then Choice 4 (Exit)
    mock_input.side_effect = ['2', '4']
    
    # Ensure the directory "exists" for the test
    with patch('os.path.exists', return_value=True):
        import zaknotes
        try:
            zaknotes.main_menu()
        except SystemExit:
            pass
            
    # Verify directory deletion and browser launch
    mock_rmtree.assert_called_with('browser_profile')
    mock_launch.assert_called_once()
