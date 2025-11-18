import http.server
from urllib.parse import urlparse, parse_qs
import sys
import cv2
import time
import threading
from http.server import HTTPServer
from socketserver import ThreadingMixIn

# Charger moteur
sys.path.append('../moteur')
import main_motor

# ================================
# Thread de capture vidéo
# ================================
cap = cv2.VideoCapture('/dev/v4l/by-id/usb-Suyin_HD_Camera_200910120001-video-index0')
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

latest_frame = None
lock = threading.Lock()

def capture_thread():
    global latest_frame
    while True:
        ret, frame = cap.read()
        if ret:
            with lock:
                latest_frame = frame.copy()
        time.sleep(0.02)    # 50 FPS max

# Lancer le thread caméra
threading.Thread(target=capture_thread, daemon=True).start()


# ================================
# Serveur HTTP
# ================================
class GestionnaireRequetes(http.server.SimpleHTTPRequestHandler):

    def _set_headers(self, code, type="text/html"):
        self.send_response(code)
        self.send_header("Content-type", type)
        self.end_headers()

    def do_GET(self):

        # ----------- STREAM MJPEG --------------
        if self.path == "/video":
            self.send_response(200)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
            self.end_headers()

            try:
                while True:
                    with lock:
                        frame = latest_frame

                    if frame is None:
                        time.sleep(0.1)
                        continue

                    _, jpeg = cv2.imencode('.jpg', frame)

                    self.wfile.write(b"--frame\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", str(len(jpeg)))
                    self.end_headers()
                    self.wfile.write(jpeg.tobytes())

                    time.sleep(0.03)  # contrôle du framerate pour alléger CPU

            except:
                print("Flux vidéo fermé")
            return

        # Autres fichiers statiques
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        """Les commandes moteur doivent s'exécuter dans un thread séparé."""
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        cmd_type = query.get("type", [None])[0]
        val = float(query.get("val", [0])[0])
        duration = float(query.get("time", [0.3])[0])

        print("[POST] Commande reçue :", cmd_type)

        # Thread pour exécuter la commande sans bloquer le serveur
        threading.Thread(
            target=self.execute_command,
            args=(cmd_type, val, duration),
            daemon=True
        ).start()

        self._set_headers(200)

    def execute_command(self, cmd_type, val, duration):
        """Thread exécutant réellement la commande moteur."""
        print(f"→ Exécution {cmd_type} (val={val}, time={duration})")
        
        # Petit délai entre les commandes si tu veux
        time.sleep(0.05)

        if cmd_type == "forward":
            main_motor.forward(val, duration)

        elif cmd_type == "backward":
            main_motor.backward(val, duration)

        elif cmd_type == "left":
            main_motor.left(val, duration)

        elif cmd_type == "right":
            main_motor.right(val, duration)

        elif cmd_type == "dance":
            main_motor.dance()

        print(f"✔️ Commande {cmd_type} terminée")


# Serveur multithread
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


PORT = 8080
print(f"Serveur lancé sur port {PORT} (threading actif)")
httpd = ThreadedHTTPServer(("", PORT), GestionnaireRequetes)
httpd.serve_forever()
