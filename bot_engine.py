from browser_driver import BrowserDriver
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import time
import os
import glob

# --- CONFIGURATION ---
TARGET_MODEL_NAME = "Gemini 3 Pro Preview"
TARGET_MODEL_ID = "model-carousel-row-models/gemini-3-pro-preview"
TARGET_SYSTEM_INSTRUCTION = "note generator"

TEMP_DIR = "temp" 
DOWNLOAD_DIR = "downloads"
ENABLE_STABILITY_CHECK = True 

os.makedirs(TEMP_DIR, exist_ok=True)

class AIStudioBot:
    def __init__(self):
        self.driver = BrowserDriver()
        self.page = None

    def ensure_connection(self):
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
        
        # Always navigate to new chat to ensure fresh state
        if self.page.url != "https://aistudio.google.com/prompts/new_chat":
             self.page.goto("https://aistudio.google.com/prompts/new_chat")
        
        try: self.page.wait_for_load_state("networkidle", timeout=10000)
        except: pass

    def select_model(self):
        print(f"🤖 Bot: Checking Model ({TARGET_MODEL_NAME})...")
        try:
            # Selector for the card in the sidebar that shows current model
            # From: ui_elements/models_list_right_sidebar_opening_button(if gemini-3-pro-preview is selected).html
            # It has class "model-selector-card"
            card_selector = "button.model-selector-card"
            
            card = self.page.wait_for_selector(card_selector, timeout=10000)
            current_text = card.text_content().strip()
            
            if TARGET_MODEL_NAME in current_text:
                print(f"   ✅ Verified: Already on {TARGET_MODEL_NAME}.")
                return

            print(f"   Mismatch. Switching from '{current_text}'...")
            card.click()
            
            # Selector for the model option in the list
            # From inferred ID based on gemini-2.5-pro example
            target_btn_selector = f'button[id="{TARGET_MODEL_ID}"]'
            
            # Wait for the list to appear and the button to be available
            # We might need to handle the "All" tab if it's not visible, but let's try direct first.
            try:
                target_btn = self.page.wait_for_selector(target_btn_selector, timeout=5000)
                target_btn.click()
            except PlaywrightTimeoutError:
                print("   Target model not immediately visible, trying to switch to 'All' tab...")
                # Try clicking "All" tab if available
                all_btn = self.page.locator("button[data-test-category-button='']").filter(has_text="All")
                if all_btn.is_visible():
                    all_btn.click()
                
                # Try finding target again
                target_btn = self.page.wait_for_selector(target_btn_selector, timeout=5000)
                target_btn.click()

            print(f"   ✅ Switched to {TARGET_MODEL_NAME}")
            
        except Exception as e:
            print(f"   ❌ Model selection error: {e}")
            raise

    def select_system_instruction(self):
        instruction_name = TARGET_SYSTEM_INSTRUCTION
        print(f"🤖 Bot: Checking System Instruction ({instruction_name})...")
        try:
            # Selector for the system instructions card in sidebar
            # From: ui_elements/system_instructions_right_sidebar_opening_button...
            card_selector = "button.system-instructions-card"
            
            # We assume the card might not show the full instruction name if it's long, 
            # but usually it shows the selected one. 
            # However, simpler to just open it and check the dropdown.
            
            card = self.page.wait_for_selector(card_selector, timeout=10000)
            card.click()
            
            # Wait for dropdown to be visible
            # From: ui_elements/system_instructions_selector_dropdown_in_the_sidebar...
            dropdown_selector = ".mat-mdc-select-trigger"
            dropdown = self.page.wait_for_selector(dropdown_selector, timeout=5000)
            
            current_val = dropdown.text_content().strip()
            if instruction_name in current_val:
                 print(f"   ✅ Already using '{instruction_name}'.")
                 return
            
            print("   Setting instruction...")
            dropdown.click()
            
            # Selector for the option
            # From: ui_elements/note_generator_instruction_selection_button...
            # It's a mat-option.
            option = self.page.locator("mat-option").filter(has_text=instruction_name).first
            option.wait_for(state="visible", timeout=5000)
            option.click()
            
            print(f"   ✅ Selected: {instruction_name}")
            
        except Exception as e:
            print(f"   ❌ System Instruction selection error: {e}")
            raise

    # Placeholder for Phase 3
    def generate_notes(self, audio_path):
        pass

    def close(self):
        self.driver.close()

if __name__ == "__main__":
    bot = AIStudioBot()
    try:
        bot.ensure_connection()
        bot.select_model()
        bot.select_system_instruction()
        print("\n--- Bot Ready ---")
            
    except Exception as e:
        print(f"CRASH: {e}")
