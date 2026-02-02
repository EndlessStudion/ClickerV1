from flask import Flask, request, jsonify
from flask_cors import CORS
import os, json, uuid

app = Flask(__name__)
CORS(app)

DB_FILE = "db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# ---------- ROUTES ----------

@app.route("/")
def home():
    return "✅ Clicker server is running!"

@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    login = data.get("login")
    password = data.get("pass")

    if not login or not password:
        return jsonify({"success": False, "message": "Введите логин и пароль"})

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

    token = db["users"][login]["token"]
    return jsonify({"success": True, "message": "Вход выполнен", "token": token})

@app.route("/status")
def status():
    login = request.args.get("user")
    token = request.args.get("token")

    db = load_db()
    if not login or login not in db["users"]:
        return jsonify({"success": False})

    user = db["users"][login]
    if user["token"] != token:
        return jsonify({"success": False})

    return jsonify({
        "success": True,
        "clicks": user["clicks"],
        "banned": user["banned"]
    })

@app.route("/click", methods=["POST"])
def click():
    data = request.json or {}
    login = data.get("user")
    token = data.get("token")
    clicks = data.get("clicks")

    db = load_db()
    if not login or login not in db["users"]:
        return jsonify({"success": False})

    user = db["users"][login]
    if user["token"] != token:
        return jsonify({"success": False})

    try:
        clicks = int(clicks)
    except:
        return jsonify({"success": False})

    user["clicks"] = clicks
    save_db(db)
    return jsonify({"success": True})

@app.route("/ban", methods=["POST"])
def ban():
    data = request.json or {}
    login = data.get("user")

    db = load_db()
    if login in db["users"]:
        db["users"][login]["banned"] = True
        save_db(db)

    return jsonify({"success": True})

DEV_CODE = "93+₽; ₽shhs29"

@app.route("/unban", methods=["POST"])
def unban():
    data = request.json or {}
    login = data.get("user")
    code = data.get("code")

    if code != DEV_CODE:
        return jsonify({"success": False, "message": "Неверный код"})

    db = load_db()
    if login in db["users"]:
        db["users"][login]["banned"] = False
        save_db(db)

    return jsonify({"success": True, "message": "Аккаунт разбанен"})

# ---------- PORT BINDING ДЛЯ RENDER ----------
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
