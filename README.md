# Smart Governance

A decision-intelligence platform for citizen complaints in Hyderabad, Telangana. The FastAPI backend classifies complaints, estimates severity, and helps citizens and department officers follow their progress.

## Features

- Citizen complaint submission and status tracking.
- DistilBERT complaint-category classification.
- XGBoost severity scoring and decision recommendations.
- SHAP explanations for model predictions.
- Officer login, complaint review, and decision recording.
- Static HTML, CSS, and JavaScript frontend served by FastAPI.

## Requirements

- Python 3.10 or newer.
- Git LFS for the DistilBERT model weights (`.safetensors`).

## Setup (Windows PowerShell)

Clone the repository after installing Git and Git LFS:

```powershell
git lfs install
git clone https://github.com/aravinderik06/A-Decision-Intelligence-Platform-for-Smart-Governance.git
cd A-Decision-Intelligence-Platform-for-Smart-Governance
git lfs pull

py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Set a unique JWT signing key in the current PowerShell session. Do not commit it or put it in a tracked file:

```powershell
$env:SMART_GOVERNANCE_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Create a fresh local database and its tables:

```powershell
python -m src.database
```

Optionally create the department officer accounts. Set and confirm a unique password for each account when prompted:

```powershell
python src\create_officers.py
```

Start the API and frontend:

```powershell
python -m uvicorn src.main:app --reload
```

Open <http://127.0.0.1:8000/> for the citizen site and <http://127.0.0.1:8000/docs> for the API documentation. The JWT signing key must be set each time the API is started.

## Project layout

- `src/` — API, database setup, model inference, and training/preparation scripts.
- `frontend/` — static citizen and officer web pages.
- `data/` — model-training and evaluation datasets; the local SQLite database is ignored by Git.
- `models/` — trained model artifacts. The DistilBERT `.safetensors` weights are stored with Git LFS.
- `results/` — model evaluation metrics.
