# LLM YouTube Landscape Tracker

This script fetches recent videos from a set of YouTube channels, tries to collect transcripts, and writes the results to `data.json`.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```powershell
.\.venv\Scripts\pip.exe install -r requirements.txt
```

3. Copy [`.env.example`](.env.example) to `.env` and fill in real values.

Required values:

```dotenv
GEMINI_API_KEY=your-key-or-leave-unused-if-you-switch-to-vertex
PROJECT_ID=your-gcp-project-id
VERTEX_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=absolute-or-relative-path-to-service_account.json
GEMINI_MODEL=gemini-2.5-flash
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
- Keep `.env`, `service_account.json`, and `.venv/` out of GitHub. The provided `.gitignore` already handles this.
- IMPORTANT: I found a `service_account.json` file in this repository. That file contains a service account private key and should NOT be committed. If you have already pushed it to a remote, rotate the key immediately and remove the file from the Git history (for example, use `git filter-branch` or the `bfg` tool). Steps:

	1. Revoke or delete the existing key in Google Cloud IAM and create a new key.
	2. Remove the file from git history (see https://rtyley.github.io/bfg-repo-cleaner/).
	3. Add the key to GitHub Secrets as `SERVICE_ACCOUNT_JSON` and do NOT commit the file.

- The repository workflow expects a secret named `SERVICE_ACCOUNT_JSON` (the full JSON content). The workflow writes that secret to `service_account.json` at runtime and sets `GOOGLE_APPLICATION_CREDENTIALS` for the job.
- If you prefer storing the secret base64-encoded, name it `SA_JSON_B64` and decode it in the workflow before writing.

- If you want, I can help rotate the key text and provide exact commands to purge the file from git history.
