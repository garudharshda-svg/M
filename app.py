from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Gemini imports
from google import genai
from dotenv import load_dotenv
import os


# ---------------------------------
# LOAD ENVIRONMENT VARIABLES
# ---------------------------------

load_dotenv()


# ---------------------------------
# FLASK APP
# ---------------------------------

app = Flask(__name__)

DATABASE = "users.db"


# ---------------------------------
# GEMINI SETUP
# ---------------------------------

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ---------------------------------
# DATABASE SETUP
# ---------------------------------

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------
# WELCOME / HOME PAGE
# ---------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------
# SIGN UP
# ---------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        fullname = request.form["fullname"].strip()
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Check password confirmation
        if password != confirm_password:
            return "Passwords do not match."

        # Hash the password before saving it
        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO users
                (fullname, username, email, password)
                VALUES (?, ?, ?, ?)
            """, (
                fullname,
                username,
                email,
                hashed_password
            ))

            conn.commit()
            conn.close()

            # Successful signup -> go to Sign In
            return redirect(url_for("signin"))

        except sqlite3.IntegrityError:
            return "Username or email already exists."

    return render_template("signup.html")


# ---------------------------------
# SIGN IN
# ---------------------------------

@app.route("/signin", methods=["GET", "POST"])
def signin():

    if request.method == "POST":

        username_or_email = request.form["username_or_email"].strip()
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, fullname, username, email, password
            FROM users
            WHERE username = ? OR email = ?
        """, (
            username_or_email,
            username_or_email
        ))

        user = cursor.fetchone()

        conn.close()

        # User does not exist
        if user is None:
            return "User not found."

        # Password stored in the database
        stored_password = user[4]

        # Check entered password against hashed password
        if check_password_hash(stored_password, password):

            # Successful signin -> go to index.html
            return redirect(url_for("home"))

        return "Incorrect password."

    return render_template("signin.html")


# ---------------------------------
# CHAT WITH GEMINI
# ---------------------------------

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_message = data.get("message", "").strip()

    # Don't send an empty message to Gemini
    if not user_message:
        return jsonify({
            "error": "Message cannot be empty."
        }), 400

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=user_message
        )

        return jsonify({
            "response": response.text
        })

    except Exception as e:

        print("Gemini API Error:", e)

        return jsonify({
            "error": "Something went wrong while contacting Gemini."
        }), 500


# ---------------------------------
# START APPLICATION
# ---------------------------------

if __name__ == "__main__":
    init_db()
    app.run(debug=True)