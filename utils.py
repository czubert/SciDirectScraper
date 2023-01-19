import pandas
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import constants


def does_element_exist(driver, tag):
    try:
        element_exist = driver.find_element(By.CLASS_NAME, tag).is_displayed()
    except NoSuchElementException:
        element_exist = False
        print("Pagination: all pages parsed")

    return element_exist


def write_data_coll_to_file(df: pandas.DataFrame):
    df.to_csv('collection.csv', sep=';')  # todo add possibility to change sep (not windows)


def create_named_dataframe():
    columns = constants.COLUMNS
    df = pd.DataFrame(columns=columns)
    df.index.name = 'id'
    return df
