from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os, random, smtplib, time
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app)

DATA_FILE = "users.json"

# Почта для отправки кодов
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_LOGIN = "Endlessstudion@gmail.com"
SMTP_PASS = "qpjs lsjh ciil vhyz"
FROM_EMAIL = SMTP_LOGIN

CLICK_LIMIT = 20  # античит: лимит кликов в секунду

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def send_code(email, code):
    msg = MIMEText(f"Ваш код ClickerV1: {code}", "plain", "utf-8")
    msg["Subject"] = "ClickerV1 — код подтверждения"
    msg["From"] = FROM_EMAIL
    msg["To"] = email

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_LOGIN, SMTP_PASS)
    server.sendmail(FROM_EMAIL, email, msg.as_string())
    server.quit()

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    if not username or not password or not email:
        return jsonify({"error":"Заполни все поля"}),400

    users = load_users()
    if username in users:
        return jsonify({"error":"Ник занят"}),400

    code = str(random.randint(100000, 999999))
    users[username] = {
        "password": password,
        "email": email,
        "code": code,
        "verified": False,
        "clicks": 0,
        "ip": ip,
        "last_click": 0
    }
    save_users(users)
    send_code(email, code)
    return jsonify({"success": True, "msg":"Код отправлен на почту"})

@app.route("/verify_code", methods=["POST"])
def verify_code():
    data = request.json
    username = data.get("username")
    code = data.get("code")
    users = load_users()
    if username not in users: return jsonify({"error":"Нет пользователя"}),400
    if users[username]["code"] != code: return jsonify({"error":"Неверный код"}),400
    users[username]["verified"]=True
    users[username]["code"]=""
    save_users(users)
    return jsonify({"success":True})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    users = load_users()
    if username not in users or users[username]["password"]!=password:
        return jsonify({"error":"Неверные данные"}),400
    if not users[username]["verified"]:
        return jsonify({"error":"Подтверди почту"}),400
    return jsonify({"success":True,"clicks":users[username]["clicks"]})

@app.route("/click", methods=["POST"])
def click():
    data = request.json
    username = data.get("username")
    users = load_users()
    if username not in users: return jsonify({"error":"Нет пользователя"}),400

    # античит
    now = time.time()
    if now - users[username].get("last_click",0) < 0.05:
        return jsonify({"error":"Слишком быстро"}),400
    users[username]["clicks"]+=1
    users[username]["last_click"]=now
    save_users(users)
    return jsonify({"clicks": users[username]["clicks"]})

@app.route("/top")
def top():
    users = load_users()
    sorted_users = sorted(users.items(), key=lambda x:x[1]["clicks"], reverse=True)
    return jsonify([{"name": u[0], "clicks": u[1]["clicks"]} for u in sorted_users[:100]])

if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
