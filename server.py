import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

DATA_FILE = "users.json"

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

class Handler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode("utf-8")
        data = json.loads(body)

        users = load_data()

        # 🧩 регистрация
        if self.path == "/register":
            username = data.get("username")
            password = data.get("password")

            if username in users:
                self._set_headers()
                self.wfile.write(json.dumps({"status": "error", "msg": "User exists"}).encode())
                return

            users[username] = {"password": password, "score": 0}
            save_data(users)

            self._set_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            return

        # 🔐 вход
        if self.path == "/login":
            username = data.get("username")
            password = data.get("password")

            if username in users and users[username]["password"] == password:
                self._set_headers()
                self.wfile.write(json.dumps({"status": "ok", "score": users[username]["score"]}).encode())
            else:
                self._set_headers()
                self.wfile.write(json.dumps({"status": "error"}).encode())
            return

        # 📤 обновление очков
        if self.path == "/update":
            username = data.get("username")
            score = int(data.get("score", 0))

            if username in users:
                if score > users[username]["score"]:
                    users[username]["score"] = score
                    save_data(users)

            self._set_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            return

    def do_GET(self):
        if self.path == "/top":
            users = load_data()
            sorted_users = sorted(users.items(), key=lambda x: x[1]["score"], reverse=True)
            top = [{"username": u, "score": s["score"]} for u, s in sorted_users[:10]]

            self._set_headers()
            self.wfile.write(json.dumps(top).encode())

def run():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print("🔥 Server started on port", port)
    server.serve_forever()

if __name__ == "__main__":
    run()
