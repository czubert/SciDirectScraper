import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from io import BytesIO

import constants


def does_element_exist(driver, tag):
    try:
        element_exist = driver.find_element(By.CLASS_NAME, tag)  # .is_displayed()
    except NoSuchElementException:
        element_exist = False
        print("Pagination: all pages parsed")

    return element_exist


def write_data_coll_to_file(df: pd.DataFrame, file_name: str):
    import os
    path = 'output'
    if not os.path.isdir(path):
        os.mkdir(path)

    df.to_excel(f'{path}/{file_name}.xlsx')
    df.to_csv(f'{path}/{file_name}.csv', encoding='utf-16')


def write_xls_csv_to_buffers(df: pd.DataFrame):
    return write_xlsx_to_buffer(df), write_csv_to_buffer(df)


def write_xlsx_to_buffer(df: pd.DataFrame):
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer)

        writer.save()
        writer.close()

    return buffer


def write_csv_to_buffer(df: pd.DataFrame):
    buffer = BytesIO()
    df.to_csv(buffer)

    return buffer


def build_filename(keyword, years, articles_urls, authors_collection):
    if len(years) == 1:
        year = str(years[0])
    else:
        years = sorted(years)
        year = f'{years[0]}-{years[-1]}'

    authors_num = len(authors_collection.index)
    pub_num = len(articles_urls)

    return f'key-{keyword}_years-{year}_auth-num-{authors_num}_publ-num-{pub_num}'


def create_named_dataframe():
    columns = constants.COLUMNS
    df = pd.DataFrame(columns=columns)
    df.index.name = 'id'
    return df


def initialize_driver():
    options = webdriver.ChromeOptions()
    # to open maximized window
    options.add_argument("start-maximized")
    # to supress the error messages/logs
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=ChromeService(), options=options)

    return driver


def open_link_in_new_tab(driver, url):
    # Open a new tab
    driver.execute_script("window.open('');")

    # Switch to the new tab and open new URL
    driver.switch_to.window(driver.window_handles[1])
    driver.get(url)


def open_link_in_new_tab(driver):
    # Closing new_url tab
    driver.close()

    # Switching to old tab
    driver.switch_to.window(driver.window_handles[0])

    return driver
