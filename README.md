# Health AI Dashboard

## Project Overview and Purpose

Health AI Dashboard is a lightweight health-tracking application for quickly logging meals, sleep, and mood, then receiving a short health suggestion based on recent entries. The project is designed as a simple local dashboard with a React frontend and a Flask backend.

## Repository Structure

- `code/` source code for the backend, frontend, and helper scripts
- `data/` persisted log data used by the backend
- `tests/` verification scripts for the backend API
- `docs/` supporting verification notes
- `report/` final report document
- `README.md` project overview, setup, and usage instructions

## Installation and Setup Instructions

### Backend

```bash
cd code/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The backend runs on `http://127.0.0.1:5050`.

### Frontend

```bash
cd code/frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173`.

## How to Run the Program and Reproduce Results

1. Start the Flask backend from `code/backend`.
2. Start the Vite frontend from `code/frontend`.
3. Open the local frontend URL shown by Vite.
4. Add health log entries with meals, sleep, and mood.
5. Click `Get Suggestion` to generate a recommendation.
6. Use the subtle `Reset` control in the history area if you want to clear stored logs.

### Reproducing Stored Data Behavior

The app stores logs in:

- [data/data.json](/Users/timothypark/repos/health-ai/data/data.json)

To reset manually, replace its contents with:

```json
{
  "users": []
}
```

## Testing and Verification

### Backend API Verification

```bash
cd code/backend
.venv/bin/python ../../tests/test_backend_api.py
```

### Frontend Build Verification

```bash
cd code/frontend
npm run build
```

## Technologies and Libraries Used

### Backend

- Python
- Flask
- Flask-CORS
- OpenAI Python SDK

### Frontend

- React
- Vite
- Recharts

## Suggestion Engine Behavior

- If `OPENAI_API_KEY` is set, `POST /suggest` uses OpenAI.
- If no API key is configured, the app falls back to a built-in local rules engine.

## Author(s) and Contribution Summary

- Repository project author: update this line with your name if needed for submission.
- Development assistance in this working session included code, UI, and documentation updates across the backend, frontend, test scaffolding, and repository restructuring.
