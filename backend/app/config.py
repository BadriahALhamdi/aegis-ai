from pathlib import Path

# ==============================
# Project Directories
# ==============================

# backend/
BASE_DIR = Path(__file__).resolve().parent.parent

# backend/app/
APP_DIR = BASE_DIR / "app"

# backend/storage/
STORAGE_DIR = BASE_DIR / "storage"

# backend/storage/uploads/
UPLOAD_DIR = STORAGE_DIR / "uploads"

# backend/storage/results/
RESULTS_DIR = STORAGE_DIR / "results"

# backend/storage/models/
MODELS_DIR = STORAGE_DIR / "models"

# ==============================
# Create directories automatically
# ==============================

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)