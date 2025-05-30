from flask import Flask, request, render_template, redirect
import random
import string
import json
import os

app = Flask(__name__)
DATA_FILE = "draw_sessions.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def generate_tokens(n):
    return ["".join(random.choices(string.ascii_uppercase + string.digits, k=6)) for _ in range(n)]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            total = int(request.form["total"])
        except:
            return "请输入有效数字！"
        session_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        numbers = list(range(1, total + 1))
        tokens = generate_tokens(total)
        session_data = {
            "max_number": total,
            "available_numbers": numbers,
            "tokens": {token: None for token in tokens}
        }
        data = load_data()
        data[session_id] = session_data
        save_data(data)
        return render_template("created.html", session_id=session_id, tokens=tokens)
    return render_template("index.html")

@app.route("/draw", methods=["GET", "POST"])
def draw():
    if request.method == "POST":
        token = request.form["token"].strip().upper()
        data = load_data()
        for session_id, session in data.items():
            if token in session["tokens"]:
                if session["tokens"][token] is not None:
                    return render_template("result.html", number=session["tokens"][token])
                if not session["available_numbers"]:
                    return "所有数字都已被抽完。"
                number = random.choice(session["available_numbers"])
                session["available_numbers"].remove(number)
                session["tokens"][token] = number
                save_data(data)
                return render_template("result.html", number=number)
        return "无效或重复的密钥。"
    return render_template("draw.html")

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Render 会自动设置 PORT 环境变量
    app.run(host='0.0.0.0', port=port)
