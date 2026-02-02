import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import time

DATA_FILE = "users.json"
UNBAN_CODE = "93+₽; ₽shhs29"

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
                self.wfile.write(json.dumps({"status":"error","msg":"exists"}).encode())
                return

            users[username] = {
                "password": password,
                "score": 0,
                "warn": 0,
                "ban": False,
                "last_time": 0,
                "last_score": 0
            }

            save_data(users)
            self._set_headers()
            self.wfile.write(json.dumps({"status":"ok"}).encode())
            return

        # 🔐 вход
        if self.path == "/login":
            username = data.get("username")
            password = data.get("password")

            if username not in users:
                self._set_headers()
                self.wfile.write(json.dumps({"status":"error","msg":"no_user"}).encode())
                return

            if users[username]["ban"]:
                self._set_headers()
                self.wfile.write(json.dumps({"status":"ban"}).encode())
                return

            if users[username]["password"] == password:
                self._set_headers()
                self.wfile.write(json.dumps({
                    "status":"ok",
                    "score": users[username]["score"],
                    "warn": users[username]["warn"]
                }).encode())
            else:
                self._set_headers()
                self.wfile.write(json.dumps({"status":"error","msg":"wrong_pass"}).encode())
            return

        # 🔓 разбан
        if self.path == "/unban":
            username = data.get("username")
            code = data.get("code")

            if username in users and code == UNBAN_CODE:
                users[username]["ban"] = False
                users[username]["warn"] = 0
                save_data(users)

                self._set_headers()
                self.wfile.write(json.dumps({"status":"ok"}).encode())
            else:
                self._set_headers()
                self.wfile.write(json.dumps({"status":"error"}).encode())
            return

        # 📤 обновление очков + античит
        if self.path == "/update":
            username = data.get("username")
            score = int(data.get("score", 0))

            if username not in users:
                self._set_headers()
                self.wfile.write(json.dumps({"status":"error"}).encode())
                return

            user = users[username]

            if user["ban"]:
                self._set_headers()
                self.wfile.write(json.dumps({"status":"ban"}).encode())
                return

            now = time.time()
            dt = now - user["last_time"]
            diff = score - user["last_score"]

            cheat = False

            # ⚡ слишком быстро кликает
            if dt < 0.05 and diff > 3:
                cheat = True

            # 💥 слишком большой скачок очков
            if diff > 100:
                cheat = True

            if cheat:
                user["warn"] += 1

                if user["warn"] >= 3:
                    user["ban"] = True

                save_data(users)
                self._set_headers()
                self.wfile.write(json.dumps({
                    "status":"warn",
                    "warn": user["warn"],
                    "ban": user["ban"]
                }).encode())
                return

            if score > user["score"]:
                user["score"] = score

            user["last_time"] = now
            user["last_score"] = score

            save_data(users)
            self._set_headers()
            self.wfile.write(json.dumps({"status":"ok"}).encode())
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
