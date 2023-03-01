import datetime
import os

import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

# Modules
import constants


def get_current_time():
    now = datetime.datetime.now()

    return f'{now.year}_{now.month}_{now.day}-{now.hour}h_{now.minute}min'


def write_data_to_file(df: pd.DataFrame, file_name: str):
    df.to_excel(f'{file_name[:-4]}.xlsx')
    df.to_csv(f'{file_name[:-4]}.csv', encoding='utf-16')


def create_named_dataframe():
    columns = constants.COLUMNS
    df = pd.DataFrame(columns=columns)
    df.index.name = 'id'
    return df


def does_link_text_exist(driver, tag):
    try:
        element_exist = driver.find_element(By.LINK_TEXT, tag)  # .is_displayed()
    except NoSuchElementException:
        element_exist = False

    return element_exist


def does_tag_exist(driver, tag):
    try:
        element_exist = driver.find_element(By.TAG_NAME, tag)  # .is_displayed()
    except NoSuchElementException:
        element_exist = False

    return element_exist


def get_num_of_pages(driver):
    return int(driver.find_element(By.CLASS_NAME, 'Pagination').text.split()[-1].replace('next', ''))


def open_link_in_new_tab(driver, url):
    # Open a new tab
    try:
        driver.execute_script("window.open('');")
    except Exception as e:
        print(e)

    # Switch to the new tab and open new URL
    driver.switch_to.window(driver.window_handles[1])
    driver.get(url)

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


def check_if_dir_exists(dir_name):
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)


def write_urls_to_file(urls, dir_name, urls_name):
    check_if_dir_exists(dir_name)

    with open(f'{dir_name}/{urls_name}', 'w+') as f:
        for el in urls:
            f.write(el + ',')


def read_urls(urls_path):
    with open(urls_path, 'r') as f:
        return f.readlines()[0].split(',')
