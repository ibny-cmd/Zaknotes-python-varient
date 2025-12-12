import os
import subprocess
import shlex
import sys  # <--- ADDED THIS

# CONFIGURATION
DOWNLOAD_DIR = "downloads"
COOKIES_DIR = "cookies"
DEFAULT_COOKIE = os.path.join(COOKIES_DIR, "bangi.txt") 

# SMART FORMAT STRATEGY
SMART_FORMAT = "best[height=240]/best[height=360]/best[height=480]/best[height=540]/bestaudio/best"

# Ensure directories exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(COOKIES_DIR, exist_ok=True)

def get_cookie_path(client_id="default"):
    specific = os.path.join(COOKIES_DIR, f"{client_id}.txt")
    if os.path.exists(specific):
        return specific
    if os.path.exists(DEFAULT_COOKIE):
        return DEFAULT_COOKIE
    return None

def run_command(cmd_str):
    """Runs a shell command and raises error if it fails"""
    print(f"Executing: {cmd_str}")
    process = subprocess.run(shlex.split(cmd_str), capture_output=True, text=True)
    if process.returncode != 0:
        print(f"❌ Error: {process.stderr}")
        raise Exception(process.stderr)
    return process.stdout.strip()

def download_audio(job):
    url = job['url']
    name = job['name']
    
    # Clean filename
    safe_name = name.replace(" ", "_").replace("/", "-")
    output_template = f"{DOWNLOAD_DIR}/{safe_name}.%(ext)s"
    
    # Cookie setup
    cookie_file = get_cookie_path()
    cookie_arg = f'--cookies "{cookie_file}"' if cookie_file else ""

    print(f"\n⬇️  Starting Download: {name}")

    # --- RULE 1: FACEBOOK ---
    if "facebook.com" in url or "fb.watch" in url:
        print(">> Mode: Facebook")
        cmd = (
            f'yt-dlp --downloader aria2c --no-part --no-keep-fragments '
            f'{cookie_arg} '
            f'-f "{SMART_FORMAT}" '
            f'-x --audio-format mp3 '
            f'-o "{output_template}" "{url}"'
        )
        run_command(cmd)

    # --- RULE 2: APAR'S CLASSROOM ---
    elif "aparsclassroom" in url:
        print(">> Mode: Apar's Classroom")
        cmd = (
            f'yt-dlp --downloader aria2c --no-part --no-keep-fragments '
            f'{cookie_arg} --no-playlist '
            f'-f "{SMART_FORMAT}" '
            f'-x --audio-format mp3 '
            f'-o "{output_template}" "{url}"'
        )
        run_command(cmd)

    # --- RULE 3: EDGECOURSEBD ---
    elif "edgecoursebd" in url:
        print(">> Mode: EdgeCourseBD (Running Scraper...)")
        
        # --- FIX IS HERE ---
        # We use sys.executable to ensure we use the VENV python, not system python
        scraper_cmd = f'"{sys.executable}" find_vimeo_url.py --url "{url}"'
        
        if cookie_file:
            scraper_cmd += f' --cookies "{cookie_file}"'
            
        try:
            vimeo_url = run_command(scraper_cmd)
            print(f"   Found Vimeo URL: {vimeo_url}")
            
            # 2. Download using Vimeo URL
            cmd = (
                f'yt-dlp --downloader aria2c --no-part --no-keep-fragments '
                f'--referer "{url}" '
                f'{cookie_arg} '
                f'-f "{SMART_FORMAT}" '
                f'-x --audio-format mp3 '
                f'-o "{output_template}" "{vimeo_url}"'
            )
            run_command(cmd)
        except Exception as e:
            print(f"❌ Scraper failed: {e}")
            raise e

    # --- RULE 4: DEFAULT / FALLBACK ---
    else:
        print(">> Mode: Default/Generic")
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        cmd = (
            f'yt-dlp -f "{SMART_FORMAT}" '
            f'--extract-audio --audio-format mp3 --audio-quality 5 '
            f'--continue {cookie_arg} '
            f'-o "{output_template}" '
            f'--add-header "Referer: https://www.youtube.com/" '
            f'--add-header "User-Agent: {ua}" '
            f'"{url}"'
        )
        run_command(cmd)
    
    final_output = f"{DOWNLOAD_DIR}/{safe_name}.mp3"
    print(f"✅ Download Complete: {final_output}")
    return final_output