import sys
import os
from unittest.mock import patch, MagicMock

# Add root to sys.path
sys.path.append(os.getcwd())

@patch('zaknotes.refresh_cookies')
@patch('builtins.input')
def test_refresh_cookies_call(mock_input, mock_refresh):
    # Choice 3, then Choice 4 (Exit)
    mock_input.side_effect = ['3', '4']
    
    import zaknotes
    try:
        zaknotes.main_menu()
    except SystemExit:
        pass
            
    # Verify cookie refresh call
    mock_refresh.assert_called_once()
