import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

DATA_FILE = "players.json"

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
        if self.path == "/update":
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)

            username = data.get("username", "Player")
            score = int(data.get("score", 0))

            players = load_data()

            if username in players:
                if score > players[username]:
                    players[username] = score
            else:
                players[username] = score

            save_data(players)

            self._set_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))

    def do_GET(self):
        if self.path == "/top":
            players = load_data()
            sorted_players = sorted(players.items(), key=lambda x: x[1], reverse=True)
            top10 = [{"username": u, "score": s} for u, s in sorted_players[:10]]

            self._set_headers()
            self.wfile.write(json.dumps(top10).encode("utf-8"))

def run():
    port = int(os.environ.get("PORT", 5000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print("🔥 Server started on port", port)
    server.serve_forever()

if __name__ == "__main__":
    run()