import random
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService

import utils
from article import Article


class ScienceDirectParser:
    def __init__(self, keyword='SERS', pub_per_page_multi25=1, n_pages=2, years=[2022]):
        self.collection_xlsx_buffer = None
        self.csv_file = None
        self.file_name = None
        self.authors_collection = None
        self.keyword = keyword
        self.pub_per_page = 25
        self.pub_per_page_multi25 = pub_per_page_multi25
        self.n_pages = n_pages
        self.years = years
        self.parser_url = ''
        self.core_url = 'https://www.sciencedirect.com/search?qs='
        self.next_class_name = 'next-link'
        self.articles_urls = []
        self.soup = None
        self.offset = None
        self.parsed_articles = []
        self.parsed_articles_df = None

    def create_parser_url(self, page_num):
        years = [str(x) for x in self.years]
        url_years = "%2c".join(years)
        pub_per_page = self.pub_per_page * self.pub_per_page_multi25
        self.offset = (page_num - 1) * pub_per_page
        self.parser_url = f'{self.core_url}{self.keyword}&years={url_years}&show={pub_per_page}&offset={self.offset}'

    def get_articles_urls(self):
        driver = webdriver.Chrome(service=ChromeService())

        driver.get(self.parser_url)
        wait = WebDriverWait(driver, 1)

        while True:
            # Parse web for urls
            self.articles_urls += [item.get_attribute("href") for item in wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "result-list-title-link")))]
            time.sleep(random.random())

            # Scrolls to the bottom to avoid 'feedback' pop-up
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            if utils.does_element_exist(driver, tag=self.next_class_name):
                wait.until(EC.visibility_of_element_located((By.CLASS_NAME, self.next_class_name))).click()
                print(len(self.articles_urls))
                time.sleep(1)
            else:
                print('No more pages to parse')
                break

    def add_records_to_collection(self, record):
        self.authors_collection = pd.concat((self.authors_collection, record))

    def scrap(self):
        # TODO coś tu śmierdzi, nie ma ustawienia, żeby po prostu leciało, aż nie będzie błedu...
        self.authors_collection = utils.create_named_dataframe()
        for page_num in range(1, self.n_pages + 1):
            self.create_parser_url(page_num)  # todo tutaj coś nie gra - to jest chyba niepotrzebne
            self.get_articles_urls()  # todo tutaj tez cos nie gra, bo niby ograniczam ile razy ma iterować,
            # ale potem wrzucam go w while, który iteruje az mu sie nie skonczą strony. Wygląda na to,
            # że tutaj ta pętla for jest do wywalenia. trzeba tylko sprzedać do while,
            # że albo ma lecieć aż nie skończy, albo ma skończyć po iluś pętlach

            for i, pub_url in enumerate(self.articles_urls):
                parsed_article = Article(pub_url)
                parsed_article.parse_article()
                self.parsed_articles.append(parsed_article)
                self.add_records_to_collection(parsed_article.article_data_df)
                print(f'{i + 1}/{len(self.articles_urls)} parsed')
        self.file_name = utils.build_filename(self.keyword, self.years, self.articles_urls, self.authors_collection)
        self.authors_collection = self.authors_collection.sort_values(by=['year'], ascending=False)
        self.csv_file = utils.write_data_coll_to_file(self.authors_collection, self.file_name)
        self.collection_xlsx_buffer = utils.write_to_xlsx(self.authors_collection)


if __name__ == '__main__':
    science = ScienceDirectParser(keyword='SERSitive', pub_per_page_multi25=4, n_pages=1,
                                  years=[x for x in range(2016, 2023)])

    # science = ScienceDirectParser(keyword='SERSitive', pub_per_page_multi25=1, n_pages=1,
    #                               years=[2021])
    science.scrap()
