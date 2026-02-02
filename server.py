from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os

app = Flask(__name__)
CORS(app)

DB_FILE = "db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": []}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

@app.route("/")
def home():
    return "SERVER OK"

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    login = data.get("login")
    password = data.get("password")

    db = load_db()

    for u in db["users"]:
        if u["login"] == login:
            return jsonify({"error": "User exists"}), 400

    user = {"login": login, "password": password, "clicks": 0}
    db["users"].append(user)
    save_db(db)

    return jsonify({"ok": True})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    login = data.get("login")
    password = data.get("password")

    db = load_db()

    for u in db["users"]:
        if u["login"] == login and u["password"] == password:
            return jsonify({"ok": True, "clicks": u["clicks"]})

    return jsonify({"error": "Wrong login"}), 400

@app.route("/click", methods=["POST"])
def click():
    data = request.json
    login = data.get("login")

    db = load_db()

    for u in db["users"]:
        if u["login"] == login:
            u["clicks"] += 1
            save_db(db)
            return jsonify({"clicks": u["clicks"]})

    return jsonify({"error": "User not found"}), 400

@app.route("/top")
def top():
    db = load_db()
    users = sorted(db["users"], key=lambda x: x["clicks"], reverse=True)
    top10 = [{"login": u["login"], "clicks": u["clicks"]} for u in users[:10]]
    return jsonify(top10)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
