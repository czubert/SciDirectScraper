import re
import time
from tqdm import tqdm

# Selenium
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidSessionIdException, StaleElementReferenceException
from selenium.webdriver.common.by import By

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

    if num_of_requested_pubs > 1000:
        num_of_papers = 0
        papers = pub_numbs_per_year.text.split()

        for i in range(1, len(papers), 2):
            try:
                num_of_papers += int(re.sub(r'([()])*', '', papers[i]).replace(',', ''))
                if num_of_papers > 1000:
                    break
            except ValueError:
                continue

        # If there is less than 1000 publications, then it is not looping through pub_categories.
        if num_of_papers <= 1000:
            pub_categories = pub_numbs_per_year
        else:
            pub_categories = driver.find_elements(By.XPATH, "(//div[@class='FacetItem'])[3]/fieldset/ol")[0]

        return pub_categories
    else:
        return pub_numbs_per_year


def paginate_through_cat(pub_categories, requested_num_of_publ, pub_per_page, articles_urls,
                         next_class_name, driver, wait, pagination_sleep):
    # Gets the publications categories
    options = pub_categories.find_elements(By.TAG_NAME, 'li')

    # Paginate through all categories of publications
    for option in options:
        try:
            option.click()  # select box

            pagination_args = [requested_num_of_publ, pub_per_page, articles_urls,
                               next_class_name, driver, wait]

            driver = paginate(*pagination_args)

            option.click()  # unselect box

        except StaleElementReferenceException:
            pass


def paginate(requested_num_of_publ, pub_per_page, articles_urls, next_class_name, driver, wait, tab=True):
    if requested_num_of_publ == 0:
        n_loops = -1
    else:
        n_loops = (requested_num_of_publ // pub_per_page) + 1

    n = 10
    i = 0

    progress = tqdm(desc='Pagination', total=n)

    while i != n_loops:

        # Short break so the server do not block script
        time.sleep(0.7)  # important: lower values result in error

        # Parse web for urls
        articles_urls += [item.get_attribute("href") for item in wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "result-list-title-link")))]

        # Update output progressbar
        progress.update(1)

        # Scrolls to the bottom to avoid 'feedback' pop-up
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        if not utils.does_element_exist(driver, tag=next_class_name) and tab is True:
            return driver

        elif utils.does_element_exist(driver, tag=next_class_name):
            if tab:
                # It is opening 'next button; in new tab instead of clicking it, so the pub categories do not hide
                url = wait.until(EC.presence_of_element_located((By.LINK_TEXT, next_class_name))).get_attribute('href')
                driver = utils.open_link_in_new_tab(driver, url)
                tab = False
                continue

            wait.until(EC.presence_of_element_located((By.LINK_TEXT, next_class_name))).click()

        else:
            try:
                driver = utils.close_link_tab(driver)
            except InvalidSessionIdException:
                pass
            finally:
                return driver
        i += 1
    progress.close()
