import http.server
from urllib.parse import urlparse, parse_qs
import sys

# accès au dossier moteur
sys.path.append('../moteur')
import main_motor


class GestionnaireRequetes(http.server.SimpleHTTPRequestHandler):

    def _set_headers(self, code, type="text/html"):
        self.send_response(code)
        self.send_header("Content-type", type)
        self.end_headers()

    # -------------------------------------------------------------
    # GET : sert les fichiers HTML, JS, CSS, images
    # -------------------------------------------------------------
    def do_GET(self):
        allowed = (".html", ".css", ".js", ".png", ".jpg", ".jpeg", ".svg")

        if self.path == "/" or self.path == "":
            filepath = "index.html"
        else:
            filepath = self.path.lstrip("/")

        if filepath.endswith(allowed):
            try:
                # type MIME
                if filepath.endswith(".css"):
                    mime = "text/css"
                elif filepath.endswith(".js"):
                    mime = "application/javascript"
                elif filepath.endswith(".png"):
                    mime = "image/png"
                elif filepath.endswith(".jpg") or filepath.endswith(".jpeg"):
                    mime = "image/jpeg"
                elif filepath.endswith(".svg"):
                    mime = "image/svg+xml"
                else:
                    mime = "text/html"

                with open(filepath, "rb") as f:
                    content = f.read()

                self._set_headers(200, mime)
                self.wfile.write(content)

            except:
                self._set_headers(500)
        else:
            self._set_headers(404)

    # -------------------------------------------------------------
    # POST : reçoit les commandes boutons ou joystick
    # -------------------------------------------------------------
    def do_POST(self):

        if not self.path.startswith("/commandes"):
            self._set_headers(400)
            return

        try:
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)

            cmd_type = query.get("type", [None])[0]

            # -----------------------------
            # JOYSTICK → main_motor.avancer(left, right, time)
            # -----------------------------
            if cmd_type == "joystick":
                left = float(query.get("left", [0])[0])
                right = float(query.get("right", [0])[0])
                duration = float(query.get("time", [0.1])[0])

                print(f"[JOYSTICK] left={left} right={right} time={duration}")
                main_motor.avancer(left, right, duration)

            # -----------------------------
            # BOUTONS → forward/backward/right/left/dance
            # -----------------------------
            else:
                val = float(query.get("val", [0])[0])
                duration = float(query.get("time", [1])[0])

                print(f"[BOUTON] type={cmd_type} val={val} time={duration}")

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
                else:
                    print("Commande inconnue.")
                    self._set_headers(400)
                    return

            self._set_headers(200)

        except Exception as e:
            print("Erreur POST :", e)
            self._set_headers(400)


# -----------------------------
# Lancement du serveur
# -----------------------------
PORT = 8080
print(f"Server running on port {PORT}...")
httpd = http.server.HTTPServer(("", PORT), GestionnaireRequetes)
httpd.serve_forever()
