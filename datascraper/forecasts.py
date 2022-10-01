from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re
import requests
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import zipfile
from datascraper.proxy import set_proxy
from datascraper.logging import init_logger


######################################
# FORECAST SOURCES SCRAPER FUNCTIONS #
######################################
# !To provide a call function from Forecast template class method
# "scrap_forecasts" their names must be the same as in Database:
# table "datascraper_forecastsource", col:"id"
def rp5(start_forecast_datetime, url):

    # Scraping html content from source
    soup = get_soup(url)
    ftab = soup.find(id='ftab_content')

    # Parsing start date from source html page
    start_date_from_source = ftab.find(
        'span', class_="weekDay").get_text().split(',')[-1].split()
    start_date_from_source = func_start_date_from_source(
        month=month_rusname_to_number(start_date_from_source[1][:3]),
        day=int(start_date_from_source[0]),
        req_start_datetime=start_forecast_datetime
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

    return generate_forecasts(
        start_forecast_datetime,
        start_date_from_source,
        time_row,
        list(zip(temp_row, press_row, wind_vel_row)))


def yandex(start_forecast_datetime, url):

    # Scraping html content from source
    def get_ftab():
        soup = get_soup_selenium(url)
        return soup.find('main').find_all('div', recursive=False)[1]

    try:
        ftab = get_ftab()
    except AttributeError:
        ftab = get_ftab()

    ftab = ftab.find_all('article', recursive=False)

    # Parsing start date from source html page
    date_tags = ftab[0].find('p').find_all('span')

    start_date_from_source = func_start_date_from_source(
        month=month_rusname_to_number(date_tags[2].get_text()),
        day=int(date_tags[0].get_text()),
        req_start_datetime=start_forecast_datetime
    )

    ftab = [day.find_all('div', recursive=False)[:6*4] for day in ftab]
    ftab = sum(ftab, [])

    # Parsing weather parameters rows from source:
    # Temperature
    temp_row = [t.div.next_sibling for t in ftab[::6]]
    # Conversion of the temperature of the form "+6...+8"
    # to the average value
    temp_row = [t.replace(chr(8722), '-').replace('°', '').split('...')
                for t in temp_row]
    temp_row = [[int(i) for i in t] for t in temp_row]
    temp_row = [sum(t)/len(t) for t in temp_row]

    # Pressure
    press_row = [int(p.get_text()) for p in ftab[2::6]]

    # Wind velocity
    wind_vel_row = [w.contents[0].replace(',', '.') for w in ftab[4::6]]
    wind_vel_row = [float(w) for w in wind_vel_row]

    # Parsing time row from source
    time_row = [9, 15, 21, 3]*(len(temp_row)//4)

    return generate_forecasts(
        start_forecast_datetime,
        start_date_from_source,
        time_row,
        list(zip(temp_row, press_row, wind_vel_row)))


def meteoinfo(start_forecast_datetime, url):

    # Scraping html content from source
    soup = get_soup(url)
    ftab = soup.find('div', class_='hidden-desktop')

    # Parsing start date from source html page
    start_date_from_source = ftab.find('nobr')
    start_hour = start_date_from_source.parent.next_sibling.get_text()
    start_hour = 15 if start_hour.strip().lower() == 'день' else 3
    start_date_from_source = start_date_from_source.get_text()
    start_date_from_source = func_start_date_from_source(
        month=month_rusname_to_number(start_date_from_source),
        day=int(re.findall(r'\d+', start_date_from_source)[0]),
        req_start_datetime=start_forecast_datetime
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

    return generate_forecasts(
        start_forecast_datetime,
        start_date_from_source,
        time_row,
        list(zip(temp_row, press_row, wind_vel_row)))


def foreca(start_forecast_datetime, url: str):

    # Scraping html content from source first day page
    soup = get_soup(url)

    # print(soup)
    ftab = soup.find('div', class_='page-content')

    # Parsing start date from source html page
    start_date_from_source = ftab.find('div', class_='date').get_text().split()
    start_date_from_source = func_start_date_from_source(
        month=month_rusname_to_number(start_date_from_source[1][:3]),
        day=int(start_date_from_source[0]),
        req_start_datetime=start_forecast_datetime
    )

    # Parsing next days urls from source first day page
    domain = url[:url.find('/', 8)]
    next_days_urls = ftab.find('ul', class_='days').find_all('a')[1:]
    next_days_urls = [domain + nd.get('href') for nd in next_days_urls]
    # print(next_days_urls)

    # Scraping tables data to array
    ftabs = [ftab] + [get_soup(ndu).find('div', class_='page-content') for
                      ndu in next_days_urls]

    forecasts_data = [[] for i in range(4)]
    # Parsing from saved tables
    for ftab in ftabs:
        # Parsing time row from source
        ftab = ftab.find('div', class_='hourContainer')
        time_row = ftab.find_all('span', class_='time_24h')
        time_row = [int(t.get_text()) for t in time_row]
        forecasts_data[0].extend(time_row)

        # Parsing weather parameters rows from source pages:
        # Temperature
        temp_row = ftab.find_all('span', class_='t')
        temp_row = [int(t.find('span', class_='temp_c').
                        get_text()) for t in temp_row]
        forecasts_data[1].extend(temp_row)
        # Pressure
        press_row = ftab.find_all('span', class_='value pres pres_mmhg')
        press_row = [float(p.get_text()) for p in press_row]
        forecasts_data[2].extend(press_row)
        # Wind velocity
        wind_vel_row = ftab.find_all('span', class_='windSpeed')
        wind_vel_row = [int(w.find('span', class_='value wind wind_ms').
                            get_text().split()[0]) for w in wind_vel_row]
        forecasts_data[3].extend(wind_vel_row)

    return generate_forecasts(
        start_forecast_datetime,
        start_date_from_source,
        forecasts_data[0],
        list(zip(*forecasts_data[1:])))


########
# MISC #
########

def get_soup(url, archive_payload=False):
    """Scraping html content from source with the help of Selenium library"""

    headers = {'Accept': '*/*', 'User-Agent': UserAgent().random}

    proxy = set_proxy()
    if proxy:
        proxy = f'http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}'
        proxies = {'https': proxy}
    else:
        proxies = None

    if not archive_payload:
        response = requests.get(
            url=url,
            # url='https://yandex.ru/internet',
            headers=headers,
            proxies=proxies,
            # proxies={'https': proxy},
            # proxies=None,
            timeout=10,

        )

    else:
        headers['Referer'] = 'https://rp5.ru/'
        response = requests.post(
            url=url,
            # cookies=cookies,
            headers=headers,
            data=archive_payload,
            proxies={'https': proxy},
            timeout=10
        )

    src = response.text
    return BeautifulSoup(src, "lxml")


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


def generate_forecasts(
        start_forecast_datetime,
        start_date_from_source,
        time_row,
        forecast_data):

    forecasts, prev_hour = [], None
    for hour in time_row:
        if prev_hour and prev_hour > hour:
            start_date_from_source += timedelta(days=1)
        datetime_ = start_date_from_source + timedelta(hours=hour)
        prev_hour = hour
        forecast_record = forecast_data.pop(0)
        if datetime_ >= start_forecast_datetime:
            forecasts.append((datetime_, forecast_record))

    return forecasts


############
# SELENIUM #
############


driver = None


def get_soup_selenium(url):
    """Scraping html content from source with the help of Selenium library"""
    global driver

    if not driver:
        logger = init_logger('Selenium')
        logger.info("> Driver initialization")

        driver = init_selenium_driver()

    driver.get(url=url)
    time.sleep(1)
    src = driver.page_source

    # driver.close()
    # driver.quit()

    return BeautifulSoup(src, "lxml")


def init_selenium_driver():
    """Selenium driver initialization"""

    # create a new Service instance and specify path to Chromedriver executable
    # service = ChromeService(executable_path=ChromeDriverManager().install())

    # create a ChromeOptions object
    # options = webdriver.ChromeOptions()
    options = Options()
    # run in headless mode
    options.add_argument("--headless=new")
    # disable the AutomationControlled feature of Blink rendering engine
    options.add_argument('--disable-blink-features=AutomationControlled')
    # disable pop-up blocking
    options.add_argument('--disable-popup-blocking')
    # disable sandbox mode
    options.add_argument('--no-sandbox')
    # disable shared memory usage
    options.add_argument('--disable-dev-shm-usage')
    # start the browser window in maximized mode
    options.add_argument('--start-maximized')
    # disable extensions
    # # options.add_argument('--disable-extensions')

    # # proxy
    # global proxies
    # if not proxies:
    #     get_proxies()
    proxy = set_proxy()
    if proxy:
        proxies_extension = selenium_proxy(
            proxy[2], proxy[3], proxy[0], proxy[1])
        options.add_extension(proxies_extension)
    # print(proxy)

    # Waits for page to be interactive
    options.page_load_strategy = 'eager'

    # create a driver instance
    driver = webdriver.Chrome(options=options)
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
