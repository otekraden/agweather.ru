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

PROXY = set_proxy()


####################################
# FORECAST SOURCES SCRAPER CLASSES #
####################################
# Attention!! Scraper Class name must have the same Name as in the Database,
# table "datascraper_foreacstsource", column "scraper_class"

class BaseForecastScraper():
    """Base class for scrapers."""

    def __init__(self, *args, **kwargs):
        self.local_datetime = kwargs["local_datetime"]
        self.start_forecast_datetime = kwargs["start_forecast_datetime"]
        self.start_date_from_source = None
        self.time_row = []
        self.temp_row = []
        self.press_row = []
        self.wind_vel_row = []

    def get_forecasts(self):
        """Generating forecast records from scraped data."""

        forecast_data = list(
            zip(self.temp_row, self.press_row, self.wind_vel_row))

        forecasts, prev_hour = [], None
        for hour in self.time_row:
            if prev_hour and prev_hour > hour:
                self.start_date_from_source += timedelta(days=1)
            datetime_ = self.start_date_from_source + timedelta(hours=hour)
            prev_hour = hour
            forecast_record = forecast_data.pop(0)
            if datetime_ >= self.start_forecast_datetime:
                forecasts.append((datetime_, forecast_record))

        return forecasts

    def get_start_date_from_source(self, month, day):
        """Calculate the starting date of the forecast source."""
        year = self.local_datetime.year
        # Processing the transition through the new year
        if self.local_datetime.month == 12 and month == 1:
            year += 1
        return datetime(year, month, day, tzinfo=self.local_datetime.tzinfo)


class rp5(BaseForecastScraper):
    """https://rp5.ru/"""

    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Scraping html content from source
        soup = get_soup(url)
        ftab = soup.find(id='ftab_content')

        # Parsing start date from source html page
        start_date_from_source = ftab.find(
            'span', class_="weekDay").get_text().split(',')[-1].split()
        self.start_date_from_source = self.get_start_date_from_source(
            month=month_name_to_number(start_date_from_source[1][:3]),
            day=int(start_date_from_source[0])
        )

        # Parsing time row from source
        time_row = ftab.find('tr', class_="forecastTime").find_all('td')[1:-1]
        self.time_row = [int(t.get_text()) for t in time_row]

        # Parsing weather parameters rows from source:
        # Temperature
        temp_row = ftab.find('a', class_='t_temperature')
        temp_row = temp_row.parent.parent.find_all('td')[1:-1]
        self.temp_row = [
            int(t.find('div', class_='t_0').get_text()) for t in temp_row]
        # Pressure
        press_row = ftab.find('a', class_='t_pressure')
        press_row = press_row.parent.parent.find_all('td')[1:-1]
        self.press_row = [
            int(t.find('div', class_='p_0').get_text()) for t in press_row]
        # Wind velocity
        wind_vel_row = ftab.find('a', class_='t_wind_velocity')
        wind_vel_row = wind_vel_row.parent.parent.find_all('td')[1:-1]
        wind_vel_row = [w.find('div', class_='wv_0') for w in wind_vel_row]
        self.wind_vel_row = [
            int(w.get_text()) if w else 0 for w in wind_vel_row]

        # TODO: ADD NEW PARAMETER HERE


