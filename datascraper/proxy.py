from dotenv import load_dotenv
import os
from datetime import datetime
from random import choice
from datascraper.logging import init_logger


def set_proxy():

    logger = init_logger('Proxy setter')

    load_dotenv()
    PROXIES = os.environ["PROXIES"].split('\n')
    PROXIES = [p.split(':') for p in PROXIES]
    logger.debug("Proxies list red from .env file")

    PROXY_MODE = int(os.environ["PROXY_MODE"])
    logger.debug(f"Proxy mode red from .env file: {PROXY_MODE}")

    if PROXY_MODE == 0:
        return None
    elif PROXY_MODE == 1:
        return PROXIES[datetime.now().day % len(PROXIES)]
    elif PROXY_MODE == 2:
        return choice(PROXIES)
