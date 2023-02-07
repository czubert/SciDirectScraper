import datetime
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


def does_element_exist(driver, tag):
    try:
        element_exist = driver.find_element(By.LINK_TEXT, tag)  # .is_displayed()
    except NoSuchElementException:
        element_exist = False

    return element_exist


def open_link_in_new_tab(driver, url):
    # Open a new tab
    driver.execute_script("window.open('');")

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
