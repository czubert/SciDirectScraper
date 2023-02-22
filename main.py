import os
import time

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

import constants
import utils
from tools import pagination, driver, data_processing
from tools.article import Article


class ScienceDirectParser:
    def __init__(self, window='Maximized', keyword='SERS', requested_num_of_publ=2,
                 years=tuple([2022])):
        # Parsing
        self.driver = None
        self.start_time = None
        self.parser_url = ''
        self.core_url = 'https://www.sciencedirect.com/search?qs='
        self.soup = None
        self.articles_urls = []
        self.window = window
        # searching parameters
        self.keyword = keyword
        self.pub_per_page = 100
        self.num_of_pages = None
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

    def get_articles_urls(self, open_browser_sleep, pagination_sleep):
        self.driver.get(self.parser_url)  # invoking driver - opening website

        time.sleep(open_browser_sleep)  # sleep so the browser has time to open

        wait = WebDriverWait(self.driver, 10)

        # Checks if limit of 1000 publications is exceeded, returns also the number of all papers
        num_of_all_papers = pagination.get_max_num_of_publications(self.driver)

        # checks if the number of pages for pagination is limited, also returns num of pages
        limited_num_of_pages, self.num_of_pages = pagination.number_of_pages_is_limited(self.driver, num_of_all_papers)

        if num_of_all_papers < self.requested_num_of_publ:
            self.requested_num_of_publ = num_of_all_papers

        # If requested number of publications or all available publications is less than 1000

        if 0 < self.requested_num_of_publ <= 1000 or num_of_all_papers <= (
                self.pub_per_page * self.num_of_pages) or not limited_num_of_pages:
            req_num_of_pages = self.requested_num_of_publ // 100 + 1
            pagination_args = [self.requested_num_of_publ, self.articles_urls,
                               self.driver, wait, pagination_sleep, req_num_of_pages]

            pagination.paginate(*pagination_args)
        else:
            # If the number of available publications > 100 * num_of_pages, pagination goes through pub title categories
            categories_num = [2, 3, 4, 5]  # index of the categories on website
            for el in categories_num:
                print(el)
                print(20*'=')
                pub_categories = pagination.get_pub_categories(self.driver, el)

                pagination_args = [pub_categories, self.requested_num_of_publ, self.articles_urls,
                                   self.driver, wait, pagination_sleep]
                pagination.paginate_through_cat(*pagination_args)

    def parse_articles(self, btn_click_sleep, pbar=None):
        """
        If requested number of publications is 0 - all, 
        then we change the overall number of requested publications,
        to the number of all publications
        """
        # Getting rid of duplicates
        self.articles_urls = list(set(self.articles_urls))
        if self.requested_num_of_publ == 0:
            self.requested_num_of_publ = len(self.articles_urls)

        # Goes through parsed urls to scrap the corresponding authors data
        for i, pub_url in enumerate(
                tqdm(self.articles_urls[:self.requested_num_of_publ], desc="Publications completed")):
            parsed_article = Article(pub_url)
            parsed_article.parse_article(self.driver, sleep=btn_click_sleep)
            # self.add_records_to_collection(parsed_article.article_data_df)
            self.add_records_to_file(parsed_article.article_data_df)

            # Information about the progress (from streamlit)
            if pbar is not None:
                pbar.progress((i + 1) / self.requested_num_of_publ)

        self.driver.close()

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
            record.to_csv(self.file_name, mode='a', header=constants.COLUMNS)
        else:
            record.to_csv(self.file_name, mode='a', header=False)

    def parser_initialization(self):
        # Program start time
        self.start_time = utils.get_current_time()

        # DataFrame to collect all corresponding authors
        self.authors_collection = utils.create_named_dataframe()

        # Creates an initial URL for parsing
        self.create_parser_url()

        # Driver initialization
        self.driver = driver.initialize_driver(self.window)

    def data_postprocessing(self):
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

    def scrap(self):
        try:
            self.parser_initialization()
            # Opens search engine from initial URL. Parse all publications urls page by page
            self.get_articles_urls(open_browser_sleep=1.5, pagination_sleep=0.7)

            # # Takes opened driver and opens each publication in a new tab
            self.parse_articles(btn_click_sleep=0.25)

        except Exception as e:
            print(f'Exception in main(): {e}')
        finally:
            self.data_postprocessing()


if __name__ == '__main__':
    science = ScienceDirectParser(keyword='sers', requested_num_of_publ=0,
                                  years=[x for x in range(2022, 2023)])

    science.scrap()
