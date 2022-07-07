from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re
import requests
import os
from dotenv import load_dotenv
from fake_useragent import UserAgent
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from random import choice
import zipfile

######################################
# FORECAST SOURCES SCRAPER FUNCTIONS #
######################################
# !To provide a call function from Forecast template class method
# "scrap_all_forecasts" their names must be the same as in Database:
# table "datascraper_forecastsource", col:"id"
def rp5(start_datetime, url):

    # Scraping html content from source
    soup = get_soup(url)
    ftab = soup.find(id='ftab_content')

    # Parsing start date from source html page
    start_date_from_source = ftab.find(
        'span', class_="weekDay").get_text().split(',')[-1].split()
    start_date_from_source = func_start_date_from_source(
        month=month_rusname_to_number(start_date_from_source[1][:3]),
        day=int(start_date_from_source[0]),
        req_start_datetime=start_datetime
    )

    # Parsing time row from source
    time_row = ftab.find('tr', class_="forecastTime").find_all('td')[1:-1]
    time_row = [int(t.get_text()) for t in time_row]

    # Parsing weather parameters rows from source:
    # Temperature
    temp_row = ftab.find('a', class_='t_temperature')
    temp_row = temp_row.parent.parent.find_all('td')[1:-1]
    temp_row = [int(t.find('div', class_='t_0').get_text()) for t in temp_row]
    # Pressure
    press_row = ftab.find('a', class_='t_pressure')
    press_row = press_row.parent.parent.find_all('td')[1:-1]
    press_row = [
        int(t.find('div', class_='p_0').get_text()) for t in press_row]
    # Wind velocity
    wind_vel_row = ftab.find('a', class_='t_wind_velocity')
    wind_vel_row = wind_vel_row.parent.parent.find_all('td')[1:-1]
    wind_vel_row = [w.find('div', class_='wv_0') for w in wind_vel_row]
    wind_vel_row = [int(w.get_text()) if w else 0 for w in wind_vel_row]
    # Merge parameters from source into one tuple
    raw_data = (temp_row, press_row, wind_vel_row)

    return json_data_gen(
        start_datetime, start_date_from_source, time_row, raw_data)


