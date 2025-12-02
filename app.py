from flask import Flask, render_template, request, jsonify
import json, os

app = Flask(__name__)

DATA_FILE = "data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/save", methods=["POST"])
def save():
    rec = request.get_json()
    date = rec["date"]

    data = load_data()
    data[date] = rec
    save_data(data)

    return jsonify({"ok": True})


@app.route("/load", methods=["GET"])
def load():
    data = load_data()
    return jsonify({"data": data})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
