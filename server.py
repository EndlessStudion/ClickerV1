from flask import Flask, request, jsonify
from flask_cors import CORS
import os, json, uuid

app = Flask(__name__)
CORS(app)

DB_FILE = "db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"users": {}}

def save_db(db):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except:
        pass

@app.route("/")
def home():
    return jsonify({"status": "ok"})

@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    login = data.get("login")
    password = data.get("pass")

    if not login or not password:
        return jsonify({"success": False, "message": "Введите ник и пароль"})

    db = load_db()

    if login in db["users"]:
        return jsonify({"success": False, "message": "Ник уже существует"})

    token = str(uuid.uuid4())
    db["users"][login] = {"password": password, "clicks": 0, "token": token}
    save_db(db)

    return jsonify({"success": True, "token": token})

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    login = data.get("login")
    password = data.get("pass")

    db = load_db()

    if login not in db["users"]:
        return jsonify({"success": False, "message": "Аккаунт не найден"})

    if db["users"][login]["password"] != password:
        return jsonify({"success": False, "message": "Неверный пароль"})

    return jsonify({"success": True, "token": db["users"][login]["token"]})

@app.route("/status")
def status():
    user = request.args.get("user")
    token = request.args.get("token")

    db = load_db()

    if user not in db["users"]:
        return jsonify({"clicks": 0})

    u = db["users"][user]

    if u["token"] != token:
        return jsonify({"clicks": 0})

    return jsonify({"clicks": int(u.get("clicks", 0))})

@app.route("/click", methods=["POST"])
def click():
    data = request.json or {}
    user = data.get("user")
    token = data.get("token")
    clicks = int(data.get("clicks", 0))

    db = load_db()

    if user not in db["users"]:
        return jsonify({"success": False})

    if db["users"][user]["token"] != token:
        return jsonify({"success": False})

    db["users"][user]["clicks"] = clicks
    save_db(db)

    return jsonify({"success": True})

@app.route("/top")
def top():
    db = load_db()
    users = db.get("users", {})

    players = []
    for name, u in users.items():
        players.append({
            "name": name,
            "clicks": int(u.get("clicks", 0))
        })

    players.sort(key=lambda x: x["clicks"], reverse=True)

    return jsonify({"top": players})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
