import time

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import http.cookiejar, urllib.request, sys
from urllib.parse import urlencode, quote_plus, urlparse


# from article import Article


class ScienceDirectParser:
    def __init__(self, keyword='SERS', n_per_page=25, pages=2):
        self.keyword = keyword
        self.n_per_page = n_per_page
        self.page_nums = pages
        self.parser_url = ''
        self.articles_urls = []
        self.soup = None

    def create_url(self, i):
        self.parser_url = f'https://www.sciencedirect.com/search?qs={self.keyword}&show={i * self.n_per_page}'

    def get_server_response(self):
        #TODO do wyjebania
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        payload = {'username': 'administrator', 'password': 'xyz'}
        result = urlencode(payload, quote_via=quote_plus)
        login_data = urlparse({'login': 'admin', 'pass': '123'})
        resp = opener.open('https://www.sciencedirect.com/search?qs=SERS&show=25', login_data)
        ua = str(UserAgent().opera)
        resp.addheaders = ua
        html = resp.read()
        print(html)

        # ua = str(UserAgent().opera)
        # headers = {'User-Agent': ua}
        # response = requests.get('https://www.sciencedirect.com/search?qs=SERS&show=25',
        #                         headers=headers)
        # if response.status_code == 200:
        #     self.soup = BeautifulSoup(response.content, 'html.parser')
        #     print(self.soup)
        # else:
        #     raise ConnectionError(response.status_code, response.raise_for_status())

    def get_articles_urls(self):
        for data in self.soup.find_all('a', {'class': 'anchor-default'}):
            self.articles_urls.append(data.get('href'))

    def scrap(self):
        for page_num in range(1, self.page_nums + 1):
            self.create_url(page_num)
            try:
                time.sleep(1)
                self.get_server_response()
                time.sleep(1)
            except ConnectionError as e:
                print(e)
                continue
            self.get_articles_urls()
            print(self.articles_urls)


if __name__ == '__main__':
    science = ScienceDirectParser()
    science.scrap()
