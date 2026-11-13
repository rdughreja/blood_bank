# Run Phase 1 in GitHub Codespaces (no local install)

Nothing runs on your laptop. Python, Node, Postgres and Redis all run in
GitHub's cloud. Free tier is enough for Phase 1.

## 1. Push this repo to GitHub (once)

From your local copy, in PowerShell:

```powershell
cd C:\Users\codes\OneDrive\Desktop\blood-bank-phase1\blood-bank
git init
git add .
git commit -m "blood bank phase 1 + codespaces setup"
git branch -M main
git remote add origin https://github.com/rdughreja/blood-bank.git
git push -u origin main
```

If the repo `rdughreja/blood-bank` doesn't exist yet, create it first at
https://github.com/new — empty repo, no README, no .gitignore, no licence —
then run the push above. GitHub will ask you to sign in in the browser.

## 2. Create the Codespace

1. Open https://github.com/rdughreja/blood-bank in your browser.
2. Click the green **Code** button → **Codespaces** tab → **Create codespace on main**.
3. Wait 3–5 minutes. The first build installs Python deps, Node deps,
   runs `alembic upgrade head` and `python seed.py`, then starts the API
   and the frontend automatically (see `.devcontainer/setup.sh` and
   `.devcontainer/start.sh`).

## 3. Open the app

- VS Code in the browser will offer the forwarded **port 3000** — click it,
  or go to the **Ports** tab and open the 3000 row.
- Log in: `admin@bloodbank.local` / `Admin@123456` (dev-only seed, change it
  before any real use).

## If it doesn't start

In the Codespace terminal:

```bash
bash .devcontainer/setup.sh
bash .devcontainer/start.sh
tail -50 /tmp/api.log
tail -50 /tmp/web.log
```

Paste those logs to Muse. Do not re-run `seed.py` before `alembic upgrade head`
— that order is what created the half-built tables on Windows.
