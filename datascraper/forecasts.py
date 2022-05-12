from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path


######################################
# FORECAST SOURCES SCRAPER FUNCTIONS #
######################################
# To arhieve calling functions from forecast template class method
# their names must be the same as in Models: "template.forecast_source.id"

def rp5(start_datetime, url):

    # Getting html content from source
    soup = get_soup(url)
    ftab = soup.find(id='ftab_content')

    # Getting start date from source html page
    start_date_from_source = ftab.find(
        'span', class_="weekDay").get_text().split(',')[-1].split()
    start_date_from_source = func_start_date_from_source(
        month=month_rusname_to_number(start_date_from_source[1][:3]),
        day=int(start_date_from_source[0]),
        req_start_datetime=start_datetime
    )

    # Generation time row
    time_row = ftab.find('tr', class_="forecastTime").find_all('td')[1:-1]
    time_row = [int(t.get_text()) for t in time_row]

    # Genereating weather parameters rows:
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
    # Merge parameters fom source into one tuple
    raw_data = (temp_row, press_row, wind_vel_row)

    return json_data_gen(
        start_datetime, start_date_from_source, time_row, raw_data)


def yandex(start_datetime, url):
    # Getting html content from source
    soup = get_soup(url)
    ftab = soup.find(
        'div', class_=[
            'forecast-details', 'i-bem', 'forecast-details_js_inited'])
    print(ftab)
    # Getting start date from source html page
    start_date_from_source = func_start_date_from_source(
        month=month_rusname_to_number(ftab.find(
            'span', class_='forecast-details__day-month').get_text()),
        day=int(ftab.find(
            'strong', class_='forecast-details__day-number').get_text()),
        req_start_datetime=9  # Morning
    )
    
    return [start_date_from_source]


def meteoinfo(start_datetime, url):
    return ['meteoinfo', [url], start_datetime.isoformat()]


def foreca(start_datetime, url):
    return ['foreca', [url], start_datetime.isoformat()]


########
# MISC #
########


def get_soup(url):
    """Getting html content from source with the help of Selenium library"""
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")

    driver_executable_path = str(
        Path(__file__).resolve().parent) + "/chromedriver"

    driver = webdriver.Chrome(executable_path=driver_executable_path,
                              options=options)

    try:
        driver.get(url=url)
        src = driver.page_source
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()

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


def intp_linear(xa, xc, xb, ya, yb):
    """Linear interpolation."""
    return round((xc-xa)/(xb-xa)*(yb-ya)+ya)


def json_data_gen(
        start_datetime, start_date_from_source, time_row, raw_data):

    # Generating datime row from html source
    datetime_row, datetime_ = [], start_date_from_source
    for i, hour in enumerate(time_row):
        if i != 0 and hour < time_row[i-1]:
            datetime_ += timedelta(days=1)
        datetime_row.append(datetime_ + timedelta(hours=hour))

    # Generating json record
    data_json, datetime_ = [[] for i in raw_data], start_datetime
    for i, dt in enumerate(datetime_row):
        if i == 0 and datetime_ < dt:
            [data_json[p].append(None) for p in range(len(raw_data))]

        elif datetime_ == dt:
            [data_json[j].append(p[i]) for j, p in enumerate(raw_data)]

        elif datetime_ < dt:
            [data_json[j].append(intp_linear(
                datetime_row[i-1].timestamp(),
                datetime_.timestamp(),
                dt.timestamp(),
                p[i-1],
                p[i])) for j, p in enumerate(raw_data)]
        else:
            continue

        # Next step datetime
        datetime_ += timedelta(hours=6)

    return data_json
