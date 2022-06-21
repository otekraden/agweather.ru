from selenium.webdriver.common.by import By
from datascraper.forecasts import month_rusname_to_number, init_selenium_driver
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from time import sleep as time_sleep

#############################
# ARCHIVE SCRAPER FUNCTIONS #
#############################


def arch_rp5(start_datetime: datetime, url, end_datetime=None):

    # Initialization selenium driver
    driver = init_selenium_driver()
    driver.get(url)

    #  Default archive beginning 01.01.2022 00:00 local time
    if not end_datetime:
        end_datetime = start_datetime.replace(
            year=2022, month=1, day=1, hour=0)
        step_option = 2  # 30 days
    else:
        step_option = 0  # 1 day

    # While cycle back to end_datetime.
    arch_data, date_ = [], start_datetime
    while date_ > end_datetime:

        # print(date_.isoformat())
        # Scraping html content from source
        date_input = driver.find_element(By.ID, 'calender_archive')
        # selected period 30 days
        period_input = driver.find_elements(
            By.CLASS_NAME, 'input_radio')[step_option]
        period_input.click()
        date_input.clear()
        date_input.send_keys(date_.strftime("%d.%m.%Y"))
        select_button = driver.find_element(By.CLASS_NAME, 'archButton')
        select_button.click()
        time_sleep(1)
        src = driver.page_source
        soup = BeautifulSoup(src, "lxml")
        atab = soup.find('table', id='archiveTable')

        # Parsing start date from source html page
        start_date_from_source = atab.find('td', class_='cl_dt').\
            get_text().replace('г.', ' ').replace(',', ' ').split()[:-1]
        start_date_from_source = start_datetime.replace(
                year=int(start_date_from_source[0]),
                month=month_rusname_to_number(start_date_from_source[2]),
                day=int(start_date_from_source[1]),
                hour=0)

        atab = atab.find_all('tr')[1:]
        atab = [row.find_all('td')[-29:] for row in atab]

        datetime_ = start_date_from_source
        prev_time = None
        for i, row in enumerate(atab):

            time = int(row[0].get_text())
            datetime_ = datetime_.replace(hour=time)
            # print('+', datetime_.isoformat())
            # print(prev_time, time)
            if i != 0 and prev_time < time:
                datetime_ -= timedelta(days=1)
            prev_time = time

            # temp = float(row[1].find(
            #     'div', class_='t_0 dfs').get_text())
            temp = row[1].find('div', class_='t_0 dfs')
            temp = float(temp.get_text()) if temp else None

            press = row[2].find('div', class_='p_0 dfs')
            press = float(press.get_text()) if press else None
            wind_vel = row[7].find('div', class_='wv_0')
            wind_vel = wind_vel.get_text() if wind_vel else None
            wind_vel = int(re.findall(r'\d+', wind_vel)[0]) \
                if wind_vel else 0
            record = [datetime_, [temp, press, wind_vel]]
            if record not in arch_data and datetime_ > end_datetime:
                arch_data.append(record)

        date_ -= timedelta(days=30)

    # END While cycle

    driver.close()
    driver.quit()

    return arch_data
