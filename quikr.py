

import copy
import sys
import os
import json
import logging
import requests
import time
import re
import socket
import random

from json import JSONEncoder
from datetime import datetime
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import InvalidArgumentException

# Set your chrome path in environment variable
# Also put the chrome driver in the same folder
# Get environment variables
chrome_path = os.getenv('chrome')

service = Service(chrome_path + "/chromedriver.exe")
options = webdriver.ChromeOptions()
# options.add_argument('--headless')
options.binary_location = chrome_path + "/chrome.exe"


def log_and_console_info(message: str):
    print(f'INFO : {message}')
    logging.info(f'INFO : {message}')


def log_and_console_error(message: str):
    print(f'ERROR: {message}')
    logging.error(f'ERROR: {message}')


def get_driver():
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    driver.maximize_window()
    return driver


def extract_data(driver: WebDriver, city_name: str, search_text: str):
    try:
        driver.get(f"https://www.quikr.com/cars/used+cars+cars+chennai+x467")
        # time.sleep(15)

        try:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "wpn_modal_actionButton"))).click()
            print("Modal found and clicked")
        except TimeoutException:
            print("Modal wasn't found")
        # time.sleep(60)
        # Select city
        # log_and_console_info(f'select city : {driver.find_elements("div.select-city")}')
        # driver.find_element(By.CSS_SELECTOR, "div.select-city").click()
        # # Get all cities
        # cities_anchor = driver.find_elements(By.CSS_SELECTOR, "div.city-state-scroll > ul > li > a")

        # for city in cities_anchor:
        #     if city.text.strip().lower() == city_name.lower():
        #         city.click()

        # search_element = driver.find_element(By.CSS_SELECTOR, "form#searchFormIndex > input#query")
        # search_element.send_keys(search_text)
        # search_element.send_keys(Keys.ENTER)

        # driver.find_element(By.CSS_SELECTOR, "form#searchFormIndex > input#query").send_keys(Keys.ENTER)
        time.sleep(2)
        # driver.find_element(By.CSS_SELECTOR, "button#submitSearch").click()
        print("clicked!")
        # time.sleep(5)
        # log_and_console_info(driver.page_source.encode("utf-8"))

        result_count = driver.find_element(By.CSS_SELECTOR, "div.qc__snb-header__start").text.strip().split(' ')[0]
        log_and_console_info(f"Results count is {result_count}")
        # time.sleep(60)
        try:
            if(result_count.isnumeric()):
                ######################################
                products_per_scroll = 12
                scroll_times = int(result_count) // 24
                log_and_console_info(f'Expected scroll time {scroll_times}')
                if(scroll_times > 0):
                    for i in range(1, scroll_times + 1):  # Adding 1 as the range will not pick the range boundary
                        ad_list_element = driver.find_element(By.CSS_SELECTOR, 'div.qc-ads > div.mdc-layout-grid')
                        visible_ads = len(driver.find_elements(By.CSS_SELECTOR, 'a.qc-ads__card'))
                        last_ad_count = (i*products_per_scroll)-1
                        log_and_console_info(f'Number of visible ads is {visible_ads} last ad position is {last_ad_count}')
                        if(visible_ads < int(result_count)):
                            if visible_ads < last_ad_count:
                                last_ad_count = visible_ads-1

                            log_and_console_info(f'Scrolling {i} times to the visible last element..')
                            scroll_to_element = ad_list_element.find_elements(By.CSS_SELECTOR, 'a.qc-ads__card')[last_ad_count]
                            driver.execute_script("arguments[0].scrollIntoView();", scroll_to_element)
                            time.sleep(7)
                        else:
                            continue  # Skipping with the list of sellers loaded already
                ######################################
            else:
                log_and_console_info('No options found!')
        except Exception as ex:
            log_and_console_error("Error while scrolling to end of the results.")
            logging.error(ex, exc_info=True)

        qc_ads = driver.find_elements(By.CSS_SELECTOR, "a.qc-ads__card")
        # print(qc_ads)
        log_and_console_info(f"Collecting details of found {len(qc_ads)} products")

        for count, ad in enumerate(qc_ads):
            url = ad.get_attribute("href")
            title = ad.find_element(By.CSS_SELECTOR, "h2").text.strip()
            features = ad.find_element(By.CSS_SELECTOR, "div.prime-features").text.strip()
            price = ad.find_element(By.CSS_SELECTOR, "div.price").text.strip()
            price = re.sub('\D', '', unidecode(price))
            location = ad.find_element(By.CSS_SELECTOR, "footer.qc-ads__card--footer > p > span").text.strip()
            log_and_console_info(f"{count}\t{title}\t{features}\t{price}\t{location}\t{url}")

            output_file = open("output.txt", "a", encoding='utf8', errors='ignore')
            output_file.write(f"{count}\t{title}\t{features}\t{price}\t{location}\t{url}\n")
            output_file.close()
    except Exception as e:
        logging.error(e, exc_info=True)
        print("Error!")


def main():
    city_name = "chennai"
    search_text = "cars"

    driver = get_driver()

    try:
        logging.basicConfig(filename='log.txt', format='%(asctime)s %(message)s', level=logging.INFO)

        log_and_console_info(f'Received {len(sys.argv)} arguments')

        if len(sys.argv) == 2:
            city_name = sys.argv[1]
            search_text = sys.argv[2]

        program_start_time = datetime.now()
        log_and_console_info(f"##### Starting the crawling at {program_start_time}")

        extract_data(driver, city_name, search_text)

        log_and_console_info(f"##### Program execution time is {datetime.now() - program_start_time}")

    except Exception as error:
        log_and_console_error(f'Error occurred {error}')
        logging.error(error, exc_info=True)
    finally:
        log_and_console_info('Quiting the webdriver!')
        driver.quit()


if __name__ == '__main__':
    main()
