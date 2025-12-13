from playwright.sync_api import sync_playwright
import time

def test_connection():
    print("🔌 Connecting to Chrome on localhost:9222...")
    
    try:
        with sync_playwright() as p:
            # Connect to the EXISTING browser (The Trojan Horse method)
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            
            # Get the first context (your profile)
            context = browser.contexts[0]
            
            # Find the AI Studio tab
            page = None
            for p_page in context.pages:
                if "aistudio.google" in p_page.url:
                    page = p_page
                    break
            
            if not page:
                print("⚠️ AI Studio tab not found. Opening a new one...")
                page = context.new_page()
                page.goto("https://aistudio.google.com/")
                page.wait_for_load_state("networkidle")

            print(f"✅ Connected to: {page.title()}")
            
            # --- THE ACID TEST ---
            print("👀 Looking for the Input Box...")
            
            # AI Studio selectors change, but usually they are contenteditable divs
            # We try a few common strategies
            
            # Strategy 1: The main prompt text area
            input_selector = "textarea" 
            
            try:
                # Wait a moment for dynamic JS to load
                page.wait_for_timeout(2000)
                
                # Check if we are logged in
                if "Sign in" in page.title() or page.get_by_text("Sign in").is_visible():
                    print("❌ You are NOT logged in.")
                    print("👉 Please log in to Google manually in the browser window, then re-run this test.")
                    return

                # Try to type
                # Usually AI Studio has a specific text area.
                # We click the 'Create new' button if we are on the home page dashboard
                if "Prompts" in page.title():
                    print("   (On Dashboard, clicking 'Create New')")
                    # This selector might need adjustment based on their current UI
                    page.get_by_role("button", name="Create new").click()
                    page.wait_for_timeout(2000)

                print("   Typing 'Hello World' into the prompt box...")
                
                # Try locating by role (most robust)
                textbox = page.get_by_role("textbox")
                
                if textbox.count() > 0:
                    textbox.first.fill("Hello World - Automation Test")
                    print("✅ SUCCESS! Textbox found and typed into.")
                else:
                    # Fallback for complex shadow DOMs
                    print("⚠️ Standard textbox role not found. Trying generic textarea...")
                    page.fill("textarea", "Hello World - Fallback Test")
                    print("✅ SUCCESS! Textarea found and typed into.")

            except Exception as e:
                print(f"❌ FAILED to find/type in input box. Google might be blocking it.\nError: {e}")

            print("\nDisconnecting... (Browser stays open)")
            browser.close()

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("Did you run 'browser_launcher.py' first?")

if __name__ == "__main__":
    test_connection()