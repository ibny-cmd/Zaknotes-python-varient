import os
import json
import sys
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config_manager import ConfigManager

TEST_CONFIG_FILE = "test_ua_config.json"

@pytest.fixture
def config_manager():
    if os.path.exists(TEST_CONFIG_FILE):
        os.remove(TEST_CONFIG_FILE)
    manager = ConfigManager(config_file=TEST_CONFIG_FILE)
    yield manager
    if os.path.exists(TEST_CONFIG_FILE):
        os.remove(TEST_CONFIG_FILE)

def test_user_agent_default(config_manager):
    """Test that a default user-agent is provided."""
    ua = config_manager.get("user_agent")
    assert ua is not None
    assert "Mozilla/5.0" in ua

def test_user_agent_persistence(config_manager):
    """Test that a custom user-agent can be saved and reloaded."""
    custom_ua = "My Custom UA 1.0"
    config_manager.set("user_agent", custom_ua)
    config_manager.save()
    
    new_manager = ConfigManager(config_file=TEST_CONFIG_FILE)
    assert new_manager.get("user_agent") == custom_ua
