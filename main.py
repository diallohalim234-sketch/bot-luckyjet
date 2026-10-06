import json
import time
import websocket
from telegram import Bot
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8677913643:AAED_SKn1qdXyi1YtbIBLGN9YhqmIzDFJxE"
CHAT_ID = "8781524714"
WEBSOCKET_URL = "wss://lucky-jet-api-or-stream-url.com/connect"

streak_under_1_5 = 0
bot = Bot(token=TELEGRAM_TOKEN)

# Serveur Web pour éviter que Render ne coupe le service gratuit
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Lucky Jet actif !")

def run_http_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

def send_telegram_alert(count):
    message = (
        f"🚨 **ALERTE LUCKY JET** 🚨\n\n"
        f"Le multiplicateur est tombé en dessous de **1.50** "
        f"pendant **{count} tours d'affilée** !"
    )
    asyncio.run(bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown"))

def on_message(ws, message):
    global streak_under_1_5
    try:
        data = json.loads(message)
        if "multiplier" in data:
            multiplier = float(data["multiplier"])
            print(f"Tour : {multiplier}x")
            
            if multiplier < 1.50:
                streak_under_1_5 += 1
                print(f"Série sous 1.50 : {streak_under_1_5}/7")
            else:
                streak_under_1_5 = 0
            
            if streak_under_1_5 == 7:
                send_telegram_alert(streak_under_1_5)
    except Exception as e:
        print(f"Erreur : {e}")

def on_error(ws, error):
    print(f"Erreur WS : {error}")

def on_close(ws, close_status_code, close_msg):
    time.sleep(5)
    run_websocket()

def run_websocket():
    ws = websocket.WebSocketApp(
        WEBSOCKET_URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

if __name__ == "__main__":
    threading.Thread(target=run_http_server, daemon=True).start()
    run_websocket()
                               
