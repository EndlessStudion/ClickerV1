from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os, random, requests

app = Flask(__name__)
CORS(app)

DB_FILE = "users.json"

RESEND_API_KEY = "re_iJLi634y_LSov9U9khENQfG82GP9KshXr"  # 👈 новый ключ

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def send_code(email, code):
    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {re_iJLi634y_LSov9U9khENQfG82GP9KshXr}",
                "Content-Type": "application/json"
            },
            json={
                "from": "ClickerV1 <Endlessstudion@gmail.com>",
                "to": email,
                "subject": "ClickerV1 — код подтверждения",
                "html": f"<h1>Ваш код: {code}</h1>"
            }
        )
        print("MAIL STATUS:", r.status_code, r.text)
        return r.status_code == 200
    except Exception as e:
        print("MAIL ERROR:", e)
        return False

@app.route("/")
def home():
    return "ClickerV1 server online"

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    login = data.get("login")
    password = data.get("password")
    email = data.get("email")

    users = load_users()

    if login in users:
        return jsonify({"ok": False, "msg": "Аккаунт уже существует"})

    code = str(random.randint(100000, 999999))

    users[login] = {
        "password": password,
        "clicks": 0,
        "email": email,
        "verified": False,
        "code": code
    }

    save_users(users)

    mail_ok = send_code(email, code)

    # 🔥 ВАЖНО: даже если почта не отправилась — код вернём в ответ
    return jsonify({
        "ok": True,
        "debug_code": code,   # 👈 ТЕСТОВЫЙ КОД
        "mail": mail_ok
    })

@app.route("/verify", methods=["POST"])
def verify():
    data = request.json
    login = data.get("login")
    code = data.get("code")

    users = load_users()

    if login not in users:
        return jsonify({"ok": False, "msg": "Нет аккаунта"})

    if users[login]["code"] != code:
        return jsonify({"ok": False, "msg": "Неверный код"})

    users[login]["verified"] = True
    users[login]["code"] = ""
    save_users(users)

    return jsonify({"ok": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
