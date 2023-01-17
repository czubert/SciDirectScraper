import re
import time
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
import json

# # needed only once for installation
# from webdriver_manager.microsoft import EdgeChromiumDriverManager
# driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))

driver = webdriver.Edge(service=EdgeService())

# driver.get('https://www.sciencedirect.com/science/article/pii/S1571065308000656')  # first auth == corr
# driver.get('https://www.sciencedirect.com/science/article/pii/S0021979722022470')  # last auth == corr
driver.get('https://www.sciencedirect.com/science/article/pii/S0925400522018937')  # two auth == corr
time.sleep(1)

try:
    button = driver.find_elements(By.CLASS_NAME, 'workspace-trigger')
    for el in button:  # Goes thru all the authors
        actions = ActionChains(driver)
        actions.click(el)
        actions.perform()

        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        #TODO delete it at the end. Part responsible for checking information
        # with open(f'{time.time()}_author.txt', 'wb') as f:
        #     f.write(soup.prettify().encode('UTF-8'))


        try:
            # for data in soup.find_all('div', {'class': 'e-address'}):
            for data in soup.find_all('div', {'class': 'WorkspaceAuthor'}):
                #todo usunąć
                print()
                for mail in data.find_all_next('div', {'class': 'e-address'}):
                    email = mail.find('a').get('href')

                try:
                    for name in data.find('span', {'class': "given-name"}):
                        print(name)
                except Exception as e:
                    print(f'Something went wrong my Lord! Probably this: {e}')
                try:
                    for surname in data.find('span', {'class': "surname"}):
                        print(surname)
                except Exception as e:
                    print(f'Something went wrong my Lord! Probably this: {e}')
                try:
                    for title in soup.find('title'):
                        print(title)
                except Exception as e:
                    print(f'Something went wrong my Lord! Probably this: {e}')
                try:
                    for doi in soup.find('a', {'class': "doi"}):
                        print(doi)
                except Exception as e:
                    print(f'Something went wrong my Lord! Probably this: {e}')

                try:
                    for aff in data.find('div', {'class': "affiliation"}):
                        if len(aff) > 0:
                            print(aff)
                except Exception as e:
                    print(f'Something went wrong my Lord! Probably this: {e}')

                if re.match(r'.+@.+\..+', email):
                    email = re.search(r'(?<=mailto:)(.+)@(.+)\.(.+)', email).group()
                    print(email)

        except Exception as e:
            print(e)
            continue

except NoSuchElementException:
    pass
