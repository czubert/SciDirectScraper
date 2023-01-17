import re
import time
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService

base_link = 'https://www.sciencedirect.com/search?qs=sers&show=100'
elsevier_link_over_hundred = 'https://www.sciencedirect.com/search?qs=sers&show=100&offset=100'


class Article:
    def __init__(self, url):
        self.url = url
        self.paper_title = ''
        self.doi = ''
        self.corr_authors = []
        self.driver = None

    def get_driver(self, sleep=1):
        # # needed only once for installation
        # from webdriver_manager.microsoft import EdgeChromiumDriverManager
        # driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))

        self.driver = webdriver.Edge(service=EdgeService())

        self.driver.get(self.url)  # two auth == corr
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

    def parse_article(self):
        try:
            self.get_driver(sleep=1)
            button = self.driver.find_elements(By.CLASS_NAME, 'workspace-trigger')
            for corr_author in button:  # Goes thru all the authors )
                self.click_author_buttons(corr_author, sleep=1)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                for data in soup.find_all('div', {'class': 'WorkspaceAuthor'}):
                    self.get_article_meta(soup)
                    author = Author()
                    author.get_author_meta(data)
                    self.corr_authors.append(author)

        except NoSuchElementException:
            pass


class Author:
    def __init__(self):
        self.first_name = ''
        self.surname = ''
        self.email = ''
        self.affiliation = ''

    def get_author_meta(self, data):
        try:
            for mail in data.find_all_next('div', {'class': 'e-address'}):
                print('dupa')
                email = mail.find('a').get('href')
                print('lupa')
                if re.match(r'.+@.+\..+', email):
                    print('kupa')
                    self.email = re.search(r'(?<=mailto:)(.+)@(.+)\.(.+)', email).group()
        except Exception as e:
            print(f'Getting e-mail failed! Reason?: {e}')
        try:
            for name in data.find('span', {'class': "given-name"}):
                self.first_name = name
        except Exception as e:
            print(f'Getting given name failed! Reason?: {e}')
        try:
            for surname in data.find('span', {'class': "surname"}):
                self.surname = surname
        except Exception as e:
            print(f'Getting surname failed! Reason?: {e}')


if __name__ == '__main__':
    # given_url = 'https://www.sciencedirect.com/science/article/pii/S1571065308000656'  # first auth == corr
    # given_url = 'https://www.sciencedirect.com/science/article/pii/S0021979722022470'  # last auth == corr
    given_url = 'https://www.sciencedirect.com/science/article/pii/S0925400522018937'  # two auth == corr

    science = Article(given_url)
    science.parse_article()
