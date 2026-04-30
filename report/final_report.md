# Final Report

## Project Title

Health AI Dashboard

## Summary

This project is a lightweight health-tracking dashboard that lets users record meals, sleep, and mood, then receive one short health suggestion based on recent entries. The application uses a React frontend for the dashboard and a Flask backend for local data storage and suggestion generation.

## Features

- Daily logging of meals, sleep, and mood
- Recent-history dashboard view
- Popup modal for full log history
- Local JSON data storage
- OpenAI-powered suggestion mode when `OPENAI_API_KEY` is configured
- Built-in fallback rules engine when OpenAI is not configured
- Subtle reset control for clearing stored logs

## Project Structure

- `code/` contains the backend, frontend, and helper scripts
- `data/` contains the persisted JSON log file
- `tests/` contains backend verification scripts
- `docs/` contains verification notes
- `report/` contains this final report

## Verification

- Backend API verified with `tests/test_backend_api.py`
- Frontend build verified with `npm run build` in `code/frontend`
