from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "code" / "backend"
DATA_FILE = REPO_ROOT / "data" / "data.json"
sys.path.insert(0, str(BACKEND_DIR))

from app import app  # noqa: E402


def reset_data() -> None:
    DATA_FILE.write_text(json.dumps({"users": []}, indent=2), encoding="utf-8")


def main() -> None:
    reset_data()
    client = app.test_client()

    health_response = client.get("/health")
    assert health_response.status_code == 200

    create_response = client.post(
        "/log",
        json={"meals": "oatmeal", "sleep": 7.5, "mood": "calm"},
    )
    assert create_response.status_code == 201

    list_response = client.get("/log")
    logs = list_response.get_json()
    assert list_response.status_code == 200
    assert len(logs) == 1

    suggest_response = client.post("/suggest")
    suggestion_payload = suggest_response.get_json()
    assert suggest_response.status_code == 200
    assert suggestion_payload["suggestion"]

    clear_response = client.delete("/log")
    assert clear_response.status_code == 200
    assert client.get("/log").get_json() == []

    print("Backend API verification passed.")


if __name__ == "__main__":
    main()
