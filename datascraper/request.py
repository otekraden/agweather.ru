import requests
from bs4 import BeautifulSoup
import re

html = requests.get('https://rp5.ru/%D0%90%D1%80%D1%85%D0%B8%D0%B2_%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D1%8B_%D0%B2_%D0%A1%D0%B0%D0%BD%D0%BA%D1%82-%D0%9F%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3%D0%B5')
html = html.text

# with open('test.html', 'w') as the_file:
#     the_file.write(html)

soup = BeautifulSoup(html, "lxml")

atab = soup.find('table', id='archiveTable')
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
