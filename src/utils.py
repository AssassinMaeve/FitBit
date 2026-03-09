import logging
import os
import yaml
from logging.handlers import RotatingFileHandler


def setup_logging(log_dir="logs"):
    """Configure logging with rotation and duplicate-handler prevention.

    Fix #17: 
    - Uses RotatingFileHandler (max 1MB, 3 backups) instead of unbounded file.
    - Checks for existing handlers to prevent duplicates on re-runs.
    - Adds a filter to suppress noisy matplotlib/seaborn UserWarnings.
    """
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger('')

    # Prevent duplicate handlers if setup_logging is called multiple times
    if logger.handlers:
        return

    logger.setLevel(logging.INFO)

    # File handler with rotation (max 1MB, keep 3 backups)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "pipeline.log"),
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    # Suppress matplotlib/seaborn internal noise
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def load_config(config_path="config/config.yaml"):
    """Load pipeline configuration from YAML."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def safe_filename(name):
    """Sanitize a string for use as a filename.

    Fix #20: Added <, >, |, " to the invalid character list,
    plus strips leading/trailing dots and spaces.
    """
    for ch in ['\\', '/', '*', '?', ':', '[', ']', '<', '>', '|', '"']:
        name = name.replace(ch, '_')
    # Strip leading/trailing dots and spaces (invalid on Windows)
    name = name.strip('. ')
    return name.lower()