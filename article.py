import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService

from author import Author


class Article:
    def __init__(self, url):
        self.url = url
        self.paper_title = ''
        self.doi = ''
        self.corr_authors = []
        self.driver = None

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
        try:
            for title in soup.find('title'):
                self.paper_title = title
        except Exception as e:
            print(f'Getting article title failed! Reason?: {e}')
        try:
            for doi in soup.find('a', {'class': "doi"}):
                self.doi = doi
        except Exception as e:
            print(f'Getting article DOI failed! Reason?: {e}')

    def get_author_meta(self, data):
        author = Author()
        author.get_author_meta(data)
        if author.email:
            self.corr_authors.append(author)

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

        except NoSuchElementException:
            pass


if __name__ == '__main__':
    url = 'https://www.sciencedirect.com/science/article/pii/S0021979722022470'
    art = Article(url)
    art.parse_article()
