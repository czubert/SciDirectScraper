import os
import time

import pandas as pd
import streamlit as st
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

import constants
import data_processing
import pagination
import utils
from article import Article


class ScienceDirectParser:
    def __init__(self, window='maximized', keyword='SERS', pub_per_page_multi25=1, requested_num_of_publ=2,
                 years=tuple([2022])):
        # Parsing
        self.start_time = None
        self.parser_url = ''
        self.core_url = 'https://www.sciencedirect.com/search?qs='
        self.next_class_name = 'next'
        self.soup = None
        self.articles_urls = []
        self.window = window
        # searching parameters
        self.keyword = keyword
        self.pub_per_page = 25 * pub_per_page_multi25
        self.requested_num_of_publ = requested_num_of_publ
        self.years = years
        # Saving
        self.csv_file = None
        self.file_name = None
        self.authors_collection = None
        self.coll_csv_buff = None  # for streamlit download button
        self.coll_xlsx_buff = None  # for streamlit download button

    def create_parser_url(self):
        years = [str(x) for x in self.years]
        url_years = "%2c".join(years)
        offset = 0
        self.parser_url = f'{self.core_url}{self.keyword}&years={url_years}&show={self.pub_per_page}&offset={offset}'

    def get_articles_urls(self, driver, open_browser_sleep, pagination_sleep):
        st.sidebar.subheader("Extracting urls:")
        driver.get(self.parser_url)
        time.sleep(open_browser_sleep)  # sleep so the browser has time to open

        wait = WebDriverWait(driver, 5)

        pub_categories = pagination.check_if_more_pubs_than_limit(driver)

        try:
            show_more_btn = pub_categories.find_elements(By.XPATH, "(//span[@class='facet-link'])")[0]
            show_more_btn.click()
        except IndexError as e:
            print(f'Index error in get articles urls: {e}')

        # Depending on if the number of available publications exceeds 1000,
        # pagination goes through years/pub title categories
        pagination_args = [pub_categories, self.requested_num_of_publ, self.pub_per_page, self.articles_urls,
                           self.next_class_name, driver, wait, pagination_sleep]

        pagination.paginate_through_cat(*pagination_args)

    def parse_articles(self, driver):
        st.sidebar.subheader("Parsing authors data:")
        progress_bar = st.sidebar.progress(0)

        """
        If requested number of publications is 0 - all, 
        then we change the overall number of requested publications,
        to the number of all publications
        """
        if self.requested_num_of_publ == 0:
            self.requested_num_of_publ = len(self.articles_urls)

        # Goes through parsed urls to scrap the corresponding authors data
        for i, pub_url in enumerate(tqdm(self.articles_urls[:self.requested_num_of_publ])):
            parsed_article = Article(pub_url)
            parsed_article.parse_article(driver, btn_click_sleep=0.01)
            # self.add_records_to_collection(parsed_article.article_data_df)
            self.add_records_to_file(parsed_article.article_data_df)

            # Information about the progress
            progress_bar.progress((i + 1) / self.requested_num_of_publ)

    def add_records_to_collection(self, record):
        self.authors_collection = pd.concat((self.authors_collection, record))

    def add_records_to_file(self, record):
        path = 'output/partial/'

        if not os.path.isdir(path):
            os.mkdir(path)

        if len(self.years) == 1:
            year = str(self.years[0])
        else:
            years = sorted(self.years)
            year = f'{years[0]}-{years[-1]}'

        self.file_name = f'{path}{self.keyword}__{year}__{self.start_time}.csv'

        if not os.path.isfile(self.file_name):
            record.to_csv(self.file_name, mode='a', index='email', header=constants.COLUMNS)
        else:
            record.to_csv(self.file_name, mode='a', index='email', header=False)

    def scrap(self):
        # Program start time

        self.start_time = utils.get_current_time()

        # DataFrame to collect all corresponding authors
        self.authors_collection = utils.create_named_dataframe()

        # Creates an initial URL for parsing
        self.create_parser_url()

        """
        Driver initialization and data parsing
        """
        driver = utils.initialize_driver(self.window)

        # Opens search engine from initial URL. Parse all publications urls page by page
        self.get_articles_urls(driver, open_browser_sleep=1.0, pagination_sleep=0.4)

        # Takes opened driver and opens each publication in a new tab
        self.parse_articles(driver)

        """
        Data Processing         
        """
        self.authors_collection = data_processing.data_processing(pd.read_csv(self.file_name))

        """
        Writing final version to a file
        """
        self.authors_collection = self.authors_collection.sort_values(by=['year', 'num_of_publications'],
                                                                      ascending=False)

        self.csv_file = utils.write_data_to_file(self.authors_collection, self.file_name)

        # todo delete after deleting download button from streamlit
        # self.coll_xlsx_buff, self.coll_csv_buff = utils.write_xls_csv_to_buffers(self.authors_collection)


if __name__ == '__main__':
    science = ScienceDirectParser(keyword='y. sheena mary', pub_per_page_multi25=4, requested_num_of_publ=5,
                                  years=[x for x in range(2010, 2023)])

    science.scrap()
