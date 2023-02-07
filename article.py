import re
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

import utils
from author import Author


class Article:
    def __init__(self, pub_url):
        self.year = None
        self.url = pub_url
        self.paper_title = ''
        self.doi = ''
        self.corr_authors = []
        self.article_data_df = None

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
                title = re.search('.+(?= - ScienceDirect)', title).group()
                self.paper_title = title
        except Exception as e:
            print(f'Getting article title failed! Reason?: {e}')

    def get_year(self, soup):
        try:
            for year in soup.find_all('div', {'class': 'text-xs'}):
                year = year.text
                if re.search(r'<!-- -->', year):
                    pattern = r'\d{4}(?=<!-- -->'
                    year = re.findall(pattern, year)
                elif re.search(r'\d{4}(?=,\s\d{6}$)', year):
                    pattern = r'\d{4}(?=,\s\d{6}$)'
                    year = re.findall(pattern, year)
                elif re.search(r'\d{4}(?=,\sPages)', year):
                    pattern = r'\d{4}(?=,\sPages)'
                    year = re.findall(pattern, year)
                elif re.search(r'^(Available).*(\d{4})$', year):
                    pattern = r'(\d{4})$'
                    year = re.findall(pattern, year)

                if len(year) > 0:
                    self.year = year[0]
                    break
        except Exception as e:
            print(f'Getting article year failed! Reason?: {e}')

    def get_author_meta(self, data):
        author = Author()
        author.get_author_meta(data)
        if author.email:
            self.corr_authors.append(author)

    def add_records_to_df(self):
        self.article_data_df = utils.create_named_dataframe()

        for author in self.corr_authors:
            df = pd.DataFrame({'name': author.first_name,
                               'surname': author.surname,
                               'email': author.email,
                               'affiliation': author.affiliation,
                               'publ_title': self.paper_title,
                               'doi': self.doi,
                               'year': self.year
                               }, index=[f'{author.surname.replace(" ", "_")}-{author.first_name.replace(" ", "_")}'])
            df.index.name = 'id'
            self.article_data_df = self.article_data_df.append(df)

    @staticmethod
    def click_author_buttons(driver, auth):
        actions = ActionChains(driver)
        actions.click(auth)
        try:
            actions.perform()
        except ElementNotInteractableException as e:
            print(f'clicking authors button failed:{e}')

    def parse_article(self, driver, sleep):
        try:
            driver = utils.open_link_in_new_tab(driver, self.url)
            button = driver.find_elements(By.XPATH, '//div[@class="author-group"]/button')
            for corr_author in button:  # Goes through all the authors )
                Article.click_author_buttons(driver, corr_author)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                for data in soup.find_all('div', {'class': 'WorkspaceAuthor'}):
                    self.get_article_meta(soup)
                    self.get_author_meta(data)
                time.sleep(sleep)
            utils.close_link_tab(driver)
            self.add_records_to_df()
        except NoSuchElementException:
            pass


if __name__ == '__main__':
    url = 'https://www.sciencedirect.com/science/article/pii/S000326701931462X'
    art = Article(url)
    art.parse_article(sleep=0.1)
