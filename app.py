from flask import Flask, jsonify, request
import sqlite3
import logging
import os
import ddtrace

ddtrace.patch_all()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("DB_PATH", "news.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            category TEXT,
            published INTEGER DEFAULT 0
        )
    """)
    # BUG: missing email and profile columns — will cause 500 errors
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO articles (id, title, category) VALUES (1, 'Breaking News', 'politics')")
    cursor.execute("INSERT OR IGNORE INTO articles (id, title, category) VALUES (2, 'Sports Update', 'sports')")
    conn.commit()
    conn.close()
    logger.info("Database initialized at %s", DB_PATH)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "db": DB_PATH})


@app.route("/articles")
def get_articles():
    try:
        conn = get_db()
        rows = conn.execute("SELECT * FROM articles").fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        logger.error("DB error fetching articles: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/articles/<int:article_id>")
def get_article(article_id):
    try:
        conn = get_db()
        row = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify(dict(row))
    except Exception as e:
        logger.error("DB error fetching article %s: %s", article_id, e)
        return jsonify({"error": str(e)}), 500


@app.route("/users", methods=["POST"])
def create_user():
    """BUG: users table has no email column — throws OperationalError"""
    try:
        data = request.get_json() or {}
        conn = get_db()
        conn.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            (data.get("username"), data.get("email")),
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "created"}), 201
    except Exception as e:
        logger.error("DB error creating user: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/users/<int:user_id>/profile")
def get_user_profile(user_id):
    """BUG: queries non-existent email and profile columns"""
    try:
        conn = get_db()
        row = conn.execute(
            "SELECT id, username, email, profile FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify(dict(row))
    except Exception as e:
        logger.error("DB error fetching profile for user %s: %s", user_id, e)
        return jsonify({"error": str(e)}), 500


@app.route("/publish/<int:article_id>", methods=["POST"])
def publish_article(article_id):
    """BUG: wrong column name is_published instead of published"""
    try:
        conn = get_db()
        conn.execute("UPDATE articles SET is_published = 1 WHERE id = ?", (article_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "published"})
    except Exception as e:
        logger.error("DB error publishing article %s: %s", article_id, e)
        return jsonify({"error": str(e)}), 500


@app.route("/spike-errors")
def spike_errors():
    """Trigger all broken endpoints to spike APM error rate"""
    results = []
    with app.test_client() as c:
        for _ in range(15):
            r1 = c.post("/users", json={"username": "test", "email": "test@test.com"})
            r2 = c.get("/users/1/profile")
            r3 = c.post("/publish/1")
            results.append({
                "create_user": r1.status_code,
                "get_profile": r2.status_code,
                "publish": r3.status_code,
            })
    return jsonify({"triggered": len(results), "sample": results[0]})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=False)
