from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests
from pprint import pprint

proxies = []  # Will contain proxies [ip, port]

def get_proxies():

    global proxies
    # Here I provide some proxies for not getting caught while scraping
    ua = UserAgent()  # From here we generate a random user agent

    headers = {'Accept': '*/*', 'User-Agent': ua.random}
    proxies_req = requests.get('https://www.sslproxies.org/', headers=headers)
    proxies_doc = proxies_req.text

    soup = BeautifulSoup(proxies_doc, 'html.parser')
    proxies_table = soup.find('table', class_='table table-striped table-bordered')

    # Save proxies in the array
    for row in proxies_table.tbody.find_all('tr'):
        proxies.append(':'.join(
            [td.get_text() for td in row.find_all('td')[:2]]))