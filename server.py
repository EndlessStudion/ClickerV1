from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os, random, smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app)

DB_FILE = "users.json"

# Почта для отправки (отправитель)
EMAIL_FROM = "Endlessstudion@gmail.com"  # твоя почта
EMAIL_PASSWORD = "Ekke82OoP!"           # пароль приложения Gmail

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# функция отправки кода
def send_code(email_to, code):
    text = f"ClickerV1\n\nВаш код подтверждения: {code}"
    msg = MIMEText(text)
    msg["Subject"] = "ClickerV1 - подтверждение аккаунта"
    msg["From"] = EMAIL_FROM
    msg["To"] = email_to

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Код {code} отправлен на {email_to}")
        return True
    except Exception as e:
        print("MAIL ERROR:", e)
        print(f"DEBUG: Код для {email_to}: {code}")  # выводим код в консоль для теста
        return False

@app.route("/")
def home():
    return "ClickerV1 server online"

# регистрация
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    login = data.get("login")
    password = data.get("password")
    email = data.get("email")

    if not login or not password or not email:
        return jsonify({"ok": False, "msg": "Заполните все поля"})

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

    send_code(email, code)  # отправка кода

    return jsonify({"ok": True, "msg": "Код отправлен на почту (или в консоль для теста)"})

# подтверждение кода
@app.route("/verify", methods=["POST"])
def verify():
    data = request.json
    login = data.get("login")
    code = data.get("code")

    users = load_users()
    if login not in users:
        return jsonify({"ok": False, "msg": "Аккаунт не найден"})
    if users[login]["code"] != code:
        return jsonify({"ok": False, "msg": "Неверный код"})

    users[login]["verified"] = True
    users[login]["code"] = ""
    save_users(users)
    return jsonify({"ok": True})

# вход
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    login = data.get("login")
    password = data.get("password")

    users = load_users()
    if login not in users or users[login]["password"] != password:
        return jsonify({"ok": False, "msg": "Неверный логин или пароль"})
    if not users[login]["verified"]:
        return jsonify({"ok": False, "msg": "Подтвердите почту"})

    return jsonify({"ok": True, "clicks": users[login]["clicks"]})

# клик
@app.route("/click", methods=["POST"])
def click():
    data = request.json
    login = data.get("login")
    users = load_users()
    if login not in users:
        return jsonify({"ok": False})
    users[login]["clicks"] += 1
    save_users(users)
    return jsonify({"ok": True, "clicks": users[login]["clicks"]})

# топ
@app.route("/top")
def top():
    users = load_users()
    top_list = sorted(
        [{"login": k, "clicks": v["clicks"]} for k, v in users.items()],
        key=lambda x: x["clicks"], reverse=True
    )[:10]
    return jsonify(top_list)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
