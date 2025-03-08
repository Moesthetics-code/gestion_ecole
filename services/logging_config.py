import logging
import logging.config
import os
from datetime import datetime

# Création du dossier logs si inexistant
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Définition du niveau de logging par défaut
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Format de log en JSON
LOG_FORMAT = (
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
    '"service": "%(name)s", "message": "%(message)s"}'
)

# Configuration du logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"format": LOG_FORMAT, "datefmt": "%Y-%m-%d %H:%M:%S"},
        "standard": {"format": "[%(asctime)s] %(levelname)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "level": LOG_LEVEL,
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "json",
            "filename": os.path.join(LOG_DIR, f"log_{datetime.now().date()}.log"),
            "mode": "a",
            "level": LOG_LEVEL,
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": LOG_LEVEL,
    },
}

def setup_logging():
    """Initialise la configuration du logging"""
    logging.config.dictConfig(LOGGING_CONFIG)