class yandex(BaseForecastScraper):
    """https://yandex.ru/pogoda"""

    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Scraping html content from source
        attempt = 0
        while attempt < 3:
            try:
                soup = get_soup_selenium(url)
                ftab = soup.find('main').find_all('div', recursive=False)[1]
            except AttributeError as e:
                print(e)
                time.sleep(1)
                attempt += 1
                continue
            break

        ftab = ftab.find_all('article', recursive=False)

        # Parsing start date from source html page
        date_tags = ftab[0].find('p').find_all('span')

        self.start_date_from_source = self.get_start_date_from_source(
            month=month_name_to_number(date_tags[2].get_text()),
            day=int(date_tags[0].get_text())
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
        self.temp_row = [sum(t)/len(t) for t in temp_row]

        # Pressure
        self.press_row = [int(p.get_text()) for p in ftab[2::6]]

        # Wind velocity
        wind_vel_row = [w.contents[0].replace(',', '.') for w in ftab[4::6]]
        self.wind_vel_row = [float(w) for w in wind_vel_row]

        # Parsing time row from source
        self.time_row = [9, 15, 21, 3]*(len(temp_row)//4)

        # TODO: ADD NEW PARAMETER HERE


class meteoinfo(BaseForecastScraper):
    """https://meteoinfo.ru/forecasts/"""

    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Scraping html content from source
        soup = get_soup(url)
        ftab = soup.find('div', class_='hidden-desktop')

        # Parsing start date from source html page
        start_date_from_source = ftab.find('nobr')
        start_hour = start_date_from_source.parent.next_sibling.get_text()
        start_hour = 15 if start_hour.strip().lower() == 'день' else 3
        start_date_from_source = start_date_from_source.get_text()
        self.start_date_from_source = self.get_start_date_from_source(
            month=month_name_to_number(start_date_from_source),
            day=int(re.findall(r'\d+', start_date_from_source)[0])
        )

        # Parsing weather parameters rows from source:
        # Temperature
        temp_row = ftab.find_all('span', class_='fc_temp_short')
        self.temp_row = [int(t.get_text().rstrip('°')) for t in temp_row]
        # Wind velocity
        wind_vel_row = ftab.find_all('i')
        press_row = wind_vel_row[:]
        self.wind_vel_row = [int(w.parent.get_text()) for w in wind_vel_row]
        # Pressure
        self.press_row = [
            int(p.parent.next_sibling.get_text()) for p in press_row]

        # Parsing time row from source
        time, self.time_row = start_hour, []
        for t in temp_row:
            self.time_row.append(time)
            time = 15 if time == 3 else 3

        # TODO: ADD NEW PARAMETER HERE


class foreca(BaseForecastScraper):
    """https://www.foreca.ru/"""

    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Scraping html content from source first day page
        soup = get_soup(url)

        ftab = soup.find('div', class_='page-content')

        # Parsing start date from source html page
        start_date_from_source = ftab.find(
            'div', class_='date').get_text().split()
        self.start_date_from_source = self.get_start_date_from_source(
            month=month_name_to_number(start_date_from_source[1][:3]),
            day=int(start_date_from_source[0])
        )

        # Parsing next days urls from source first day page
        domain = url[:url.find('/', 8)]
        next_days_urls = ftab.find('ul', class_='days').find_all('a')[1:]
        next_days_urls = [domain + nd.get('href') for nd in next_days_urls]

        # Scraping tables data to array
        ftabs = [ftab] + [get_soup(ndu).find(
            'div', class_='page-content') for ndu in next_days_urls]

        # Parsing from saved tables
        for ftab in ftabs:
            # Parsing time row from source
            ftab = ftab.find('div', class_='hourContainer')
            time_row = ftab.find_all('span', class_='time_24h')
            time_row = [int(t.get_text()) for t in time_row]
            self.time_row.extend(time_row)

            # Parsing weather parameters rows from source pages:
            # Temperature
            temp_row = ftab.find_all('span', class_='t')
            temp_row = [int(t.find('span', class_='temp_c').
                            get_text()) for t in temp_row]
            self.temp_row.extend(temp_row)
            # Pressure
            press_row = ftab.find_all('span', class_='value pres pres_mmhg')
            press_row = [float(p.get_text()) for p in press_row]
            self.press_row.extend(press_row)
            # Wind velocity
            wind_vel_row = ftab.find_all('span', class_='windSpeed')
            wind_vel_row = [int(w.find('span', class_='value wind wind_ms').
                                get_text().split()[0]) for w in wind_vel_row]
            self.wind_vel_row.extend(wind_vel_row)

            # TODO: ADD NEW PARAMETER HERE

# TODO: ADD NEW FORECAST SCRAPER CLASS HERE


########
# MISC #
########

def get_soup(url, archive_payload=False):
    """Scraping html content from source with the help of Selenium library"""

    headers = {'Accept': '*/*', 'User-Agent': UserAgent().random}

    if PROXY:
        proxy = f'http://{PROXY[2]}:{PROXY[3]}@{PROXY[0]}:{PROXY[1]}'
        proxies = {'https': proxy}
    else:
        proxies = None

    if not archive_payload:
        response = requests.get(
            url=url,
            headers=headers,
            proxies=proxies,
            timeout=10,
        )

    else:
        headers['Referer'] = 'https://rp5.ru/'
        response = requests.post(
            url=url,
            headers=headers,
            data=archive_payload,
            proxies=proxies,
            timeout=10
        )

    src = response.text
    return BeautifulSoup(src, "lxml")


def month_name_to_number(name):
    """Translate month name to its number."""
    name = name.strip().lower().split(' ')[-1][:3]

    if name == 'май':
        return 5
    # 01.02.2024 fix bug with meteoinfo.ru
    # [ord(l) for l in 'фeв'] == [1092, 101!!, 1074]
    elif name == 'фeв':
        return 2
    # 01.03.2024 fix bug with meteoinfo.ru
    # [ord(l) for l in 'фeв'] == [1084, 97!!, 1088]
    elif name == 'мaр':
        return 3

    month_tuple = ('янв', 'фев', 'мар', 'апр', 'мая', 'июн',  # RUS
                   'июл', 'авг', 'сен', 'окт', 'ноя', 'дек',
                   'jan', 'feb', 'mar', 'apr', 'may', 'jun',  # ENG
                   'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
    return month_tuple.index(name) % 12 + 1


############
# SELENIUM #
############

driver = None


def get_soup_selenium(url):
    """Scraping html content from source with the help of Selenium library"""
    global driver

    if not driver:
        logger = init_logger('Selenium')
        logger.debug("Driver initialization")
        driver = init_selenium_driver()

    driver.get(url=url)
    time.sleep(1)
    src = driver.page_source

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

    if PROXY:
        proxies_extension = selenium_proxy(
            PROXY[2], PROXY[3], PROXY[0], PROXY[1])
        options.add_extension(proxies_extension)

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
    """Enabling using proxy with Selenium."""
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
