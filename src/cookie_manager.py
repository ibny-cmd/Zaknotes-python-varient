import re
import os
import sys

# --- CONFIGURATION ---
COOKIES_DIR = "cookies"
TARGET_COOKIE_FILE = os.path.join(COOKIES_DIR, "bangi.txt")

class CookieMerger:
    def __init__(self, cookie_file_path):
        self.cookie_file_path = cookie_file_path
        # Ensure dir exists
        os.makedirs(os.path.dirname(self.cookie_file_path), exist_ok=True)
        
    def normalize_content(self, content):
        if not content: return ''
        normalized = content.replace(r'\n', '\n')
        normalized = normalized.replace(' # ', '\n# ')
        normalized = re.sub(r'(\S+)\t(TRUE|FALSE)\t\/', r'\n\1\t\2\t/', normalized)
        normalized = re.sub(r'#HttpOnly_(\S+)', r'\n#HttpOnly_\1', normalized)
        normalized = re.sub(r'#HttpOnly\.(\S+)', r'\n#HttpOnly.\1', normalized)
        normalized = re.sub(r'^\n+', '', normalized)
        return normalized

    def parse_cookie_content(self, content):
        if not content or not content.strip(): return []
        normalized = self.normalize_content(content)
        lines = normalized.split('\n')
        cookies = []

        for line in lines:
            line = line.strip()
            if (not line or line.startswith('Netscape') or line.startswith('http') or 
                line.startswith('This file') or (line.startswith('#') and not line.startswith('#HttpOnly'))):
                continue

            clean_line = line
            prefix = ''
            if line.startswith('#HttpOnly_'):
                prefix = '#HttpOnly_'
                clean_line = line[10:]
            elif line.startswith('#HttpOnly.'):
                prefix = '#HttpOnly.'
                clean_line = line[9:]

            parts = [p for p in clean_line.split('\t') if p]
            if len(parts) < 7:
                parts = [p for p in re.split(r'\s+', clean_line) if p]

            if len(parts) >= 7:
                cookies.append({
                    'prefix': prefix, 'domain': parts[0], 'flag': parts[1], 'path': parts[2],
                    'secure': parts[3], 'expiration': parts[4], 'name': parts[5],
                    'value': ' '.join(parts[6:])
                })
        return cookies

    def merge_cookies(self, new_content):
        print(f"📂 Target File: {self.cookie_file_path}")
        
        # Read Existing
        existing_content = ""
        if os.path.exists(self.cookie_file_path):
            try:
                with open(self.cookie_file_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            except: pass

        existing_cookies = self.parse_cookie_content(existing_content)
        new_cookies = self.parse_cookie_content(new_content)

        if not new_cookies:
            print("⚠️  No valid cookies detected in input. Nothing updated.")
            return

        # Merge
        cookie_map = {}
        for c in existing_cookies:
            cookie_map[f"{c['domain']}|{c['path']}|{c['name']}"] = c
        for c in new_cookies:
            cookie_map[f"{c['domain']}|{c['path']}|{c['name']}"] = c

        # Write
        header = "# Netscape HTTP Cookie File\n# http://curl.haxx.se/rfc/cookie_spec.html\n# This is a generated file!  Do not edit.\n"
        output_lines = [header]
        for c in cookie_map.values():
            line = f"{c['prefix']}{c['domain']}\t{c['flag']}\t{c['path']}\t{c['secure']}\t{c['expiration']}\t{c['name']}\t{c['value']}"
            output_lines.append(line)

        with open(self.cookie_file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(output_lines))
            
        print(f"✅ Success! Merged {len(new_cookies)} new cookies. Total now: {len(cookie_map)}")

def interactive_update():
    print("==========================================")
    print("   🍪 COOKIE UPDATER")
    print(f"   Target: {TARGET_COOKIE_FILE}")
    print("==========================================")
    print("1. Copy your cookies from the browser/extension.")
    print("2. PASTE them below.")
    print("3. Type 'DONE' on a new line and hit Enter when finished.")
    print("------------------------------------------")

    lines = []
    while True:
        try:
            line = input()
            # Stop condition
            if line.strip().upper() == "DONE":
                break
            lines.append(line)
        except EOFError:
            break
            
    raw_input = "\n".join(lines)
    
    if not raw_input.strip():
        print("❌ No input provided.")
        return

    merger = CookieMerger(TARGET_COOKIE_FILE)
    merger.merge_cookies(raw_input)

if __name__ == "__main__":
    interactive_update()