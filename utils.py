import time

import streamlit as st
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, InvalidSessionIdException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from io import BytesIO

import constants


def does_element_exist(driver, tag):
    try:
        element_exist = driver.find_element(By.LINK_TEXT, tag)  # .is_displayed()
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


def initialize_driver(window):
    options = webdriver.ChromeOptions()
    # # to supress the error messages/logs
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', True)

    # Initialising Driver with preset options
    # driver = webdriver.Chrome(service=ChromeService('chromedriver'), options=options)
    from selenium.webdriver.edge.service import Service
    service = Service(verbose=True)
    driver = webdriver.Edge(service=service)
    time.sleep(0.7)
    if window == 'Maximized':
        driver.maximize_window()
    elif window == 'Hidden':
        driver.set_window_position(-2000, 0)

    return driver


def open_link_in_new_tab(driver, url):
    # Open a new tab
    driver.execute_script("window.open('');")

    # Switch to the new tab and open new URL
    driver.switch_to.window(driver.window_handles[1])
    driver.get(url)
    time.sleep(0.5)

    return driver


def close_link_tab(driver):
    # Closing new_url tab
    driver.close()

    # Switching to old tab
    driver.switch_to.window(driver.window_handles[0])
    return driver


def paginate(requested_num_of_publ, pub_per_page, articles_urls, next_class_name, driver, wait, tab=True):
    if requested_num_of_publ == 0:
        n_loops = -1
    else:
        n_loops = (requested_num_of_publ // pub_per_page) + 1

    i = 0

    while i != n_loops:

        # Short break so the server do not block script
        time.sleep(0.7)  # important: lower values result in error

        # Parse web for urls
        articles_urls += [item.get_attribute("href") for item in wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "result-list-title-link")))]

        # Scrolls to the bottom to avoid 'feedback' pop-up
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        info = f'{len(articles_urls)} addresses extracted'
        print(info)
        st.sidebar.write(info)

        if not does_element_exist(driver, tag=next_class_name) and tab is True:
            return driver

        elif does_element_exist(driver, tag=next_class_name):
            if tab:
                # It is opening 'next button; in new tab instead of clicking it, so the pub categories do not hide
                url = wait.until(EC.presence_of_element_located((By.LINK_TEXT, next_class_name))).get_attribute('href')
                driver = open_link_in_new_tab(driver, url)
                tab = False
                continue

            wait.until(EC.presence_of_element_located((By.LINK_TEXT, next_class_name))).click()

        else:
            try:
                driver = close_link_tab(driver)
            except InvalidSessionIdException:
                print('Pagination finished')
            finally:
                return driver

        i += 1
