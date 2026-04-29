# health-ai

A simple health tracker with a React frontend and Flask backend.

## Structure

- `backend/` Flask API with local JSON storage in `backend/data.json`
- `frontend/` React app built with Vite and Recharts

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The Flask API runs on `http://localhost:5000`.

If `OPENAI_API_KEY` is set, `POST /suggest` uses OpenAI. If not, the backend falls back to a simple built-in suggestion engine.

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The React app runs on `http://localhost:5173`.

Vite proxies `/api/*` to the Flask backend during local development.

## API endpoints

- `GET /log` returns the default user's health log
- `POST /log` accepts `{ "meals": "...", "sleep": 7.5, "mood": "..." }`
- `POST /suggest` returns one actionable health tip from OpenAI when configured, or a basic local rules engine otherwise
