import pandas
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import constants
from io import BytesIO


def does_element_exist(driver, tag):
    try:
        element_exist = driver.find_element(By.CLASS_NAME, tag)  # .is_displayed()
    except NoSuchElementException:
        element_exist = False
        print("Pagination: all pages parsed")

    return element_exist


def write_data_coll_to_file(df: pandas.DataFrame, file_name: str):
    import os
    path = 'output'
    if not os.path.isdir(path):
        os.mkdir(path)

    df.to_excel(f'{path}/{file_name}.xlsx')
    df.to_csv(f'{path}/{file_name}.csv', encoding='utf-16')


def write_xls_csv_to_buffers(df: pandas.DataFrame):
    return write_xlsx_to_buffer(df), write_csv_to_buffer(df)


def write_xlsx_to_buffer(df: pandas.DataFrame):
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer)

        writer.save()
        writer.close()

    return buffer


def write_csv_to_buffer(df: pandas.DataFrame):
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
