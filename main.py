import re
import time
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService

# # needed only once for installation
# from webdriver_manager.microsoft import EdgeChromiumDriverManager
# driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))

driver = webdriver.Edge(service=EdgeService())

# driver.get('https://www.sciencedirect.com/science/article/pii/S1571065308000656')
driver.get('https://www.sciencedirect.com/science/article/pii/S0021979722022470')
time.sleep(1)

try:
    button = driver.find_elements(By.CLASS_NAME, 'workspace-trigger')
    # button = driver.find_element(By.CSS_SELECTOR, ".show-hide-details.u-font-sans")
    emails = []
    for el in button:
        actions = ActionChains(driver)
        actions.click(el)
        actions.perform()

        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        #TODO delete it at the end. Part responsible for checking information
        # with open(f'{time.time()}_author.txt', 'wb') as f:
        #     f.write(soup.prettify().encode('UTF-8'))
        # print(soup.prettify())

        try:
            for data in soup.find_all('div', {'class': 'e-address'}):
                email = data.find('a').get('href')
                if email is not None:
                    if re.match(r'.+@.+\..+', email):
                        email = re.search(r'(?<=mailto:)(.+)@(.+)\.(.+)', email).group()
                        emails.append(email)
                else:
                    continue
            print(emails)
        except Exception as e:
            print(e)
            continue

except NoSuchElementException:
    pass
