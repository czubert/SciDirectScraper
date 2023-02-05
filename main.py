import re
import time

import pandas as pd
import streamlit as st
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from tqdm import tqdm

import utils
from article import Article


class ScienceDirectParser:
    def __init__(self, window='maximized', keyword='SERS', pub_per_page_multi25=1, requested_num_of_publ=2,
                 years=tuple([2022])):
        # Parsing
        self.authors_collection = None
        self.link = None
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
        self.parsed_articles = []
        self.parsed_articles_df = None
        self.coll_csv_buff = None  # for streamlit download button
        self.coll_xlsx_buff = None  # for streamlit download button

    def create_parser_url(self):
        years = [str(x) for x in self.years]
        url_years = "%2c".join(years)
        offset = 0
        self.parser_url = f'{self.core_url}{self.keyword}&years={url_years}&show={self.pub_per_page}&offset={offset}'

    def get_articles_urls(self, driver):
        st.sidebar.subheader("Extracting urls:")
        driver.get(self.parser_url)

        wait = WebDriverWait(driver, 5)
        time.sleep(0.9)
        years_pub_nums = driver.find_elements(By.XPATH, "(//div[@class='FacetItem'])[1]/fieldset/ol")[0]

        num_of_papers = 0
        papers = years_pub_nums.text.split()
        for i in range(1, len(papers), 2):
            num_of_papers += int(re.sub(r'([()])*', '', papers[i]))

        # If there is less than 1000 publications, then it is not looping through pub_categories.
        if num_of_papers < 1000:
            pub_categories = years_pub_nums
        else:
            pub_categories = driver.find_elements(By.XPATH, "(//div[@class='FacetItem'])[3]/fieldset/ol")[0]

        try:
            show_more_btn = pub_categories.find_elements(By.XPATH, "(//span[@class='facet-link'])")[0]
            show_more_btn.click()
        except IndexError:
            pass

        options = pub_categories.find_elements(By.TAG_NAME, 'li')

        for option in options:
            try:
                option.click()  # select box

                pagination_args = [self.requested_num_of_publ, self.pub_per_page, self.articles_urls,
                                   self.next_class_name, driver, wait]

                driver = utils.paginate(*pagination_args)

                option.click()  # unselect box

            except StaleElementReferenceException:
                pass

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
            parsed_article.parse_article(driver)
            self.parsed_articles.append(parsed_article)
            self.add_records_to_collection(parsed_article.article_data_df)

            # Information about the progress
            progress_bar.progress((i + 1) / self.requested_num_of_publ)

    def add_records_to_collection(self, record):
        self.authors_collection = pd.concat((self.authors_collection, record))
        # todo zrobic odczyt i zapis z pliku, zeby dodac nowe linijki i zapisac

    def scrap(self):
        # DataFrame to collect all corresponding authors
        self.authors_collection = utils.create_named_dataframe()

        # Creates an initial URL for parsing
        self.create_parser_url()

        # # # Beginning "Initialize driver" # # #
        driver = utils.initialize_driver(self.window)

        # Opens search engine from initial URL. Parse all publications urls page by page
        with st.spinner('Wait while program is extracting publications urls...'):
            self.get_articles_urls(driver)
        # progressbar at sidebar
        st.sidebar.success(f'Total: {len(self.articles_urls)} addresses extracted')

        # Takes opened driver and opens each publication in a new tab
        self.parse_articles(driver)
        driver.close()
        # # # End "Initialize driver" # # #

        # Data Processing, to get rid of repetitions and group by email - so one email appear only once in database
        utils.data_processing(self.authors_collection)

        self.authors_collection = utils.group_by_email(self.authors_collection)

        # returns num of a list in each row
        self.authors_collection['num_of_publications'] = [len(x) for x in self.authors_collection['publ_title']]

        # returns first element of list in each row (returns grouped and agg df)
        def return_first_el(x):
            try:
                if type(x) == list:
                    return x[0]
                else:
                    return x
            except Exception as e:
                print(e)

        # Getting only the first publication from all (and their details: year and affiliation)
        self.authors_collection = self.authors_collection.applymap(return_first_el)

        # If someone has different email, but the same name and surname
        self.authors_collection = self.authors_collection.drop_duplicates(['name', 'surname'], keep='first')

        # writing to a file
        self.file_name = utils.build_filename(self.keyword, self.years, self.articles_urls, self.authors_collection)
        self.authors_collection = self.authors_collection.sort_values(by=['year'], ascending=False)
        self.csv_file = utils.write_data_coll_to_file(self.authors_collection, self.file_name)
        self.coll_xlsx_buff, self.coll_csv_buff = utils.write_xls_csv_to_buffers(self.authors_collection)


if __name__ == '__main__':
    science = ScienceDirectParser(keyword='y. sheena mary', pub_per_page_multi25=4, requested_num_of_publ=15,
                                  years=[x for x in range(2021, 2023)])

    # science = ScienceDirectParser(keyword='SERSitive', pub_per_page_multi25=1, n_pages=1,
    #                               years=[2021])
    science.scrap()
