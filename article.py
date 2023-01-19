import re
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService

import constants
from author import Author


class Article:
    def __init__(self, url):
        self.year = None
        self.url = url
        self.paper_title = ''
        self.doi = ''
        self.driver = None
        self.corr_authors = []
        self.article_data_df = None

    def get_driver(self, sleep=1):
        self.driver = webdriver.Chrome(service=ChromeService())

        self.driver.get(self.url)
        time.sleep(sleep)

    def click_author_buttons(self, auth, sleep=1):
        actions = ActionChains(self.driver)
        actions.click(auth)
        actions.perform()
        time.sleep(sleep)

    def get_article_meta(self, soup):
        self.get_doi(soup)
        self.get_title(soup)
        self.get_year(soup)

    def get_doi(self, soup):
        try:
            for doi in soup.find('a', {'class': "doi"}):
                self.doi = doi
        except Exception as e:
            print(f'Getting article DOI failed! Reason?: {e}')

    def get_title(self, soup):
        try:
            for title in soup.find('title'):
                self.paper_title = title
        except Exception as e:
            print(f'Getting article title failed! Reason?: {e}')

    def get_year(self, soup):
        try:
            for year in soup.find_all('div', {'class': 'text-xs'}):
                # print(year.text)
                pattern = r'\d{4}(?=<\!-- -->)'
                year = re.findall(pattern, year.text)
                # print(year)
                if len(year) > 0:
                    self.year = year
                    print(year)
                    break

        except Exception as e:
            print(f'Getting article title failed! Reason?: {e}')

    def get_author_meta(self, data):
        author = Author()
        author.get_author_meta(data)
        if author.email:
            self.corr_authors.append(author)

    def add_records_to_df(self):
        columns = constants.COLUMNS
        self.article_data_df = pd.DataFrame(columns=columns)

        for author in self.corr_authors:
            df = pd.DataFrame({'name': author.first_name,
                               'surname': author.surname,
                               'email': author.email,
                               'affiliation': author.affiliation,
                               'publ_title': self.paper_title,
                               'doi': self.doi
                               }, index=[f'{author.surname}_{author.first_name}'])
            self.article_data_df = self.article_data_df.append(df)

    def parse_article(self):
        try:
            self.get_driver(sleep=1)
            button = self.driver.find_elements(By.CLASS_NAME, 'workspace-trigger')
            for corr_author in button:  # Goes through all the authors )
                self.click_author_buttons(corr_author, sleep=1)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                for data in soup.find_all('div', {'class': 'WorkspaceAuthor'}):
                    self.get_article_meta(soup)
                    self.get_author_meta(data)

            self.add_records_to_df()
        except NoSuchElementException:
            pass


if __name__ == '__main__':
    # url = 'https://www.sciencedirect.com/science/article/pii/S0021979722022470'
    url = 'https://www.sciencedirect.com/science/article/pii/S000326701931462X'
    art = Article(url)
    art.parse_article()