import os
import json
import sys
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config_manager import ConfigManager
from src.rclone_config_manager import RcloneConfigManager

TEST_CONFIG_FILE = "test_config_rclone.json"
TEST_RCLONE_KEYS_FILE = "test_rclone_keys.json"

@pytest.fixture
def config_manager():
    if os.path.exists(TEST_CONFIG_FILE):
        os.remove(TEST_CONFIG_FILE)
    manager = ConfigManager(config_file=TEST_CONFIG_FILE)
    yield manager
    if os.path.exists(TEST_CONFIG_FILE):
        os.remove(TEST_CONFIG_FILE)

@pytest.fixture
def rclone_config_manager():
    if os.path.exists(TEST_RCLONE_KEYS_FILE):
        os.remove(TEST_RCLONE_KEYS_FILE)
    
    manager = RcloneConfigManager(keys_file=TEST_RCLONE_KEYS_FILE)
    yield manager
    if os.path.exists(TEST_RCLONE_KEYS_FILE):
        os.remove(TEST_RCLONE_KEYS_FILE)

def test_rclone_integration_default_false(config_manager):
    """Test that rclone_integration_enabled defaults to False."""
    assert config_manager.get("rclone_integration_enabled") is False

def test_rclone_config_manager_exists():
    """Verify that RcloneConfigManager can be imported."""
    assert RcloneConfigManager is not None

def test_rclone_config_defaults(rclone_config_manager):
    """Test default values for rclone credentials."""
    remote_name, remote_path = rclone_config_manager.get_credentials()
    assert remote_name == ""
    assert remote_path == ""

def test_rclone_config_load_save(rclone_config_manager):
    """Test saving and loading rclone credentials."""
    rclone_config_manager.set_credentials("my_remote", "my/path")
    
    # Reload with a new instance
    new_manager = RcloneConfigManager(keys_file=TEST_RCLONE_KEYS_FILE)
    remote_name, remote_path = new_manager.get_credentials()
    assert remote_name == "my_remote"
    assert remote_path == "my/path"
