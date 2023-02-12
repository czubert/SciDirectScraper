import re
import time
from tqdm import tqdm

# Selenium
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidSessionIdException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.by import By

import constants
# Modules
import utils


def number_of_pages_is_limited(driver, num_of_all_papers):
    pub_numbs_per_year = driver.find_elements(By.XPATH, "(//ol[@id='srp-pagination']/li)")[0]
    pages = int(pub_numbs_per_year.text.split()[-1])
    if num_of_all_papers // 100 + 1 != pages:
        return True, pages
    else:
        return False, pages


def get_max_num_of_publications(driver):
    """
    There is a limit of publications to parse per one link = 1000.
    This function returns True if the limit is exceeded, else it returns False
    :param driver: Selenium Webdriver
    :return: list
    """
    # number of publications per year
    # if there are fewer publications than requested,
    pub_numbs_per_year = driver.find_element(By.XPATH, "(//div[@class='FacetItem'][1]/fieldset/ol)")
    max_num_of_papers = 0
    papers = pub_numbs_per_year.text.split()

    for i in range(1, len(papers) + 1, 2):
        try:
            max_num_of_papers += int(re.sub(r'([()])*', '', papers[i]).replace(',', ''))
        except ValueError:
            continue
    return max_num_of_papers


def get_pub_categories(driver):
    cat = driver.find_element(By.XPATH, "(//div[@class='FacetItem'])[3]/fieldset/ol")
    try:
        cat.find_element(By.TAG_NAME, 'button').click()
    except NoSuchElementException as e:
        print(f'No "show more" button found: {e}')

    return cat


def paginate_through_cat(pub_categories, requested_num_of_publ, articles_urls,
                         driver, wait, pagination_sleep):
    # Gets the publications categories
    options = pub_categories.find_elements(By.TAG_NAME, 'li')
    categories = True

    collected_urls = 0

    # Paginate through all categories of publications
    for i, option in enumerate(options):
        num_of_articles_per_cat = int(re.sub('([()])+', '', option.text.split()[-1]).replace(',', ''))
        collected_urls += num_of_articles_per_cat
        num_of_pages_per_cat = num_of_articles_per_cat // 100 + 1

        try:
            option.click()  # select box

            pagination_args = [requested_num_of_publ, articles_urls,
                               driver, wait, pagination_sleep, num_of_pages_per_cat, categories, i+1, len(options)]

            driver = paginate(*pagination_args)

            option.click()  # unselect box

        except StaleElementReferenceException:
            pass

        if collected_urls >= requested_num_of_publ != 0:
            break


def paginate(requested_num_of_publ, articles_urls, driver, wait, pagination_sleep, num_of_pages,
             categories=False, cat_num=None, cat_max_num=None, tab_opened=False):
    next_btn = constants.NEXT_CLASS_NAME

    if requested_num_of_publ == 0:
        n_loops = -1
    else:
        n_loops = num_of_pages

    i = 0
    if categories is True:
        progress = tqdm(desc=f'Pagination {cat_num}/{cat_max_num}', total=num_of_pages)
    else:
        progress = tqdm(desc=f'Pagination', total=num_of_pages)

    while i < n_loops or n_loops == -1:
        # Update output progressbar
        progress.update(1)

        # Short break so the server do not block script
        time.sleep(pagination_sleep)  # important: lower than 0.8s values result in error
        # Parse web for urls
        articles_urls += [item.get_attribute("href") for item in wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "result-list-title-link")))]

        # there is fewer publications requested than 100, so all fit in one page
        # if n_loops == 1:
        #     return driver

        # Scrolls to the bottom to avoid 'feedback' pop-up
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Opens new tab. As "next" button available - there is more than 100 pubs for given params. And tab is closed
        if utils.does_element_exist(driver, tag=next_btn):
            if categories is False:
                wait.until(EC.presence_of_element_located((By.LINK_TEXT, next_btn))).click()
            if not tab_opened and categories is True:
                # Opening 'next button' in new tab instead of clicking it, so the pub categories do not hide
                url = wait.until(EC.presence_of_element_located((By.LINK_TEXT, next_btn))).get_attribute('href')
                driver = utils.open_link_in_new_tab(driver, url)
                tab_opened = True
                continue
            if tab_opened and categories is True:
                wait.until(EC.presence_of_element_located((By.LINK_TEXT, next_btn))).click()

        else:
            return driver

        i += 1

    progress.close()
