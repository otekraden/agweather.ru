"""Module scrapes data from forecast sources."""
from datetime import datetime, timedelta
import re
from json import load
import requests
from bs4 import BeautifulSoup
# from urllib.request import urlopen



def scrap_forecasts(path_to_config_file):
    """Run scarping and storing forecasts data process."""
    # Reading configuration file
    with open(path_to_config_file, 'r', encoding='UTF-8') as file:
        datascraper_config = load(file)

    # Required datetime row
    datetime_row = DatetimeRow(14).get_row()
    datetime_row_len = len(datetime_row)
    datetime_row_start = datetime_row[0]
    # Empty for scraped data
    forecasts_data_list = []

    try:  # Source site РП5

        source_config = datascraper_config["forecast_sources"][0]

        req = requests.get(url=source_config['url'],
                           headers=source_config['headers'],
                           cookies=source_config['cookies'],
                           proxies=datascraper_config['proxies'],
                           timeout=10)
        # return req
        src = req.text

        soup = BeautifulSoup(src, "lxml")

        # Parsing forecast table data
        ftab = soup.find(id='ftab_6_content')

        # Сalculate the starting date from the forecast source
        source_start_datetime = ftab.b.get_text()
        source_start_datetime = func_source_start_datetime(
            month_rusname_to_number(source_start_datetime),
            int(re.findall(r'\d+', source_start_datetime)[0]),
            int(ftab.find(class_='underlineRow')
                .next_sibling.next_sibling.get_text())
        )

        # Сut or add None
        add_none, cut_exc = add_none_or_cut_exc(
            source_start_datetime, datetime_row_start)

        # Parsing of the air temperature row
        t_row = ftab.find_all(class_='toplineRow')[
            1:][cut_exc:][:datetime_row_len]
        t_row = [int(t.find(class_='t_0').get_text()) for t in t_row]
        t_row = add_none + t_row

        # Parsing of the air pressure row
        p_row = ftab.find_all(class_="p_0")[1:][cut_exc:][:datetime_row_len]
        p_row = [int(p.get_text()) for p in p_row]
        p_row = add_none + p_row

        # Parsing of the wind speed row
        w_row = ftab.find(
            'a', class_="t_wind_velocity").parent.parent.find_all('td')
        w_row = [int(w.get_text().strip().split(' ')[0])
                 for w in w_row[1:]][cut_exc:][:len(t_row)]
        w_row = add_none + w_row

        # Recording parsed data general list
        forecasts_data_list.append(
            ((source_config['name'], source_config['chart_color']),
             (t_row, p_row, w_row)))

    except AttributeError:
        scraper_error(source_config['name'])
        return

    try:  # Source site "Яндекс Погода"

        source_config = datascraper_config["forecast_sources"][1]

        response = requests.get(url=source_config['url'],
                                params=source_config['params'],
                                cookies=source_config['cookies'],
                                headers=source_config['headers'], timeout=10)
        src = response.text
        soup = BeautifulSoup(src, 'lxml')

        # Parsing forecast table data
        ftab = soup.find(
            class_=['forecast-details', 'i-bem', 'forecast-details_js_inited'])

        # Сalculate the starting date from the forecast source
        source_start_datetime = func_source_start_datetime(
            month_rusname_to_number(
                ftab.find(class_='forecast-details__day-month').get_text()),
            int(ftab.find(class_='forecast-details__day-number').get_text()),
            9  # Morning
        )

        # Сut or add None
        add_none, cut_exc = add_none_or_cut_exc(
            source_start_datetime, datetime_row_start)

        # Parsing of the air temperature row
        t_row = ftab.find_all(
            class_='weather-table__temp')[cut_exc:][:datetime_row_len]
        t_row = [t.get_text() for t in t_row]
        # Conversion of the temperature of the form "+6...+8"
        # to the average value
        t_row = [t.replace(chr(8722), '-').split('…') for t in t_row]
        t_row = [[int(i) for i in t] for t in t_row]
        t_row = [int(sum(t)/len(t)) for t in t_row]
        t_row = add_none + t_row

        # Parsing of the air pressure row
        p_row = ftab.find_all(
            class_='weather-table__body-cell_type_air-pressure')
        p_row = p_row[cut_exc:][:datetime_row_len]
        p_row = [int(p.get_text()) for p in p_row]
        p_row = add_none + p_row

        # Parsing of the wind speed row
        w_row = ftab.find_all(class_="wind-speed")[cut_exc:][:datetime_row_len]
        w_row = [int(round(float(w.get_text().replace(',', '.')), 0))
                 for w in w_row]
        w_row = add_none + w_row

        # Recording parsed data general list
        forecasts_data_list.append(
            ((source_config['name'], source_config['chart_color']),
             (t_row, p_row, w_row)))

    except AttributeError:
        scraper_error(source_config['name'])
        return

    try:  # Source site Meteoinfo.ru

        source_config = datascraper_config["forecast_sources"][2]

        req = requests.get(source_config['url'],
                           headers=source_config['headers'], timeout=10)
        src = req.text
        soup = BeautifulSoup(src, "lxml")

        # Parsing forecast table data
        ftab = soup.find(id='div_4_1')
        ftab = ftab.find(class_='hidden-desktop')

        # Сalculate the starting date from the forecast source
        source_start_datetime = ftab.find('nobr')
        start_hour = source_start_datetime.parent.next_sibling.get_text()
        start_hour = 15 if start_hour.strip().lower() == 'день' else 3
        source_start_datetime = source_start_datetime.get_text()
        source_start_datetime = func_source_start_datetime(
            month_rusname_to_number(source_start_datetime),
            int(re.findall(r'\d+', source_start_datetime)[0]),
            start_hour
        )

        # Сut or add None
        add_none, cut_exc = add_none_or_cut_exc(
            source_start_datetime, datetime_row_start)
        add_none = add_none[:len(add_none)//2]
        cut_exc //= 2

        # Parsing of the air temperature row
        t_row = ftab.find_all(class_='fc_temp_short')[
            cut_exc:][:datetime_row_len]
        t_row = [[int(t.get_text().rstrip('°')), 'none'] for t in t_row]
        t_row = add_none + sum(t_row, [])

        # Parsing of the wind speed row
        w_row = ftab.find_all('i')[cut_exc:][:datetime_row_len]
        p_row = w_row
        w_row = [[int(w.next_sibling.get_text()), 'none'] for w in w_row]
        w_row = add_none + sum(w_row, [])

        # Parsing of the air pressure row
        p_row = [[int(p.parent.next_sibling.get_text()), 'none']
                 for p in p_row]
        p_row = add_none + sum(p_row, [])

        # Recording parsed data general list
        forecasts_data_list.append(
            ((source_config['name'], source_config['chart_color']),
             (t_row, p_row, w_row)))

    except AttributeError:
        scraper_error(source_config['name'])
        return

    try:  # Source site Foreca.ru

        source_config = datascraper_config["forecast_sources"][3]

        # Empty lists for scraped data
        t_row, p_row, w_row = [], [], []

        # Walking in cycle by forecast day web pages
        old_url_with_date = ''
        for date in datetime_row[:36]:
            url_with_date = source_config['url'] + \
                str(date).replace('-', '')[:8]
            # Open next forecast web page
            if url_with_date != old_url_with_date:
                old_url_with_date = url_with_date
                req = requests.get(url_with_date,
                                   cookies=source_config['cookies'],
                                   headers=source_config['headers'],
                                   timeout=10)
                src = req.text
                soup = BeautifulSoup(src, "lxml")

            # Parsing single values of weather parameters
            temp = press = wind = 'none'
            tag = soup.find('strong', string=str(date)
                            [11:16]).parent.parent
            tag = tag.next_sibling.next_sibling
            temp = int(tag.get_text().strip().replace('°', ''))
            tag = tag.next_sibling.next_sibling
            wind = int(tag.get_text().strip().replace(' м/с', ''))
            tag = tag.next_sibling.next_sibling
            press = int(tag.get_text().strip().split(' ')[-3])

            # Saving single weather data
            t_row.append(temp)
            p_row.append(press)
            w_row.append(wind)

        # Recording parsed data general list
        forecasts_data_list.append(
            ((source_config['name'], source_config['chart_color']),
             (t_row, p_row, w_row)))

    except AttributeError:
        scraper_error(source_config['name'])
        return


    return datetime_row_start.isoformat(), forecasts_data_list


class DatetimeRow():
    """Represent datetime for forecast record."""

    # Forecast data step = 6 hours
    step = timedelta(hours=6)

    def __init__(self, forec_len_days):
        """Intiation of dattimerow."""
        start_date = self.start_forec_date()
        self.datetime_row = [
            start_date + i*DatetimeRow.step for i in range(0, forec_len_days*4)]

    def get_row(self):
        """Return datetime row."""
        return self.datetime_row

    @staticmethod
    def start_forec_date():
        """Determine the start date of the forecast.

        today at 3:00, 9:00, 15:00 or 21:00.
        """
        start_dt = datetime.now()  # Local time now
        start_dt = start_dt.replace(minute=0, second=0, microsecond=0)
        bhour = (((start_dt.hour-3)//6+1)*6+3)
        if bhour == 27:
            start_dt = start_dt.replace(hour=3)
            start_dt = start_dt + timedelta(days=1)
        else:
            start_dt = start_dt.replace(hour=bhour)
        return start_dt


def scraper_error(source_name):
    """Print error message after scraper failure."""
    print(f"Failed scrap data on site: {source_name}. Exit scraper.")


def func_source_start_datetime(start_month, start_day, start_hour):
    """Calculate the starting date of the forecast source."""
    start_year = datetime.now().year

    # Processing the transition through the new year
    if datetime.now().month == 12 and start_month == 1:
        start_year += 1

    return datetime(year=start_year, month=start_month,
                    day=start_day, hour=start_hour)


def month_rusname_to_number(name):
    """Translate russian month name to its number."""
    month_numbers = {'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4, 'май': 5,
                     'июн': 6, 'июл': 7, 'авг': 8, 'сен': 9, 'окт': 10,
                     'ноя': 11, 'дек': 12}
    number = name.strip().lower().split(' ')[-1][:3]
    number = month_numbers[number]

    return number


def add_none_or_cut_exc(source_start_datetime, datetime_row_start):
    """Сalculates of None values additions at the.

    data row beginnings or their end trimmings to
    align their lengths acording to the reqiured datetime row.
    """
    if source_start_datetime == datetime_row_start:
        add_none, cut_exc = 0, 0
    elif source_start_datetime > datetime_row_start:
        add_none, cut_exc = (source_start_datetime -
                             datetime_row_start)//timedelta(hours=6), 0
    else:
        add_none, cut_exc = 0, (datetime_row_start -
                                source_start_datetime)//timedelta(hours=6)
    add_none = ['none' for i in range(0, add_none)]
    return add_none, cut_exc


if __name__ == '__main__':

    forecasts = scrap_forecasts(
        "static/datascraper_config.json")
        # "datascraper_config.json")
    print(forecasts)
