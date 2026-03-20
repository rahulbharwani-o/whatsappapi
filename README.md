# Standalone Background WhatsApp API Server

This folder contains a fully packaged, standalone microservice that exposes a simple `POST` API to send WhatsApp messages completely invisibly in the background. You can upload this folder to any server (VPS like AWS, DigitalOcean, Hetzner, etc) and consume the API from anywhere, using any language (PHP, Node, Go, etc).

## 🚀 Setting up on a Linux Server (VPS/Ubuntu)

### 1. Install Dependencies
SSH into your server and install Python and Playwright.

```bash
# Update and install python requirements
sudo apt update
sudo apt install python3 python3-venv python3-pip -y

# Setup a virtual environment inside this folder
cd server_whatsapp_api/
python3 -m venv venv
source venv/bin/activate

# Install the Python requirements
pip install -r requirements.txt

# Install the Chromium browser and its system dependencies
playwright install chromium
playwright install-deps chromium
```

### 2. How to handle the WhatsApp Login on a Headless Linux Server
Because `setup.py` opens a visible browser to scan a QR code, you cannot run it on a standard headless Linux VPS (it will crash since there is no desktop GUI). 

**The Solution:**
1. Run `python3 setup.py` on your **local Mac/Windows computer** first.
2. Scan the QR code.
3. This creates a hidden folder called `whatsapp_session/` on your local computer.
4. Simply upload/ZIP that entire `whatsapp_session` folder directly onto your server alongside these files!
5. Playwright on the server will read the uploaded session cookies and be instantly authenticated!

### 3. Start the API Server!
Once the session is uploaded, boot up the API worker:

```bash
# We recommend running this using 'screen', 'tmux', or PM2 so it stays alive
source venv/bin/activate
python3 api.py
```

It will now be listening globally on `http://SERVER_IP:5001`.

## 🌐 How to consume your API in PHP
Once the python server is running, any PHP script on your website can trigger a background WhatsApp ping instantaneously:

```php
<?php
$payload = json_encode([
    "phone" => "919876543210", 
    "message" => "Invoice Paid Successfully!"
]);

$ch = curl_init('http://127.0.0.1:5001/api/send'); // Change 127.0.0.1 if API server is hosted elsewhere
curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
curl_exec($ch);
?>
```
