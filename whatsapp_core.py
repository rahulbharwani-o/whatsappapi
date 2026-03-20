import os
from playwright.sync_api import sync_playwright

def send_whatsapp_message(phone_number, message_text):
    """
    Executes the Playwright script to send a WA message via background Chromium process.
    """
    user_data_dir = os.path.join(os.getcwd(), 'whatsapp_session')

    print(f"[BACKGROUND ENGINE] Initializing Playwright browser...")
    try:
        with sync_playwright() as p:
            # Launch Chromium entirely in the background
            browser = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=True,
                args=['--no-sandbox', '--headless=new'],
                # Spoofed user-agent prevents WA Web from detecting headless mode
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()

            url = f"https://web.whatsapp.com/send/?phone={phone_number}"
            page.goto(url)

            print(f"[BACKGROUND ENGINE] Loading chat {phone_number}...")
            # `#main` guarantees the chat is ready
            page.wait_for_selector('#main', timeout=60000)
            
            # Find the input box inside `#main`
            input_box = '#main footer div[contenteditable="true"]'
            page.wait_for_selector(input_box, timeout=20000)
            
            print(f"[BACKGROUND ENGINE] Typing out payload...")
            page.fill(input_box, message_text)
            page.wait_for_timeout(1000)
            
            print(f"[BACKGROUND ENGINE] Executing send command (ENTER Key)...")
            page.keyboard.press("Enter")
            
            print(f"✅ [SUCCESS] Delivered message entirely via background engine!")
            page.wait_for_timeout(3000)
            
            browser.close()
            
    except Exception as e:
        print(f"❌ [ERROR] Engine failed to run automation task.")
        print(f"Details: {e}")
