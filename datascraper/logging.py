import logging
import sys
import tg_logger
from dotenv import load_dotenv
import os
from pathlib import Path


def init_logger(name):
    """Initialization logger for all applications."""

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(name)s: %(message)s")

    # logging to Terminal
    stream_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(stream_handler)
    stream_handler.setFormatter(formatter)

    # logging to *.log File
    BASE_DIR = Path(__file__).resolve().parent.parent
    file_handler = logging.FileHandler(BASE_DIR / "datascraper.log")
    logger.addHandler(file_handler)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    # file_handler.setLevel(logging.DEBUG)

    # logging to Telegram
    load_dotenv()
    token = os.environ["TELEGRAM_TOKEN"]
    users = os.environ["TELEGRAM_USERS"].split('\n')
    telegram_handler = tg_logger.setup(logger, token=token, users=users)
    # telegram_handler.setLevel(logging.CRITICAL)
    telegram_handler.setLevel(logging.INFO)

    return logger
