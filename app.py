from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import json, os, hashlib

app = Flask(__name__)
app.secret_key = "SuperSecretAttendanceKey"

DATA_FILE = "data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"users": {}}, f)
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {"users": {}}


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

        if user and user["password"] == password:
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
    data["users"][email]["data"][date] = rec
    save_data(data)

    return jsonify({"ok": True})


@app.route("/load", methods=["GET"])
def load():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    email = session["user"]
    data = load_data()
    return jsonify({"data": data["users"][email]["data"]})


if __name__ == "__main__":
    app.run(debug=True)
