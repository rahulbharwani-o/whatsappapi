import os
import time
from playwright.sync_api import sync_playwright

def setup_whatsapp():
    """
    Run this script ONCE on your server to log into WhatsApp Web.
    """
    user_data_dir = os.path.join(os.getcwd(), 'whatsapp_session')
    
    print("Launching UI Browser for initial WhatsApp Login...")
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,  # This requires a graphical environment for the first scan!
            args=['--no-sandbox']
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto('https://web.whatsapp.com/')
        
        print("\n==============================================")
        print("📲 STEP 1: Open WhatsApp on your Phone")
        print("📲 STEP 2: Go to Linked Devices")
        print("📲 STEP 3: Scan the QR code in the browser window")
        print("==============================================\n")
        
        try:
            page.wait_for_selector('#pane-side', timeout=120000)
            print("✅ SUCCESS! You are logged in. The session is securely cached.")
            time.sleep(2)
        except Exception as e:
            print("❌ TIMEOUT. You didn't scan the QR code in time. Run python3 setup.py again.")
            
        browser.close()
        print("Setup completed. You can now start the production API using 'python3 api.py'.")

if __name__ == "__main__":
    setup_whatsapp()
