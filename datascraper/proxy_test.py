import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/\
        537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

load_dotenv()
PROXY = os.environ["PROXY"]
proxies = {
    'https': PROXY
}


def get_location(url):
    response = requests.get(
        url=url,
        headers=headers,
        proxies=proxies
        )

    soup = BeautifulSoup(response.text, 'lxml')

    table = soup.find('table', class_='table').find_all('td')
    table = [td.get_text() for td in table]
    ip = table[1]
    location = f"{table[7]}, {table[9]}"
    print(f'IP: {ip}\nLocation: {location}')


def main():
    get_location(url='https://www.ipaddress.my/')


if __name__ == '__main__':
    main()
