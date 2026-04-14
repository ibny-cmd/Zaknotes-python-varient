import os
import sys
from src.config_manager import ConfigManager
from src.rclone_config_manager import RcloneConfigManager

def verify_phase_1():
    print("Verifying Phase 1: Configuration Management...")
    
    # 1. Verify ConfigManager default
    cm = ConfigManager(config_file="temp_config.json")
    enabled = cm.get("rclone_integration_enabled")
    print(f"Rclone integration enabled (default): {enabled}")
    if enabled is not False:
        print("FAILED: rclone_integration_enabled should default to False")
        return False
    
    # 2. Verify RcloneConfigManager
    rcm = RcloneConfigManager(keys_file="temp_rclone_keys.json")
    remote, path = rcm.get_credentials()
    print(f"Default credentials: remote='{remote}', path='{path}'")
    
    rcm.set_credentials("test_remote", "test/path")
    print("Setting credentials to: remote='test_remote', path='test/path'")
    
    # Reload to verify persistence
    rcm2 = RcloneConfigManager(keys_file="temp_rclone_keys.json")
    remote2, path2 = rcm2.get_credentials()
    print(f"Reloaded credentials: remote='{remote2}', path='{path2}'")
    
    if remote2 == "test_remote" and path2 == "test/path":
        print("PASSED: Phase 1 verification successful")
        return True
    else:
        print("FAILED: Credentials did not persist correctly")
        return False

if __name__ == "__main__":
    success = verify_phase_1()
    
    # Cleanup
    if os.path.exists("temp_config.json"):
        os.remove("temp_config.json")
    if os.path.exists("temp_rclone_keys.json"):
        os.remove("temp_rclone_keys.json")
        
    if not success:
        sys.exit(1)
