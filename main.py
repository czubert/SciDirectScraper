import time

import pandas as pd
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService

import utils
from article import Article


class ScienceDirectParser:
    def __init__(self, keyword='SERS', pub_per_page_multi25=1, requested_num_of_publ=2, years=[2022]):
        # Parsing
        self.parser_url = ''
        self.core_url = 'https://www.sciencedirect.com/search?qs='
        self.next_class_name = 'next-link'
        self.soup = None
        self.articles_urls = []
        # searching parameters
        self.keyword = keyword
        self.pub_per_page = 25 * pub_per_page_multi25
        self.requested_num_of_publ = requested_num_of_publ
        self.years = years
        # Saving
        self.csv_file = None
        self.file_name = None
        self.authors_collection = None
        self.parsed_articles = []
        self.parsed_articles_df = None
        self.coll_csv_buff = None  # for streamlit download button
        self.coll_xlsx_buff = None  # for streamlit download button

    def create_parser_url(self):
        years = [str(x) for x in self.years]
        url_years = "%2c".join(years)
        offset = 0
        self.parser_url = f'{self.core_url}{self.keyword}&years={url_years}&show={self.pub_per_page}&offset={offset}'

    def get_articles_urls(self):
        st.sidebar.subheader("Extracting urls:")
        options = webdriver.ChromeOptions()
        # to open maximized window
        options.add_argument("start-maximized")
        # to supress the error messages/logs
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(service=ChromeService(), options=options)

        driver.get(self.parser_url)
        wait = WebDriverWait(driver, 5)

        if self.requested_num_of_publ == 0:
            n_loops = -1
        else:
            n_loops = (self.requested_num_of_publ // self.pub_per_page) + 1
        i = 0

        while i != n_loops:
            # Short break so the server do not block script
            time.sleep(0.1)

            # Parse web for urls
            self.articles_urls += [item.get_attribute("href") for item in wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "result-list-title-link")))]

            # Scrolls to the bottom to avoid 'feedback' pop-up
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            if utils.does_element_exist(driver, tag=self.next_class_name):
                wait.until(EC.visibility_of_element_located((By.CLASS_NAME, self.next_class_name))).click()
                info = f'{len(self.articles_urls)} addresses extracted'
                print(info)
                st.sidebar.write(info)
            else:
                break
            i += 1

    def parse_articles(self):
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
        for i, pub_url in enumerate(self.articles_urls[:self.requested_num_of_publ]):
            parsed_article = Article(pub_url)
            parsed_article.parse_article()
            self.parsed_articles.append(parsed_article)
            self.add_records_to_collection(parsed_article.article_data_df)

            # Information about the progress
            print(f'{i + 1}/{self.requested_num_of_publ} articles parsed')
            progress_bar.progress((i + 1) / self.requested_num_of_publ)

    def add_records_to_collection(self, record):
        self.authors_collection = pd.concat((self.authors_collection, record))

    def scrap(self):
        # DataFrame to collect all corresponding authors
        self.authors_collection = utils.create_named_dataframe()

        # creates an initial URL for parsing
        self.create_parser_url()

        with st.spinner('Wait while program is extracting publications urls...'):
            self.get_articles_urls()  # opens initial URL (SciDirect), and parse urls of all publications page by page
        st.sidebar.success(f'Total: {len(self.articles_urls)} addresses extracted')

        self.parse_articles()
        self.file_name = utils.build_filename(self.keyword, self.years, self.articles_urls, self.authors_collection)
        self.authors_collection = self.authors_collection.sort_values(by=['year'], ascending=False)
        self.csv_file = utils.write_data_coll_to_file(self.authors_collection, self.file_name)
        self.coll_xlsx_buff, self.coll_csv_buff = utils.write_xls_csv_to_buffers(self.authors_collection)


if __name__ == '__main__':
    science = ScienceDirectParser(keyword='SERSitive', pub_per_page_multi25=4, requested_num_of_publ=12,
                                  years=[x for x in range(2016, 2023)])

    # science = ScienceDirectParser(keyword='SERSitive', pub_per_page_multi25=1, n_pages=1,
    #                               years=[2021])
    science.scrap()
