from browser_driver import BrowserDriver
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import time
import os
import glob

# --- CONFIGURATION ---
TARGET_MODEL_NAME = "Gemini 3 Pro Preview"
TARGET_MODEL_ID = "model-carousel-row-models/gemini-3-pro-preview"
TARGET_SYSTEM_PROMPT = "note generator"

TEMP_DIR = "temp" 
DOWNLOAD_DIR = "downloads"
ENABLE_STABILITY_CHECK = True 

os.makedirs(TEMP_DIR, exist_ok=True)

class AIStudioBot:
    def __init__(self):
        self.driver = BrowserDriver()
        self.page = None

    def start_session(self):
        print("🤖 Bot: Connecting to session...")
        if not self.driver.connect(): 
            raise Exception("Could not connect to browser.")
        
        context = self.driver.context
        context.grant_permissions(["clipboard-read", "clipboard-write"])
        
        found = False
        for p in context.pages:
            if "aistudio" in p.url:
                self.page = p
                found = True
                p.bring_to_front()
                break
        
        if not found:
            print("   Opening new AI Studio tab...")
            self.page = context.new_page()
            self.page.goto("https://aistudio.google.com/prompts/new_chat")
        
        try: self.page.wait_for_load_state("networkidle", timeout=10000)
        except: pass

    def select_model(self):
        print(f"🤖 Bot: Checking Model ({TARGET_MODEL_NAME})...")
        try:
            for attempt in range(3):
                card = self.page.locator(".model-selector-card").first
                try: card.wait_for(state="visible", timeout=8000)
                except: pass
                
                if not card.is_visible():
                    self.page.locator("button[data-test-id='model-selector']").click()
                
                current_text = card.text_content().strip()
                if TARGET_MODEL_NAME in current_text:
                    print(f"   ✅ Verified: Already on {TARGET_MODEL_NAME}.")
                    return

                print(f"   Mismatch (Attempt {attempt+1}). Switching...")
                
                class_attr = card.get_attribute("class") or ""
                if "expanded" not in class_attr: 
                    card.click()
                    time.sleep(1)

                try:
                    all_btn = self.page.locator("button[data-test-category-button='']").filter(has_text="All")
                    all_btn.wait_for(state="visible", timeout=5000)
                    all_btn.click(force=True)
                    time.sleep(1)
                except: pass

                target_btn = self.page.locator(f'button[id="{TARGET_MODEL_ID}"]').first
                
                if not target_btn.is_visible():
                    print("   Scrolling for target...")
                    list_container = self.page.locator("mat-dialog-content").first 
                    if not list_container.is_visible():
                         list_container = self.page.locator(".mat-mdc-dialog-content").first
                    for _ in range(5):
                        if target_btn.is_visible(): break
                        list_container.press("PageDown")
                        time.sleep(0.5)

                if target_btn.is_visible():
                    target_btn.evaluate("e => e.click()")
                    time.sleep(1)
                else:
                    print(f"   ❌ Could not find model ID '{TARGET_MODEL_ID}'")

                try: self.page.get_by_label("Close panel").click(timeout=2000)
                except: pass
                time.sleep(1)
            
            print("❌ Failed to switch model after 3 attempts.")
        except Exception as e:
            print(f"   ❌ Model selection error: {e}")

    def set_system_prompt(self):
        prompt_name = TARGET_SYSTEM_PROMPT
        print(f"🤖 Bot: Checking System Prompt ({prompt_name})...")
        try:
            # 1. SMART CHECK ON CARD
            card = self.page.locator("button[data-test-system-instructions-card]").first
            card.wait_for(state="visible", timeout=5000)
            card_text = card.text_content()

            if prompt_name in card_text:
                print(f"   ✅ Already using '{prompt_name}'. Skipping.")
                return

            print("   Setting prompt...")
            card.click()
            self.page.wait_for_timeout(1500) 
            
            # 2. FIND DROPDOWN TRIGGER (JS Click)
            print("   Clicking Dropdown Trigger...")
            triggers = self.page.locator(".mat-mdc-select-trigger")
            count = triggers.count()
            
            clicked = False
            for i in range(count):
                el = triggers.nth(i)
                if el.is_visible():
                    el.evaluate("e => e.click()")
                    clicked = True
                    try:
                        self.page.wait_for_selector("mat-option", timeout=1000)
                        break 
                    except: pass
            
            if not clicked:
                # Fallback
                self.page.get_by_text("Create new instruction", exact=False).click(force=True)

            self.page.wait_for_timeout(1000)
            
            # 3. SELECT OPTION
            option = self.page.locator("mat-option").filter(has_text=prompt_name).first
            try:
                option.wait_for(state="visible", timeout=5000)
                option.click(force=True)
                print(f"   ✅ Selected: {prompt_name}")
            except:
                print(f"   ❌ Prompt '{prompt_name}' not found.")
            
            time.sleep(1)
            try: self.page.get_by_label("Close panel").click(force=True)
            except: pass
            
        except Exception as e:
            print(f"   ❌ System Prompt failed: {e}")

    def generate_notes(self, audio_path):
        if not os.path.exists(audio_path):
            print(f"❌ File not found: {audio_path}")
            return None, None

        filename = os.path.basename(audio_path)
        name_no_ext = os.path.splitext(filename)[0]
        output_filename = f"{name_no_ext}.md"
        output_path = os.path.join(TEMP_DIR, output_filename)

        print(f"🤖 Bot: Uploading {filename}...")
        
        try:
            # 1. Open Menu
            print("   Clicking '+' to load menu...")
            self.page.locator("button[data-test-add-chunk-menu-button]").click()
            self.page.wait_for_timeout(2000) 

            # 2. TARGET HIDDEN INPUT
            print("   Targeting hidden input...")
            try:
                file_input = self.page.locator("input[data-test-upload-file-input]")
                file_input.set_input_files(audio_path, timeout=60000)
                print("   ✅ File injected successfully.")
                
                # --- REMOVED ESCAPE KEY PRESS HERE ---
                # We just wait. The menu should act naturally or ignore.
                
            except Exception as e:
                print(f"   ❌ Input Injection Failed: {e}")
                return None, None

            # 3. WAIT FOR RUN
            print("   Waiting for 'Run'...")
            run_btn = self.page.locator("button.run-button:not([aria-label*='Close'])").first
            
            for i in range(300):
                if run_btn.is_enabled():
                    print("   🚀 Run Clicked!")
                    run_btn.click()
                    break
                time.sleep(1)
            else:
                print("   ❌ Timeout: Run button never enabled.")
                run_btn.click(force=True)

            print("⏳ Waiting for generation...")
            for _ in range(30):
                if self.page.get_by_label("Stop generation").count() > 0: break
                time.sleep(1)
            
            # Heartbeat loop
            start_time = time.time()
            while self.page.get_by_label("Stop generation").count() > 0:
                elapsed = int(time.time() - start_time)
                if elapsed % 10 == 0:
                    print(f"   ... Generating ({elapsed}s) ...")
                time.sleep(2)
            
            print("   ✅ Generation finished.")
            
            print("   Locating response container...")
            last_model_turn = self.page.locator("ms-chat-turn").filter(
                has=self.page.locator("[data-turn-role='Model']")
            ).last
            last_model_turn.wait_for(state="visible", timeout=300000)

            if ENABLE_STABILITY_CHECK:
                print("   Verifying text stability...")
                prev_len = 0
                stable_count = 0
                for _ in range(120): 
                    try: last_model_turn.scroll_into_view_if_needed()
                    except: pass
                    
                    curr_text = last_model_turn.inner_text()
                    curr_len = len(curr_text)
                    
                    if curr_len == prev_len and curr_len > 10:
                        stable_count += 1
                    else:
                        stable_count = 0
                    
                    if stable_count >= 5: 
                        print("   ✅ Text stabilized.")
                        break
                    
                    prev_len = curr_len
                    time.sleep(0.5)

            print("   Extracting text via Copy Menu...")
            try:
                # Hover to reveal buttons
                last_model_turn.hover()
                time.sleep(0.5)
                
                # Locate and Click 3-Dots
                more_btn = last_model_turn.locator("button[aria-label='Open options']").first
                more_btn.click(force=True)
                
                # Click Copy
                self.page.get_by_text("Copy as markdown").click(force=True)
                
                time.sleep(1)
                final_text = self.page.evaluate("navigator.clipboard.readText()")
                
                if not final_text: raise Exception("Clipboard empty")
                print("   ✅ Copied via Menu.")

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(final_text)
                print(f"   💾 Saved to: {output_path}")
                return final_text, output_path

            except Exception as e:
                print(f"   ❌ Menu interaction failed: {e}")
                return None, None

        except Exception as e:
            print(f"❌ Notes generation failed: {e}")
            return None, None

    def close(self):
        self.driver.close()

if __name__ == "__main__":
    bot = AIStudioBot()
    try:
        bot.start_session()
        bot.select_model()
        bot.set_system_prompt()
        
        real_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.mp3"))
        if real_files:
            text, path = bot.generate_notes(real_files[0])
            if path:
                 print(f"\n--- SUCCESS ---")
        else:
            print(f"❌ No mp3 files in {DOWNLOAD_DIR}")
            
    except Exception as e:
        print(f"CRASH: {e}")