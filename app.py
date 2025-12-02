from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import json, os, hashlib

app = Flask(__name__)
app.secret_key = "SuperSecretAttendanceKey"

DATA_FILE = "data.json"


def load_data():
    """Always return dict with at least {'users': {}}"""
    if not os.path.exists(DATA_FILE):
        base = {"users": {}}
        with open(DATA_FILE, "w") as f:
            json.dump(base, f, indent=4)
        return base

    with open(DATA_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}

    # Ensure top-level 'users' key exists and is a dict
    if "users" not in data or not isinstance(data["users"], dict):
        data["users"] = {}

    return data


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()


@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = hash_password(request.form["password"])

        data = load_data()
        user = data["users"].get(email)

        if user and user.get("password") == password:
            session["user"] = email
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = hash_password(request.form["password"])

        data = load_data()

        if email in data["users"]:
            return render_template("signup.html", error="Email already registered")

        # create empty data storage for this user
        data["users"][email] = {"password": password, "data": {}}
        save_data(data)

        return redirect(url_for("login_page"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


@app.route("/save", methods=["POST"])
def save():
    if "user" not in session:
        return jsonify({"error": "Not logged in!"}), 401

    rec = request.get_json()
    date = rec["date"]
    email = session["user"]

    data = load_data()

    # make sure user node exists
    if email not in data["users"]:
        data["users"][email] = {"password": hash_password("temp"), "data": {}}

    data["users"][email]["data"][date] = rec
    save_data(data)

    return jsonify({"ok": True})


@app.route("/load", methods=["GET"])
def load():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    email = session["user"]
    data = load_data()
    user = data["users"].get(email)

    if not user:
        return jsonify({"data": {}})

    return jsonify({"data": user.get("data", {})})


if __name__ == "__main__":
    # important for Render: use dynamic port
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
