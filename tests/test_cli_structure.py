import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import zaknotes

class TestCLIStructure(unittest.TestCase):
    @patch('zaknotes.main_menu')
    def test_default_interactive_mode(self, mock_main_menu):
        """Test that running without args enters interactive mode."""
        with patch.object(sys, 'argv', ['zaknotes.py']):
            zaknotes.main()
            mock_main_menu.assert_called_once()

    @patch('zaknotes.main_menu')
    def test_local_flag_parsing_empty(self, mock_main_menu):
        """Test that --local flag is parsed correctly with no names."""
        with patch.object(sys, 'argv', ['zaknotes.py', '--local']):
            # For now, it just prints DEBUG
            zaknotes.main()
            mock_main_menu.assert_not_called()

    @patch('zaknotes.main_menu')
    def test_local_flag_parsing_with_names(self, mock_main_menu):
        """Test that --local flag is parsed correctly with names."""
        with patch.object(sys, 'argv', ['zaknotes.py', '--local', 'Bio', 'Hist']):
            zaknotes.main()
            mock_main_menu.assert_not_called()

    @patch('builtins.input', side_effect=['10']) # Exit choice
    @patch('builtins.print')
    def test_main_menu_has_rclone_option(self, mock_print, mock_input):
        """Test that main_menu prints the Rclone integration option."""
        zaknotes.main_menu()
        
        # Check if "Manage Rclone Settings" was printed
        any_rclone_print = any("Manage Rclone Settings" in str(call) for call in mock_print.call_args_list)
        assert any_rclone_print is True

    @patch('zaknotes.manage_rclone_settings')
    @patch('builtins.input', side_effect=['4', '10']) # Select Rclone then Exit
    def test_main_menu_calls_rclone_settings(self, mock_input, mock_manage_rclone):
        """Test that main_menu calls manage_rclone_settings when option 4 is selected."""
        zaknotes.main_menu()
        mock_manage_rclone.assert_called_once()

if __name__ == '__main__':
    unittest.main()
