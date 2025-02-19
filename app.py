from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Инициализация БД
def init_db():
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            score INTEGER DEFAULT 0
        )"""
    )
    conn.commit()
    conn.close()

init_db()

# Функция обновления очков
def update_score(telegram_id, username):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,))
    user = cursor.fetchone()

    if user:
        cursor.execute("UPDATE users SET score = score + 1 WHERE telegram_id=?", (telegram_id,))
    else:
        cursor.execute("INSERT INTO users (telegram_id, username, score) VALUES (?, ?, ?)", (telegram_id, username, 1))

    conn.commit()
    conn.close()

# Получение таблицы лидеров
def get_leaderboard():
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, score FROM users ORDER BY score DESC LIMIT 10")
    top_players = cursor.fetchall()
    conn.close()
    return [{"username": row[0], "score": row[1]} for row in top_players]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/click", methods=["POST"])
def click():
    data = request.json
    telegram_id = data.get("telegram_id")
    username = data.get("username")

    if telegram_id and username:
        update_score(telegram_id, username)
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    return jsonify(get_leaderboard())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
