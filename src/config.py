import os
from pathlib import Path

_DATA_DIR = Path("data")

LOG_FORMAT = '%(asctime)s:%(levelname)s:%(name)s:%(module)s:%(message)s'
LOG_DIR = Path(_DATA_DIR, "logs")
LOG_FILE_BOT = "bot.logs"
LOG_FILE_EDT = "edt.logs"

EDT_DIR = Path(_DATA_DIR, "edt")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(EDT_DIR, exist_ok=True)
