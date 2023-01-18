import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service as EdgeService


class ScienceDirectParser:
    def __init__(self, keyword='SERS', pub_per_page_multi25=1, n_pages=2, years=[2022]):
        self.keyword = keyword
        self.pub_per_page = 25
        self.pub_per_page_multi25 = pub_per_page_multi25
        self.n_pages = n_pages
        self.years = years
        self.parser_url = ''
        self.core_url = 'https://www.sciencedirect.com/search?qs='
        self.articles_urls = []
        self.soup = None

    def create_url(self, page_num):
        years = [str(x) for x in self.years]
        url_years = "%2c".join(years)
        pub_per_page = self.pub_per_page * self.pub_per_page_multi25
        offset = (page_num-1) * pub_per_page
        self.parser_url = f'{self.core_url}{self.keyword}&years={url_years}&show={pub_per_page}&offset={offset}'

    def get_articles_urls(self):
        try:
            driver = webdriver.Edge(service=EdgeService())
        except Exception:  # todo sprawdzić jakie
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))

        driver.get("https://www.sciencedirect.com/search?qs=SERS&show=25")
        wait = WebDriverWait(driver, 5)

        # store all the links in a list
        self.articles_urls += [item.get_attribute("href") for item in wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "subtype-srctitle-link")))]

    def scrap(self):
        for page_num in range(1, self.n_pages + 1):
            print(page_num)
            self.create_url(page_num)
            self.get_articles_urls()
            # print(self.articles_urls)
            # print(len(self.articles_urls))
            print(self.parser_url)


if __name__ == '__main__':
    science = ScienceDirectParser(keyword='SERS', pub_per_page_multi25=2, n_pages=2, years=[2022, 2021])
    science.scrap()
