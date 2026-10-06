import asyncio
import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import websocket

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "8677913643"  # Votre Token Bot
TELEGRAM_CHAT_ID = ""  # Mettez votre Chat ID Telegram ici (ex: "123456789")

# URL générique du serveur Lucky Jet
WEBSOCKET_URL = "wss://crash-gateway-cr.1win.tf/connection/websocket"

low_streak = 0  # Compteur de tours sous 1.50x

# --- SERVEUR HTTP FLASK/SERVEUR POUR KEEP-ALIVE RENDER ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(b"Bot Lucky Jet actif 24/7 sur Render !")


def run_http_server():
  port = int(os.environ.get("PORT", 10000))
  server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
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


# --- TRAITEMENT DES DONNEES WEBSOCKET ---
def on_message(ws, message):
  global low_streak
  try:
    data = json.loads(message)

    # Verification de la presence d'un multiplicateur dans le message
    if "val" in data or "coefficient" in data:
      multiplier = float(data.get("val", data.get("coefficient", 0)))

      if multiplier > 0:
        print(f"Nouveau tour recu : {multiplier}x")

        if multiplier < 1.50:
          low_streak += 1
          print(f"Série sous 1.50x : {low_streak}/7")
        else:
          low_streak = 0

        if low_streak == 7:
          msg = (
              "⚠️ **ALERTE LUCKY JET** ⚠️\n\n7 tours consecutifs sous 1.50x"
              " détectés !\nPréparer une stratégie."
          )
          send_telegram_alert(msg)
          low_streak = 0
  except Exception as e:
    pass


def on_error(ws, error):
  print(f"Erreur WebSocket: {error}")


def on_close(ws, close_status_code, close_msg):
  print("Connexion fermee, reconnexion en cours...")


def on_open(ws):
  print("Connecte au flux de donnees Lucky Jet !")


def start_websocket():
  ws = websocket.WebSocketApp(
      WEBSOCKET_URL,
      on_open=on_open,
      on_message=on_message,
      on_error=on_error,
      on_close=on_close,
  )
  ws.run_forever()


if __name__ == "__main__":
  # Lancement du serveur Web en arrière-plan pour Render
  threading.Thread(target=run_http_server, daemon=True).start()

  # Lancement de l'ecoute en direct
  start_websocket()
    
