from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Функция для обновления очков
def update_score(telegram_id, username):
    conn = sqlite3.connect("/tmp/game.db")  # Используем временную БД
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            score INTEGER DEFAULT 0
        )"""
    )
    conn.commit()

    cursor.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,))
    user = cursor.fetchone()

    if user:
        cursor.execute("UPDATE users SET score = score + 1 WHERE telegram_id=?", (telegram_id,))
    else:
        cursor.execute("INSERT INTO users (telegram_id, username, score) VALUES (?, ?, ?)", (telegram_id, username, 1))

    conn.commit()
    conn.close()

# Обработчик нажатия
@app.route("/api/click", methods=["POST"])
def click():
    data = request.json
    telegram_id = data.get("telegram_id")
    username = data.get("username")

    if telegram_id and username:
        update_score(telegram_id, username)
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

# Таблица лидеров
@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    conn = sqlite3.connect("/tmp/game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, score FROM users ORDER BY score DESC LIMIT 10")
    top_players = cursor.fetchall()
    conn.close()
    return jsonify([{"username": row[0], "score": row[1]} for row in top_players])

# Vercel handler
def handler(event, context):
    return app(event, context)
