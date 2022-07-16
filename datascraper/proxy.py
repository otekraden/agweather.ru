from dotenv import load_dotenv
import os
from datetime import datetime
from random import choice
from datascraper.logging import init_logger

# 0: no use proxy,
# 1: every day next from list,
# 2: random choice from list
PROXY_MODE = 0

proxies = []


def set_proxy():
    
    global PROXY_MODE

    logger = init_logger('Proxy setter')

    global proxies
    if not proxies:
        logger.debug("Proxies list red from .env file")
        logger.debug(f"Proxy mode is {PROXY_MODE}")
        load_dotenv()
        proxies = os.environ["PROXIES"].split('\n')
        proxies = [p.split(':') for p in proxies]

    if PROXY_MODE == 0:
        return None
    elif PROXY_MODE == 1:
        return proxies[datetime.now().day % len(proxies)]
    elif PROXY_MODE == 2:
        return choice(proxies)
