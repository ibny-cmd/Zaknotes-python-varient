from browser_driver import BrowserDriver

def test_auto_flow():
    driver = BrowserDriver()
    
    try:
        # 1. This will auto-launch Brave if needed
        page = driver.get_ai_studio_page()
        
        if not page:
            print("❌ Failed to get page.")
            return

        print(f"✅ Controlling Page: {page.title()}")
        
        # 2. Perform the typing test again to be sure
        print("👀 Looking for input box...")
        
        try:
            # Quick check for input
            textbox = page.get_by_role("textbox")
            # Wait up to 5s
            textbox.first.wait_for(state="visible", timeout=5000)
            
            textbox.first.fill("Auto-Launch Test Successful!")
            print("🎉 SUCCESS! Browser launched and text typed automatically.")
            
        except Exception as e:
            print(f"⚠️  Could not type: {e}")

    except Exception as e:
        print(f"❌ Critical Error: {e}")
    
    finally:
        print("👋 Disconnecting driver...")
        driver.close()

if __name__ == "__main__":
    test_auto_flow()