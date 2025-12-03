from flask import Flask, render_template, request, redirect, session, jsonify
import json, os, hashlib

app = Flask(__name__)
app.secret_key = "super-secret"

DATA_FILE = "data.json"

# ---------- JSON HANDLING ----------
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


def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()


# ---------- SIGNUP ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]

        data = load_data()

        if email in data["users"]:
            return render_template("signup.html", error="User already exists")

        data["users"][email] = {
            "password": hash_pass(password),
            "attendance": {}   # <<<< FIXED KEY
        }
        save_data(data)

        return redirect("/login")

    return render_template("signup.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = hash_pass(request.form["password"])
        month = request.form["month"]

        data = load_data()

        if email in data["users"] and data["users"][email]["password"] == password:
            session["user"] = email
            session["month"] = month
            return redirect("/")

        return render_template("login.html", error="Invalid email/password")

    return render_template("login.html")


# ---------- HOME ----------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    return render_template("index.html", month=session["month"])


# ---------- SAVE (MAIN FIX HERE) ----------
@app.route("/save", methods=["POST"])
def save():
    if "user" not in session:
        return jsonify({"error": "Not logged in"})

    rec = request.get_json()

    date = rec.get("date")  # <<<< FIXED: ensure correct date
    if not date:
        return jsonify({"error": "Invalid date"}), 400

    user = session["user"]

    data = load_data()

    # FIXED: use correct key "attendance"
    if "attendance" not in data["users"][user]:
        data["users"][user]["attendance"] = {}

    # SAVE ENTRY
    data["users"][user]["attendance"][date] = rec
    save_data(data)

    return jsonify({"status": "ok"})


# ---------- LOAD ----------
@app.route("/load")
def load():
    if "user" not in session:
        return jsonify({"error": "Not logged in"})

    user = session["user"]

    data = load_data()
    att = data["users"][user].get("attendance", {})

    return jsonify({"data": att})


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
