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
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

@app.route("/")
def home():
    return "✅ Server is working!"

# ================= REGISTER =================
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
    db["users"][login] = {
        "password": password,
        "clicks": 0,
        "banned": False,
        "token": token
    }
    save_db(db)

    return jsonify({"success": True, "message": "Регистрация успешна", "token": token})

# ================= LOGIN =================
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

# ================= STATUS =================
@app.route("/status")
def status():
    user = request.args.get("user")
    token = request.args.get("token")

    db = load_db()

    if user not in db["users"]:
        return jsonify({"clicks": 0, "banned": False})

    u = db["users"][user]

    if u.get("token") != token:
        return jsonify({"clicks": 0, "banned": False})

    return jsonify({
        "clicks": int(u.get("clicks", 0)),
        "banned": bool(u.get("banned", False))
    })

# ================= CLICK =================
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

# ================= TOP =================
@app.route("/top")
def top():
    db = load_db()

    users = db.get("users", {})

    players = []
    for name, data in users.items():
        clicks = int(data.get("clicks", 0))
        players.append({"name": name, "clicks": clicks})

    players.sort(key=lambda x: x["clicks"], reverse=True)

    return jsonify({"top": players})

# ================= BAN =================
@app.route("/ban", methods=["POST"])
def ban():
    data = request.json or {}
    user = data.get("user")

    db = load_db()
    if user in db["users"]:
        db["users"][user]["banned"] = True
        save_db(db)

    return jsonify({"success": True})

# ================= UNBAN =================
DEV_CODE = "93+₽; ₽shhs29"

@app.route("/unban", methods=["POST"])
def unban():
    data = request.json or {}
    user = data.get("user")
    code = data.get("code")

    if code != DEV_CODE:
        return jsonify({"success": False})

    db = load_db()
    if user in db["users"]:
        db["users"][user]["banned"] = False
        save_db(db)

    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
