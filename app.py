from flask import Flask, render_template, request, redirect, session, jsonify
import json, os, hashlib

app = Flask(__name__)
app.secret_key = "super-secret-key"

DATA_FILE = "data.json"


# ------------------- JSON HANDLING -------------------
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


# ------------------- SIGNUP -------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]

        data = load_data()

        # IF USER EXISTS
        if email in data["users"]:
            return render_template("signup.html", error="Email already registered!")

        # CREATE NEW USER
        data["users"][email] = {
            "password": hash_pass(password),
            "data": {}
        }
        save_data(data)

        return redirect("/login")

    return render_template("signup.html")


# ------------------- LOGIN -------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = hash_pass(request.form["password"])
        selected_month = request.form["month"]

        data = load_data()

        if email in data["users"] and data["users"][email]["password"] == password:
            session["user"] = email
            session["month"] = selected_month
            return redirect("/")

        return render_template("login.html", error="Wrong email or password!")

    return render_template("login.html")


# ------------------- FORGOT PASSWORD -------------------
@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form["email"].lower()

        data = load_data()

        if email not in data["users"]:
            return render_template("forgot.html", error="Email not found!")

        # Reset password
        new_password = "123456"  # Default reset
        data["users"][email]["password"] = hash_pass(new_password)

        save_data(data)

        msg = f"Your new password is: {new_password}"
        return render_template("forgot.html", success=msg)

    return render_template("forgot.html")


# ------------------- LOGOUT -------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ------------------- HOME -------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html", month=session["month"])


# ------------------- SAVE ENTRY -------------------
@app.route("/save", methods=["POST"])
def save():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user = session["user"]
    rec = request.get_json()
    date = rec["date"]

    data = load_data()

    data["users"][user]["data"][date] = rec
    save_data(data)

    return jsonify({"ok": True})


# ------------------- LOAD ENTRY -------------------
@app.route("/load")
def load():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user = session["user"]
    data = load_data()

    return jsonify({"data": data["users"][user]["data"]})


if __name__ == "__main__":
    app.run(debug=True)