def yandex(start_datetime, url):

    # Scraping html content from source
    soup = get_soup_selenium(url)
    ftab = soup.find('div', class_='sc-f83bbea-0 gyELnZ')
    # ftab = soup.find('li', class_='parameter-wrapper general-info__parameter').get_text()
    # ftab = soup.find('main').find_all('div', recursive=False)[1].find_all('article', recursive=False)
    # ftab = [f.find_all('div', recursive=False) for f in ftab]
    # ftab = [f.get_text() for f in ftab]
    # # ftab = ftab.findChildren('article', recursive=False)

    # Parsing start date from source html page
    start_datetime = start_datetime.replace(hour=9, minute=0, second=0,
                                            microsecond=0)  # Morning
    start_date_from_source = func_start_date_from_source(
        month=month_rusname_to_number(ftab.find(
            'span', class_='sc-b1913d4b-3 fEuQBg').get_text()),
        day=int(ftab.find(
            'span', class_='sc-b1913d4b-1 ePbffO').get_text()),
        req_start_datetime=start_datetime
    )


    # Parsing weather parameters rows from source:
    # Temperature
    temp_row = ftab.find_all('div', class_='sc-e9667f21-0 gKfmfO')
    temp_row = [t.div.get_text() for t in temp_row]
    # Conversion of the temperature of the form "+6...+8"
    # to the average value
    temp_row = [t.replace(chr(8722), '-').replace('°', '').split('...')
                for t in temp_row]
    temp_row = [[int(i) for i in t] for t in temp_row]
    temp_row = [int(round(sum(t)/len(t))) for t in temp_row]

    # Pressure
    ftab = ftab.find_all('div', class_='sc-e9667f21-0 hJBgFV')
    press_row = [int(p.get_text()) for p in ftab[1::5]]
    
    w = [f.div.prev_sibling for f in ftab[3::5]]
    pprint(w)
    return
    # Wind velocity
    wind_vel_row = ftab.find_all('span', class_="wind-speed")
    wind_vel_row = [int(round(float(w.get_text().replace(',', '.')), 0))
                    for w in wind_vel_row]
    # Merge parameters from source into one tuple
    raw_data = (temp_row, press_row, wind_vel_row)

    # Parsing time row from source
    time_row = [9, 15, 21, 3]*(len(temp_row)//4)

    return json_data_gen(
        start_datetime, start_date_from_source, time_row, raw_data)


def meteoinfo(start_datetime, url):

    # Scraping html content from source
    soup = get_soup(url)
    ftab = soup.find('div', class_='hidden-desktop')

    # Parsing start date from source html page
    start_datetime = start_datetime.replace(minute=0, second=0, microsecond=0)
    start_date_from_source = ftab.find('nobr')
    start_hour = start_date_from_source.parent.next_sibling.get_text()
    start_hour = 15 if start_hour.strip().lower() == 'день' else 3
    start_date_from_source = start_date_from_source.get_text()
    start_date_from_source = func_start_date_from_source(
        month=month_rusname_to_number(start_date_from_source),
        day=int(re.findall(r'\d+', start_date_from_source)[0]),
        req_start_datetime=start_datetime
    )

    # Parsing weather parameters rows from source:
    # Temperature
    temp_row = ftab.find_all('span', class_='fc_temp_short')
    temp_row = [int(t.get_text().rstrip('°')) for t in temp_row]
    # Wind velocity
    wind_vel_row = ftab.find_all('i')
    press_row = wind_vel_row[:]
    wind_vel_row = [int(w.parent.get_text()) for w in wind_vel_row]
    # Pressure
    press_row = [int(p.parent.next_sibling.get_text()) for p in press_row]

    # Parsing time row from source
    time, time_row = start_hour, []
    for t in temp_row:
        time_row.append(time)
        time = 15 if time == 3 else 3

    # Merge parameters from source into one tuple
    raw_data = (temp_row, press_row, wind_vel_row)

    return json_data_gen(
        start_datetime, start_date_from_source, time_row, raw_data)


def foreca(start_datetime, url: str):

    # Scraping html content from source first day page
    soup = get_soup(url)

    # print(soup)
    ftab = soup.find('div', class_='page-content')

    # Parsing start date from source html page
    start_date_from_source = ftab.find('div', class_='date').get_text().split()
    start_date_from_source = func_start_date_from_source(
        month=month_rusname_to_number(start_date_from_source[1][:3]),
        day=int(start_date_from_source[0]),
        req_start_datetime=start_datetime
    )

    # Parsing next days urls from source first day page
    domain = url[:url.find('/', 8)]
    next_days_urls = ftab.find('ul', class_='days').find_all('a')[1:]
    next_days_urls = [domain + nd.get('href') for nd in next_days_urls]
    # print(next_days_urls)

    # Scraping tables data to array
    ftabs = [ftab] + [get_soup(ndu).find('div', class_='page-content') for
                      ndu in next_days_urls]

    raw_data = [[] for i in range(4)]
    # Parsing from saved tables
    for ftab in ftabs:
        # Parsing time row from source
        ftab = ftab.find('div', class_='hourContainer')
        time_row = ftab.find_all('span', class_='time_24h')
        time_row = [int(t.get_text()) for t in time_row]
        raw_data[0].extend(time_row)

        # Parsing weather parameters rows from source pages:
        # Temperature
        temp_row = ftab.find_all('span', class_='t')
        temp_row = [int(t.find('span', class_='temp_c').
                        get_text()) for t in temp_row]
        raw_data[1].extend(temp_row)
        # Pressure
        press_row = ftab.find_all('span', class_='value pres pres_mmhg')
        press_row = [int(round(float(p.get_text()))) for p in press_row]
        raw_data[2].extend(press_row)
        # Wind velocity
        wind_vel_row = ftab.find_all('span', class_='windSpeed')
        wind_vel_row = [int(w.find('span', class_='value wind wind_ms').
                            get_text().split()[0]) for w in wind_vel_row]
        raw_data[3].extend(wind_vel_row)

    # for i in raw_data:
    #     print(i)

    return json_data_gen(
        start_datetime, start_date_from_source, raw_data[0], raw_data[1:])


########
# MISC #
########

# list of random proxies
proxies = []


def get_soup(url):
    """Scraping html content from source with the help of Selenium library"""
    global proxies

    if not proxies:
        get_proxies()

    headers = {'Accept': '*/*', 'User-Agent': UserAgent().random}

    proxy = proxies[datetime.now().day % len(proxies)]
    proxy = f'https://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}'
    # print(proxy)
    # try:

    response = requests.get(
        url=url,
        # url='https://yandex.ru/internet',
        headers=headers,
        # proxies=proxies,
        proxies={'https': proxy},
        timeout=10
    )

    src = response.text

    # with open('soup.html', 'w') as file:
    #     file.write(src)

    return BeautifulSoup(src, "lxml")

    # except Exception:
    #     print('Proxy ' + proxies[0] + ' deleted.')
    #     del proxies[0]


def get_proxies():
    """Scraping random proxy list"""
    print('get_proxies called!!!')
    global proxies
    load_dotenv()
    proxies = os.environ["PROXIES"].split('\n')
    proxies = [p.split(':') for p in proxies]


def func_start_date_from_source(month, day, req_start_datetime):
    """Calculate the starting date of the forecast source."""
    year = req_start_datetime.year
    # Processing the transition through the new year
    if req_start_datetime.month == 12 and month == 1:
        year += 1

    return datetime(year, month, day, tzinfo=req_start_datetime.tzinfo)


def month_rusname_to_number(name):
    """Translate russian month name to its number."""
    month_tuple = ('', 'янв', 'фев', 'мар', 'апр', 'мая', 'июн',
                   'июл', 'авг', 'сен', 'окт', 'ноя', 'дек')
    name = name.strip().lower().split(' ')[-1][:3]
    if name == 'май':
        return 5
    return month_tuple.index(name)


def intp_linear(xa, xc, xb, ya, yb):
    """Linear interpolation."""
    return round((xc-xa)/(xb-xa)*(yb-ya)+ya)


def json_data_gen(start_datetime, start_date_from_source,
                  time_row_from_source, raw_data):
    """Recalculating forecast data from source datetime row to required row."""

    # Generating datetime row from html source
    datetime_row_from_source = []
    for i, hour in enumerate(time_row_from_source):
        if i != 0 and hour < time_row_from_source[i-1]:
            start_date_from_source += timedelta(days=1)
        datetime_row_from_source.append(start_date_from_source
                                        + timedelta(hours=hour))

    # Generating json record
    data_json, datetime_ = [[] for i in raw_data], start_datetime
    datetime_step = timedelta(hours=6)
    # index = 0
    while datetime_ <= datetime_row_from_source[-1]:
        for i, dt in enumerate(datetime_row_from_source):
            if (i == 0 and datetime_ < dt) or dt - datetime_ >= datetime_step:
                [data_json[p].append(None) for p in range(len(raw_data))]
            elif datetime_ == dt:
                [data_json[j].append(p[i]) for j, p in enumerate(raw_data)]
            elif datetime_ < dt:
                [data_json[j].append(intp_linear(
                    datetime_row_from_source[i-1].timestamp(),
                    datetime_.timestamp(),
                    dt.timestamp(),
                    p[i-1],
                    p[i])) for j, p in enumerate(raw_data)]
            else:
                continue

            del datetime_row_from_source[:i]
            for p in range(len(raw_data)):
                del raw_data[p][:i]
            break

        datetime_ += datetime_step

    return data_json


############
# SELENIUM #
############


def get_soup_selenium(url):
    """Scraping html content from source with the help of Selenium library"""

    driver = init_selenium_driver()

    driver.get(url=url)
    # driver.get(url='https://yandex.ru/internet')
    time.sleep(1)
    src = driver.page_source

    driver.close()
    driver.quit()

    return BeautifulSoup(src, "lxml")


def init_selenium_driver():
    """Selenium driver initialization"""

    # create a new Service instance and specify path to Chromedriver executable
    service = ChromeService(executable_path=ChromeDriverManager().install())

    # create a ChromeOptions object
    options = webdriver.ChromeOptions()
    # run in headless mode
    options.add_argument("--headless=new")
    # disable the AutomationControlled feature of Blink rendering engine
    options.add_argument('--disable-blink-features=AutomationControlled')
    # disable pop-up blocking
    options.add_argument('--disable-popup-blocking')
    # start the browser window in maximized mode
    options.add_argument('--start-maximized')
    # disable extensions
    # # options.add_argument('--disable-extensions')
    # disable sandbox mode
    options.add_argument('--no-sandbox')
    # disable shared memory usage
    options.add_argument('--disable-dev-shm-usage')

    # proxy
    global proxies
    if not proxies:
        get_proxies()
    proxy = proxies[datetime.now().day % len(proxies)-4]

    proxies_extension = selenium_proxy(proxy[2], proxy[3], proxy[0], proxy[1])
    options.add_extension(proxies_extension)

    # Waits for page to be interactive
    options.page_load_strategy = 'eager'

    # create a driver instance
    driver = webdriver.Chrome(service=service, options=options)
    # Change the property value of the navigator for webdriver to undefined
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', \
                          {get: () => undefined})")

    # pass in selected user agent as an argument
    options.add_argument(f'user-agent={UserAgent().random}')

    # enable stealth mode
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    return driver


def selenium_proxy(username, password, endpoint, port):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxies",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };

    chrome.proxy.settings.set({
        value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (endpoint, port, username, password)

    extension = 'proxies_extension.zip'

    with zipfile.ZipFile(extension, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return extension
