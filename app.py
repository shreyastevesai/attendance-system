from flask import Flask, render_template, request, redirect, session, jsonify
import json, os, hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super-secret"

DATA_FILE = "data.json"


# ---------------- JSON HELPERS -----------------

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


# ---------------- SIGNUP -----------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]

        data = load_data()

        if email in data["users"]:
            return render_template("signup.html", error="User exists")

        data["users"][email] = {
            "password": hash_pass(password),
            "attendance": {}
        }
        save_data(data)
        return redirect("/login")

    return render_template("signup.html")


# ---------------- LOGIN -----------------

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

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# ---------------- HOME / INDEX -----------------

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    return render_template("index.html", month=session["month"])


# ---------------- CHANGE MONTH -----------------

@app.route("/change_month", methods=["POST"])
def change_month():
    session["month"] = request.form["month"]
    return jsonify({"status": "ok"})


# ---------------- SAVE ATTENDANCE -----------------

@app.route("/save", methods=["POST"])
def save():
    if "user" not in session:
        return jsonify({"error": "Not logged in"})

    rec = request.get_json()
    date = rec["date"]
    user = session["user"]

    data = load_data()

    if "attendance" not in data["users"][user]:
        data["users"][user]["attendance"] = {}

    # SAVE ENTRY
    data["users"][user]["attendance"][date] = rec

    # --------- KEEP ONLY LAST 6 MONTHS --------------
    dates = sorted(data["users"][user]["attendance"].keys())
    all_months = sorted(list({d[:7] for d in dates}))

    if len(all_months) > 6:
        delete_months = all_months[:-6]
        for d in dates:
            if d[:7] in delete_months:
                del data["users"][user]["attendance"][d]

    save_data(data)
    return jsonify({"status": "ok"})


# ---------------- LOAD ATTENDANCE -----------------

@app.route("/load")
def load():
    if "user" not in session:
        return jsonify({"error": "Not logged in"})
    user = session["user"]

    data = load_data()
    return jsonify({"data": data["users"][user]["attendance"]})


# ---------------- FORGOT PASSWORD -----------------

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form["email"].lower()
        data = load_data()

        if email not in data["users"]:
            return render_template("forgot.html", error="Email not found")

        new_pass = "123456"
        data["users"][email]["password"] = hash_pass(new_pass)
        save_data(data)

        return render_template("forgot.html", success=f"New password: {new_pass}")

    return render_template("forgot.html")


# ---------------- LOGOUT -----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- RUN APP -----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
