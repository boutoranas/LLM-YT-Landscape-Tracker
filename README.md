# LLM YouTube Landscape Tracker

This script fetches recent videos from a set of YouTube channels, tries to collect transcripts, and writes the results to `data.json`.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```powershell
.\.venv\Scripts\pip.exe install -r requirements.txt
```

3. Put your credentials in `.env`.

Required values:

```dotenv
PROJECT_ID=your-gcp-project-id
GEMINI_API_KEY=your-key-or-leave-unused-if-you-switch-to-vertex
SERVICE_ACCOUNT=service_account.json
```

## Run locally

```powershell
.\.venv\Scripts\python.exe tracker.py
```

## Upload to GitHub

1. Make sure `.env`, `service_account.json`, and `.venv/` stay untracked. The provided `.gitignore` already handles this.
2. Initialize the repo if needed:

```powershell
git init
git add .
git commit -m "Initial tracker"
```

3. Create an empty GitHub repository, then add the remote and push:

```powershell
git remote add origin https://github.com/<your-username>/<your-repo>.git
git branch -M main
git push -u origin main
```

## Run periodically on Windows

Use Task Scheduler and point it at `run_tracker.ps1`.

Suggested action:

```powershell
powershell.exe -ExecutionPolicy Bypass -File "C:\Users\DELL 7430\Documents\LLM_YT_landscape_tracker\run_tracker.ps1"
```

Set the trigger to whatever interval you want, for example daily or every 6 hours.

## Notes

- `data.json` is the output file.
- If you want the script to use Vertex AI instead of an API key, keep `GOOGLE_APPLICATION_CREDENTIALS` pointing at your service-account JSON and make sure the Vertex project has the right roles and billing.
- I did not see anything named `openclaw` in this repo. If you meant a specific provider or feature, tell me the exact name and I can wire it in.
