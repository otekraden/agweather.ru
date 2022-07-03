import requests
from bs4 import BeautifulSoup
import re
import time

# url = 'https://rp5.ru/%D0%90%D1%80%D1%85%D0%B8%D0%B2_%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D1%8B_%D0%B2_%D0%A1%D0%B0%D0%BD%D0%BA%D1%82-%D0%9F%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3%D0%B5'
# url = 'https://rp5.ru/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B5_(%D0%92%D0%94%D0%9D%D0%A5)'
url = 'https://rp5.ru/%D0%90%D1%80%D1%85%D0%B8%D0%B2_%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D1%8B_%D0%B2_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B5_(%D0%92%D0%94%D0%9D%D0%A5)'
# url = 'https://rp5.ru/%D0%90%D1%80%D1%85%D0%B8%D0%B2_%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D1%8B_%D0%B2_%D0%A1%D0%B8%D0%B4%D0%BD%D0%B5%D0%B5_(%D0%B0%D1%8D%D1%80%D0%BE%D0%BF%D0%BE%D1%80%D1%82)'
# url = 'https://rp5.ru/%D0%90%D1%80%D1%85%D0%B8%D0%B2_%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D1%8B_%D0%B2_%D0%98%D1%81%D1%82-%D0%AD%D0%BB%D0%BC%D1%85%D0%B5%D1%80%D1%81%D1%82%D0%B5_(%D0%B0%D1%8D%D1%80%D0%BE%D0%BF%D0%BE%D1%80%D1%82)'


headers = {
    'Accept': '*/*',
    'Referer': 'https://rp5.ru/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/\
        537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

payload = {
    'ArchDate': '10.03.2023',
    'pe': '30',
}

response = requests.post(
    url=url,
    # cookies=cookies,
    headers=headers,
    data=payload
)

html = response.text

# print(html)


# req1 = requests.get(url=url)

# print(req1.cookies)
# print(req1.headers)

# # html = requests.post(url=url)
# html = requests.post(url=url, cookies=req1.cookies, headers=req1.headers, data=payload)
# html = html.text

# print(html)


time.sleep(1)
soup = BeautifulSoup(html, 'lxml')

# for s in soup:
#     print(s)

# with open('msk.html', 'w') as the_file:
#     the_file.write(html)
# print(soup)
time.sleep(1)
print(len(html))
atab = soup.find('table', id='archiveTable')
# atab = soup.find('div', id='divSynopArchive')
atab = atab.find_all('tr')[1:]
atab = [row.find_all('td')[-29:] for row in atab]


for i, row in enumerate(atab):
    time = int(row[0].get_text())

    temp = row[1].find('div', class_='t_0 dfs')
    temp = float(temp.get_text()) if temp else None

    press = row[2].find('div', class_='p_0 dfs')
    press = float(press.get_text()) if press else None
    wind_vel = row[7].find('div', class_='wv_0')
    wind_vel = wind_vel.get_text() if wind_vel else None
    wind_vel = int(re.findall(r'\d+', wind_vel)[0]) \
        if wind_vel else 0
    record = [time, temp, press, wind_vel]

    print(record)
