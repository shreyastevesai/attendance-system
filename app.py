from flask import Flask, render_template, request, redirect, session, jsonify
import json, os, hashlib

app = Flask(__name__)
app.secret_key = "super-secret-session-key"

DATA_FILE = "data.json"


# ---------------------------------
# LOAD & SAVE JSON DATA
# ---------------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"users": {}}, f)

    with open(DATA_FILE, "r") as f:
        try:
            data = json.load(f)
        except:
            data = {"users": {}}

    if "users" not in data:
        data["users"] = {}
    return data


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()


# ---------------------------------
# LOGIN PAGE
# ---------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = hash_pass(request.form["password"])
        selected_month = request.form["month"]  # ⭐ MONTH SELECTED

        data = load_data()

        if email in data["users"] and data["users"][email]["password"] == password:
            session["user"] = email
            session["month"] = selected_month  # ⭐ SAVE MONTH IN SESSION
            return redirect("/")

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


# ---------------------------------
# SIGNUP PAGE
# ---------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = hash_pass(request.form["password"])

        data = load_data()

        if email in data["users"]:
            return render_template("signup.html", error="Email already exists!")

        data["users"][email] = {"password": hash_pass(password), "data": {}}
        save_data(data)

        return redirect("/login")

    return render_template("signup.html")


# ---------------------------------
# LOGOUT
# ---------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------------------------
# ATTENDANCE PAGE
# ---------------------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    month = session.get("month", "2025-12")
    return render_template("index.html", month=month)


# ---------------------------------
# SAVE ENTRY
# ---------------------------------
@app.route("/save", methods=["POST"])
def save():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    email = session["user"]
    rec = request.get_json()
    date = rec["date"]

    data = load_data()
    data["users"][email]["data"][date] = rec
    save_data(data)

    return jsonify({"ok": True})


# ---------------------------------
# LOAD USER DATA
# ---------------------------------
@app.route("/load")
def load():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    email = session["user"]
    data = load_data()

    return jsonify({"data": data["users"][email]["data"]})


if __name__ == "__main__":
    app.run(debug=True)
