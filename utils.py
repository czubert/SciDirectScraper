import datetime
import os
import time
import pandas as pd
from io import BytesIO
# Selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service

# Modules
import constants


def does_element_exist(driver, tag):
    try:
        element_exist = driver.find_element(By.LINK_TEXT, tag)  # .is_displayed()
    except NoSuchElementException:
        element_exist = False

    return element_exist


def get_current_time():
    now = datetime.datetime.now()

    return f'{now.year}_{now.month}_{now.day}-{now.hour}h_{now.minute}min'


def write_data_to_file(df: pd.DataFrame, file_name: str):
    df.to_excel(f'{file_name[:-4]}.xlsx')
    df.to_csv(f'{file_name[:-4]}.csv', encoding='utf-16')

#
# def write_xls_csv_to_buffers(df: pd.DataFrame):
#     return write_xlsx_to_buffer(df), write_csv_to_buffer(df)
#
#
# def write_xlsx_to_buffer(df: pd.DataFrame):
#     buffer = BytesIO()
#
#     with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
#         df.to_excel(writer)
#
#         writer.save()
#         writer.close()
#
#     return buffer
#
#
# def write_csv_to_buffer(df: pd.DataFrame):
#     buffer = BytesIO()
#     df.to_csv(buffer)
#
#     return buffer


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
    service = Service(verbose=True)
    driver = webdriver.Edge(service=service)
    time.sleep(0.1)
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
    time.sleep(0.1)

    return driver


def close_link_tab(driver):
    # Closing new_url tab
    driver.close()

    # Switching to old tab
    driver.switch_to.window(driver.window_handles[0])
    return driver




def return_first_el(x):
    """
    Returns first element of list in each row - for each author (returns grouped and agg df)
    :param x:
    :return:
    """
    try:
        if type(x) == list:
            return x[0]
        else:
            return x
    except Exception as e:
        print(e)


def group_by_email(df):
    # returns grouped and agg df
    return df.groupby('email').agg(lambda x: list(x) if (x.name not in ['name', 'surname']) else x[0])
