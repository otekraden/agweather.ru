from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests

proxies = []  
def get_proxies():
    print('get_proxies called!!!')
    headers = {'Accept': '*/*', 'User-Agent': UserAgent().random}
    proxies_req = requests.get('https://www.sslproxies.org/', headers=headers)
    proxies_doc = proxies_req.text
    soup = BeautifulSoup(proxies_doc, 'html.parser')
    proxies_table = soup.find('table', class_='table table-striped table-bordered')

    for row in proxies_table.tbody.find_all('tr'):
        proxies.append(':'.join(
            [td.get_text() for td in row.find_all('td')[:2]]))

def main():

    for n in range(1, 20):

        if not proxies:
            get_proxies()

        # From here we generate a random user agent
        headers = {'Accept': '*/*', 'User-Agent': UserAgent().random}

        try:
            req = requests.get('http://icanhazip.com',
                               headers=headers,
                               proxies={'http': proxies[0]},
                               timeout=10
                               )
            print(req.status_code)
            my_ip = req.text
            print('#' + str(n) + ': ' + my_ip)

        except Exception:  # If error, delete this proxy and find another one
            print('Proxy ' + proxies[0] + ' deleted.')
            del proxies[0]

if __name__ == '__main__':
    main()
