import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService

import utils
from article import Article


class ScienceDirectParser:
    def __init__(self, keyword='SERS', pub_per_page_multi25=1, n_pages=2, years=[2022]):
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

    def create_url(self, page_num):
        years = [str(x) for x in self.years]
        url_years = "%2c".join(years)
        pub_per_page = self.pub_per_page * self.pub_per_page_multi25
        self.offset = (page_num - 1) * pub_per_page
        self.parser_url = f'{self.core_url}{self.keyword}&years={url_years}&show={pub_per_page}&offset={self.offset}'

    def get_articles_urls(self):
        driver = webdriver.Chrome(service=ChromeService())

        driver.get(self.parser_url)
        wait = WebDriverWait(driver, 3)

        while True:
            # Parse web for urls
            self.articles_urls += [item.get_attribute("href") for item in wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "result-list-title-link")))]
            time.sleep(1)

            # Scrolls to the bottom to avoid 'feedback' pop-up
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            if utils.does_element_exist(driver, tag=self.next_class_name):
                wait.until(EC.visibility_of_element_located((By.CLASS_NAME, self.next_class_name))).click()
                print(len(self.articles_urls))
                time.sleep(1)
            else:
                print('No more pages to scroll')
                break

    def scrap(self):
        for page_num in range(1, self.n_pages + 1):
            self.create_url(page_num)
            self.get_articles_urls()
            # for pub_url in self.articles_urls[:3]:
            #     article = Article(pub_url)
            #     article.parse_article()


if __name__ == '__main__':
    science = ScienceDirectParser(keyword='SERS', pub_per_page_multi25=1, n_pages=1,
                                  years=[x for x in range(1940, 2023)])
    science.scrap()
