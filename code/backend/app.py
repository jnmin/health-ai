import json
import os
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent
DATA_FILE = REPO_ROOT / "data" / "data.json"
DEFAULT_USER_ID = "default-user"

app = Flask(__name__)
CORS(app)


def normalize_text(value):
    return str(value).strip()


def ensure_data_file():
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps({"users": []}, indent=2))


def load_data():
    ensure_data_file()
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data):
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def get_or_create_user(data, user_id=DEFAULT_USER_ID):
    for user in data["users"]:
        if user["id"] == user_id:
            return user

    user = {"id": user_id, "log": []}
    data["users"].append(user)
    return user


def build_basic_suggestion(entries):
    latest_entry = entries[-1]
    sleep_values = [entry["sleep"] for entry in entries if isinstance(entry.get("sleep"), (int, float))]
    avg_sleep = sum(sleep_values) / len(sleep_values) if sleep_values else latest_entry["sleep"]
    mood_text = latest_entry["mood"].lower()
    meals_text = latest_entry["meals"].lower()

    if latest_entry["sleep"] < 6 or avg_sleep < 6.5:
        return (
            "Your sleep has been a little low. Aim for an earlier wind-down tonight and try to get at least 7 hours."
        )

    low_energy_words = ["tired", "stressed", "anxious", "overwhelmed", "drained", "low"]
    if any(word in mood_text for word in low_energy_words):
        return (
            "Your recent mood sounds strained. Keep tomorrow simple: drink water early, get a short walk, and plan one real break."
        )

    meal_quality_words = ["skip", "skipped", "snack", "chips", "fast food", "takeout", "soda"]
    if any(word in meals_text for word in meal_quality_words):
        return (
            "Your meals look a bit inconsistent. A simple next step is to add one balanced meal with protein, fiber, and water."
        )

    if latest_entry["sleep"] >= 7 and any(word in mood_text for word in ["good", "calm", "great", "focused", "happy"]):
        return (
            "You seem to be in a solid groove. Keep the same sleep routine and repeat the meals that helped you feel steady."
        )

    return (
        "A good next step is to keep tomorrow consistent: eat regular meals, get some movement, and protect your sleep schedule."
    )


def generate_suggestion(entries):
    recent_entries = entries[-5:]
    fallback_suggestion = build_basic_suggestion(recent_entries)
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {
            "suggestion": fallback_suggestion,
            "source": "basic-local-engine",
        }

    summary_lines = [
        f"{entry['date']}: meals={entry['meals']}, sleep={entry['sleep']} hours, mood={entry['mood']}"
        for entry in recent_entries
    ]
    prompt = (
        "You are a helpful health coach. Based on the recent health log below, "
        "give one short, specific, actionable health tip.\n\nRecent log:\n"
        + "\n".join(summary_lines)
    )

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )
        suggestion = response.output_text.strip()
        if suggestion:
            return {"suggestion": suggestion, "source": "openai"}
    except Exception:
        pass

    return {
        "suggestion": fallback_suggestion,
        "source": "basic-local-engine",
    }


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"ok": True})


@app.route("/log", methods=["GET"])
def get_log():
    data = load_data()
    user = get_or_create_user(data)
    save_data(data)
    return jsonify(user["log"])


@app.route("/log", methods=["POST"])
def add_log():
    payload = request.get_json(silent=True) or {}
    meals = normalize_text(payload.get("meals", ""))
    sleep = payload.get("sleep")
    mood = normalize_text(payload.get("mood", ""))

    if not meals or sleep is None or not mood:
        return jsonify({"error": "meals, sleep, and mood are required"}), 400

    try:
        sleep_value = float(sleep)
    except (TypeError, ValueError):
        return jsonify({"error": "sleep must be a number"}), 400

    if sleep_value < 0:
        return jsonify({"error": "sleep must be zero or higher"}), 400

    entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "meals": meals,
        "sleep": sleep_value,
        "mood": mood,
    }

    data = load_data()
    user = get_or_create_user(data)
    user["log"].append(entry)
    save_data(data)

    return jsonify(entry), 201


@app.route("/log", methods=["DELETE"])
def clear_log():
    data = load_data()
    user = get_or_create_user(data)
    user["log"] = []
    save_data(data)
    return jsonify({"ok": True})


@app.route("/suggest", methods=["POST"])
def suggest():
    data = load_data()
    user = get_or_create_user(data)
    recent_entries = user["log"][-5:]

    if not recent_entries:
        return jsonify(
            {
                "suggestion": "Add a few health logs first so I can suggest something useful.",
                "source": "basic-local-engine",
            }
        )

    return jsonify(generate_suggestion(recent_entries))


if __name__ == "__main__":
    ensure_data_file()
    debug_enabled = os.getenv("FLASK_DEBUG") == "1"
    app.run(debug=debug_enabled, host="127.0.0.1", port=5050)
