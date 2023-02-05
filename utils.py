import re
import time
import streamlit as st
import pandas as pd
from io import BytesIO
from tqdm import tqdm
# Selenium
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, InvalidSessionIdException
from selenium.webdriver.common.by import By

# Modules
import constants


def does_element_exist(driver, tag):
    try:
        element_exist = driver.find_element(By.LINK_TEXT, tag)  # .is_displayed()
    except NoSuchElementException:
        element_exist = False

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


def data_processing(df: pd.DataFrame):
    """
    Getting rid of repetitions and group by email
    :param df: pd.DataFrame
    :return: pd.DataFrame
    """
    df.drop_duplicates(inplace=True)

    # Groups authors by eamil
    df = group_by_email(df)

    # Returns num of a list in each row
    df['num_of_publications'] = [len(x) for x in df['publ_title']]

    # Getting only the first publication from all (and their details: year and affiliation)
    df = df.applymap(return_first_el)

    # Removing records of the same author with different email
    df = df.drop_duplicates(['name', 'surname'], keep='first')

    return df


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
