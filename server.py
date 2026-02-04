from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DB_FILE = "users.json"

# Загрузка базы
def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Сохранение базы
def save_users(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Проверка сервера
@app.route("/")
def home():
    return "ClickerV1 server online"

# Регистрация
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    login = data.get("login")
    password = data.get("password")

    if not login or not password:
        return jsonify({"ok": False, "msg": "Введите логин и пароль"})

    users = load_users()
    if login in users:
        return jsonify({"ok": False, "msg": "Аккаунт уже существует"})

    users[login] = {"password": password, "clicks": 0}
    save_users(users)

    return jsonify({"ok": True})

# Вход
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    login = data.get("login")
    password = data.get("password")

    users = load_users()
    if login not in users or users[login]["password"] != password:
        return jsonify({"ok": False, "msg": "Неверный логин или пароль"})

    return jsonify({"ok": True, "clicks": users[login]["clicks"]})

# Клик
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

# Топ
@app.route("/top")
def top():
    users = load_users()
    top_list = sorted(
        [{"login": k, "clicks": v["clicks"]} for k, v in users.items()],
        key=lambda x: x["clicks"],
        reverse=True
    )[:10]

    return jsonify(top_list)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
