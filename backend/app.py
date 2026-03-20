import os
from flask import Flask, request, redirect, session, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import bcrypt
from dotenv import load_dotenv

# ---------------- LOAD ENV ----------------
load_dotenv()
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app, supports_credentials=True, origins=os.getenv("FRONTEND_URL", "*"))

app.secret_key = os.getenv("SECRET_KEY", "change-me-in-production")

# Use /tmp for SQLite on Render (ephemeral but works for demo/hackathon)
# For production, switch to PostgreSQL (free on Render)
DB_PATH = os.getenv("DB_PATH", "/tmp/users.db")

# ---------------- DATABASE ----------------
def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_db() as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
        """)

init_db()

# ---------------- AUTH HELPER ----------------
def require_auth():
    return "user_id" in session

# ---------------- ROUTES ----------------

@app.route("/")
def entry():
    if require_auth():
        return redirect("/landing")
    return render_template("entry.html")

@app.route("/landing")
def landing():
    if not require_auth():
        return redirect("/")
    return render_template("landing.html")

@app.route("/app")
def app_page():
    if not require_auth():
        return redirect("/")
    return render_template("kalai.html")

# Health check — Render uses this to confirm the service is alive
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# ---------------- API ----------------

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    if not data or not all(k in data for k in ["firstName", "lastName", "email", "password"]):
        return jsonify({"error": "Missing required fields"}), 400

    hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())
    try:
        with get_db() as db:
            db.execute(
                "INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
                (data["firstName"], data["lastName"], data["email"], hashed)
            )
            user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            session["user_id"] = user_id
        return jsonify({"success": True, "redirect": "/landing"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    if not data or not all(k in data for k in ["email", "password"]):
        return jsonify({"error": "Missing required fields"}), 400

    with get_db() as db:
        user = db.execute(
            "SELECT * FROM users WHERE email=?",
            (data["email"],)
        ).fetchone()

    if not user or not bcrypt.checkpw(data["password"].encode(), user[4]):
        return jsonify({"error": "Invalid email or password"}), 401

    session["user_id"] = user[0]
    return jsonify({"success": True, "redirect": "/landing"})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "redirect": "/"})

@app.route("/api/me")
def me():
    if not require_auth():
        return jsonify({"error": "Not authenticated"}), 401
    with get_db() as db:
        user = db.execute(
            "SELECT id, first_name, last_name, email FROM users WHERE id=?",
            (session["user_id"],)
        ).fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"id": user[0], "firstName": user[1], "lastName": user[2], "email": user[3]})

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
