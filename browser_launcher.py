import subprocess
import os
import sys
import time

# --- CONFIGURATION FOR BRAVE ---
# Common Linux Brave Paths
BROWSER_PATHS = [
    "/usr/bin/brave-browser",
    "/usr/bin/brave-browser-stable",
    "/usr/bin/brave",
    "/snap/bin/brave",
    "/opt/brave.com/brave/brave-browser"
]

# Brave Profile Path on Linux
USER_DATA_DIR = os.path.expanduser("~/.config/BraveSoftware/Brave-Browser") 

def launch_browser():
    # 1. Find Brave
    browser_exe = None
    for path in BROWSER_PATHS:
        if os.path.exists(path):
            browser_exe = path
            break
    
    if not browser_exe:
        print("❌ Could not find Brave Browser installation.")
        print("checked paths:", BROWSER_PATHS)
        return False

    print(f"🚀 Launching Brave from: {browser_exe}")
    print(f"📂 Profile Path: {USER_DATA_DIR}")
    print("⚠️  IMPORTANT: If Brave is already open, CLOSE IT COMPLETELY first!")
    
    # 2. Construct Command
    # --remote-debugging-port=9222: The key to controlling it
    cmd = [
        browser_exe,
        "--remote-debugging-port=9222",
        f"--user-data-dir={USER_DATA_DIR}",
        "https://aistudio.google.com/"
    ]

    # 3. Launch
    try:
        # Popen launches it in the background so Python can continue
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Brave launched! Waiting 5 seconds for it to load...")
        time.sleep(5)
        return True
    except Exception as e:
        print(f"❌ Error launching Brave: {e}")
        return False

if __name__ == "__main__":
    launch_browser()