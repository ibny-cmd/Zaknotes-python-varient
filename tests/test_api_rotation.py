import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api_key_manager import APIKeyManager

def test_round_robin_rotation(tmp_path):
    """Verify that get_available_key rotates through available keys."""
    keys_file = tmp_path / "api_keys.json"
    with open(keys_file, 'w') as f:
        json.dump({
            "keys": [
                {"key": "key-1", "usage": {"gemini-2.5-flash": 0}, "exhausted": {"gemini-2.5-flash": False}},
                {"key": "key-2", "usage": {"gemini-2.5-flash": 0}, "exhausted": {"gemini-2.5-flash": False}},
                {"key": "key-3", "usage": {"gemini-2.5-flash": 0}, "exhausted": {"gemini-2.5-flash": False}}
            ],
            "last_reset_date": "2026-02-09"
        }, f)
    
    # Mock _get_current_time_pt to avoid network calls
    with patch.object(APIKeyManager, '_get_current_time_pt', return_value=MagicMock(strftime=lambda x: "2026-02-09")):
        manager = APIKeyManager(keys_file=str(keys_file))
        
        # Consecutive calls should rotate
        assert manager.get_available_key("gemini-2.5-flash") == "key-1"
        assert manager.get_available_key("gemini-2.5-flash") == "key-2"
        assert manager.get_available_key("gemini-2.5-flash") == "key-3"
        assert manager.get_available_key("gemini-2.5-flash") == "key-1"

def test_rotation_skips_exhausted(tmp_path):
    """Verify that rotation skips exhausted or over-quota keys."""
    keys_file = tmp_path / "api_keys.json"
    with open(keys_file, 'w') as f:
        json.dump({
            "keys": [
                {"key": "key-1", "usage": {"gemini-2.5-flash": 0}, "exhausted": {"gemini-2.5-flash": False}},
                {"key": "key-2", "usage": {"gemini-2.5-flash": 20}, "exhausted": {"gemini-2.5-flash": False}}, # Over quota
                {"key": "key-3", "usage": {"gemini-2.5-flash": 0}, "exhausted": {"gemini-2.5-flash": True}},  # Exhausted
                {"key": "key-4", "usage": {"gemini-2.5-flash": 0}, "exhausted": {"gemini-2.5-flash": False}}
            ],
            "last_reset_date": "2026-02-09"
        }, f)
    
    with patch.object(APIKeyManager, '_get_current_time_pt', return_value=MagicMock(strftime=lambda x: "2026-02-09")):
        manager = APIKeyManager(keys_file=str(keys_file))
        
        assert manager.get_available_key("gemini-2.5-flash") == "key-1"
        assert manager.get_available_key("gemini-2.5-flash") == "key-4"
        assert manager.get_available_key("gemini-2.5-flash") == "key-1"
