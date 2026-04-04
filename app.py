import os
import ssl
import smtplib
import sqlite3
from email.mime.text import MIMEText
from flask import Flask, request, render_template, redirect, session

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "cases.db")

# ---------- Database ----------
def db():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            desc TEXT,
            file TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- Routes ----------
@app.route("/", methods=["GET", "HEAD"])
def home():
    if request.method == "HEAD":
        return "", 200
    return render_template("index.html")

@app.route("/report")
def report():
    return render_template("report.html")

@app.route("/about")
def about():
    return render_template("about.html")
    
    @app.route("/privacy")
def about():
    return render_template("privacy.html")
    
    @app.route("/terms")
def about():
    return render_template("terms.html")
    
@app.route("/submit", methods=["POST"])
def submit():
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        desc = request.form.get("desc")

        file = request.files.get("file")
        filename = file.filename if file else "No file uploaded"

        body = f"""
NEW FRAUD REPORT SUBMITTED

Name: {name}
Email: {email}
Phone: {phone}

Description:
{desc}

Uploaded File: {filename}
"""

        msg = MIMEText(body)
        msg["Subject"] = "New Fraud Report Submitted"
        msg["From"] = os.getenv("GMAIL_USER")
        msg["To"] = os.getenv("GMAIL_USER")

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_PASS"))
            server.send_message(msg)

        return "Report submitted successfully."

    except Exception as e:
        return f"Error submitting report: {str(e)}", 500

@app.route("/admin")
def admin():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    if request.form["user"] == "Adminlog" and request.form["pw"] == "PasswordSafe26":
        session["admin"] = True
        return redirect("/dashboard")
    return "Invalid login"

@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cases")
    rows = cur.fetchall()
    conn.close()

    return render_template("dashboard.html", cases=rows)
