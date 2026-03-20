from flask import Flask, request, jsonify
import threading
import os
import shutil
import base64
from playwright.sync_api import sync_playwright
from whatsapp_core import send_whatsapp_message

app = Flask(__name__)
wa_state = {"status": "idle", "qr_code": None}

def headless_qr_scanner():
    global wa_state
    print("[SCANNER] Clearing old session to generate a fresh QR...")
    session_dir = os.path.join(os.getcwd(), 'whatsapp_session')
    shutil.rmtree(session_dir, ignore_errors=True)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=session_dir,
                headless=True,
                args=['--no-sandbox', '--headless=new'],
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto('https://web.whatsapp.com/')
            
            try:
                # Wait for the QR code canvas to render natively (up to 30s)
                canvas = page.wait_for_selector('canvas', timeout=30000)
                # Ensure it's fully rendered
                page.wait_for_timeout(2000)
                
                # Screenshot solely the QR canvas
                img_bytes = canvas.screenshot()
                wa_state["qr_code"] = "data:image/png;base64," + base64.b64encode(img_bytes).decode('utf-8')
                print("[SCANNER] Captured QR Code! Ready for frontend injection.")
            except Exception as e:
                print(f"[SCANNER] No QR code detected. {e}")
                
            print("[SCANNER] Waiting for the user to scan the code...")
            try:
                # Give them 90 seconds to scan before timing out
                page.wait_for_selector('#pane-side', timeout=90000)
                print("✅ [SCANNER] Successfully logged in! Session secured.")
                wa_state["status"] = "connected"
                wa_state["qr_code"] = None
            except Exception as e:
                print(f"❌ [SCANNER] Timeout waiting for scan.")
                wa_state["status"] = "timeout"
                
            browser.close()
    except Exception as e:
        print(f"❌ [SCANNER] Critical failure: {e}")
        wa_state["status"] = "error"

@app.route('/api/scan', methods=['POST'])
def trigger_scan():
    global wa_state
    wa_state["status"] = "scanning"
    wa_state["qr_code"] = None
    threading.Thread(target=headless_qr_scanner).start()
    return jsonify({"success": True})

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(wa_state)


@app.route('/api/send', methods=['POST'])
def send_message():
    """
    Microservice API Endpoint.
    Receives JSON: {"phone": "919111444147", "message": "Your text here"}
    Executes WhatsApp automation in a non-blocking background thread.
    """
    data = request.json
    
    if not data or 'phone' not in data or 'message' not in data:
        return jsonify({"success": False, "error": "Missing 'phone' or 'message' parameter"}), 400
        
    phone = data['phone']
    message = data['message']
    
    # Spawn background thread to prevent API from freezing for 15 seconds
    print(f"[API SERVER] Received request for {phone}. Starting background job...")
    threading.Thread(target=send_whatsapp_message, args=(phone, message)).start()
    
    return jsonify({
        "success": True, 
        "status": "Background WhatsApp job scheduled successfully!",
        "phone": phone
    }), 200

if __name__ == '__main__':
    print("🚀 WhatsApp API Server Started!")
    print("Listening on http://0.0.0.0:5001")
    # Host 0.0.0.0 is used so it binds on all server network interfaces (for VPS deployments)
    app.run(host='0.0.0.0', port=5001, debug=True)
