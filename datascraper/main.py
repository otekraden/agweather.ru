# import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from pathlib import Path


def get_source_html(url):

    # print(Path(__file__).resolve().parent)

    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")

    driver_executable_path = str(
        Path(__file__).resolve().parent) + "/chromedriver"

    driver = webdriver.Chrome(executable_path=driver_executable_path,
                              options=options
                              )

    # driver.maximize_window()

    try:
        driver.get(url=url)
        src = driver.page_source

        time.sleep(3)

        # driver.get("https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html")
        print(ftab)
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()

    soup = BeautifulSoup(src, "lxml")
    ftab = soup.find(id='ftab_6_content')

    return ftab


def main():
    url = "https://rp5.ru/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%A1%D0%B0%D0%BD%D0%BA%D1%82-%D0%9F%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3%D0%B5"

    return get_source_html(url)


if __name__ == "__main__":
    main()
