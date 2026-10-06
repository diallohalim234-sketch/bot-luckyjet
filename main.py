import time
import requests
import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "8677913643"
TELEGRAM_CHAT_ID = ""  # Mettez votre Chat ID Telegram ici (ex: "123456789")

# Endpoint API direct pour le suivi
API_URL = "https://crash-gateway-cr.1win.tf/state"

low_streak = 0  # Compteur de tours sous 1.50x

# --- SERVEUR HTTP POUR MANTEINIR RENDER ACTIF (KEEP-ALIVE) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot Lucky Jet actif 24/7 sur Render !")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Serveur Web lance sur le port {port}")
    server.serve_forever()

# --- ENVOI ALERTES TELEGRAM ---
def send_telegram_alert(message):
    if not TELEGRAM_CHAT_ID:
        print("Chat ID manquant ! L'alerte ne peut pas etre envoyee.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Erreur d'envoi Telegram: {e}")

# --- SURVEILLANCE DES TOURS EN CONTINU ---
def monitor_game():
    global low_streak
    print("Demarrage de la surveillance des cotes Lucky Jet...")
    last_processed_id = None

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    }

    while True:
        try:
            response = requests.get(API_URL, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Extraction du multiplicateur du tour actuel ou precedent
                multiplier = float(data.get("topMultiplier", data.get("coefficient", 0)))
                game_id = data.get("id", data.get("gameId"))

                if multiplier > 0 and game_id != last_processed_id:
                    last_processed_id = game_id
                    print(f"Nouveau tour détecté : {multiplier}x")

                    if multiplier < 1.50:
                        low_streak += 1
                        print(f"Série sous 1.50x : {low_streak}/7")
                    else:
                        low_streak = 0

                    if low_streak >= 1:
                        msg = f"⚠️ **ALERTE LUCKY JET** ⚠️\n\n7 tours consecutifs sous 1.50x détectés !\nDerniere cote: {multiplier}x\nPréparer une stratégie."
                        send_telegram_alert(msg)
                        low_streak = 0
            
        except Exception as e:
            print(f"Attente du prochain tour... ({e})")

        time.sleep(3)  # Verification toutes les 3 secondes

if __name__ == "__main__":
    # Lancement du serveur Web en arrière-plan
    threading.Thread(target=run_http_server, daemon=True).start()
    
    # Lancement du script de surveillance
    monitor_game()
                      
