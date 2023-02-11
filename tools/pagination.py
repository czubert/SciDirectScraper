import re
import time
from tqdm import tqdm

# Selenium
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidSessionIdException, StaleElementReferenceException
from selenium.webdriver.common.by import By

import constants
# Modules
import utils


def check_if_more_pubs_than_limit(driver, num_of_requested_pubs):
    """
    There is a limit of publications to parse per one link = 1000.
    This function returns categories of publications if the limit is exceeded.
    If it is not it returns publications per year
    :param num_of_requested_pubs:
    :param driver: Selenium Webdriver
    :return: list
    """
    # number of publications per year
    pub_numbs_per_year = driver.find_elements(By.XPATH, "(//div[@class='FacetItem'])[1]/fieldset/ol")[0]

    max_num_of_papers = 0
    papers = pub_numbs_per_year.text.split()

    for i in range(1, len(papers), 2):
        try:
            max_num_of_papers += int(re.sub(r'([()])*', '', papers[i]).replace(',', ''))
            if max_num_of_papers > 1000:
                break
        except ValueError:
            continue

        # If there is less than 1000 publications, then it is not looping through pub_categories.
        if max_num_of_papers <= 1000:
            pub_categories = pub_numbs_per_year

        else:
            pub_categories = driver.find_elements(By.XPATH, "(//div[@class='FacetItem'])[3]/fieldset/ol")[0]

        return pub_categories


def paginate_through_cat(pub_categories, requested_num_of_publ, pub_per_page, articles_urls,
                         driver, wait, pagination_sleep):
    # Gets the publications categories
    options = pub_categories.find_elements(By.TAG_NAME, 'li')

    # Paginate through all categories of publications
    for option in options:
        try:
            option.click()  # select box

            pagination_args = [requested_num_of_publ, pub_per_page, articles_urls,
                               driver, wait, pagination_sleep]

            driver = paginate(*pagination_args)

            option.click()  # unselect box

        except StaleElementReferenceException:
            pass


def paginate(requested_num_of_publ, pub_per_page, articles_urls, driver, wait, pagination_sleep, tab_opened=False):
    next_btn = constants.NEXT_CLASS_NAME
    progress_bar_limit = 10

    if requested_num_of_publ == 0:
        n_loops = -1
    else:
        n_loops = (requested_num_of_publ // pub_per_page) + 1
        progress_bar_limit = n_loops
    i = 0

    progress = tqdm(desc='Pagination', total=progress_bar_limit)

    while i != n_loops:

        # Update output progressbar
        progress.update(1)

        # Short break so the server do not block script
        time.sleep(pagination_sleep)  # important: lower than 0.8s values result in error

        # Parse web for urls
        articles_urls += [item.get_attribute("href") for item in wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "result-list-title-link")))]

        # "next" button not available, there is less than 100 pubs for given parameters, so all fit in one page
        if n_loops == 1:
            return driver

        # Scrolls to the bottom to avoid 'feedback' pop-up
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Opens new tab. As "next" button available - there is more than 100 pubs for given params. And tab is closed
        if utils.does_element_exist(driver, tag=next_btn):
            if not tab_opened:
                # Opening 'next button' in new tab instead of clicking it, so the pub categories do not hide
                url = wait.until(EC.presence_of_element_located((By.LINK_TEXT, next_btn))).get_attribute('href')
                driver = utils.open_link_in_new_tab(driver, url)
                tab_opened = True
                continue
            if n_loops != 1:
                wait.until(EC.presence_of_element_located((By.LINK_TEXT, next_btn))).click()

        else:
            try:
                driver = utils.close_link_tab(driver)
            except InvalidSessionIdException:
                pass
            finally:
                return driver

        i += 1
    progress.close()
