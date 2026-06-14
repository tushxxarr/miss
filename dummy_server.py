from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    # Render assigns a dynamic port, so we must use it. Default to 8080 if not found.
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
