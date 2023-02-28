import re
import time

import selenium.webdriver
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.support.wait import WebDriverWait
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


def get_pub_categories(driver, el):
    cat = driver.find_element(By.XPATH, f"(//div[@class='FacetItem'])[{el}]/fieldset/ol")
    # Click 'show more' button if exists
    try:
        cat.find_element(By.TAG_NAME, 'button').click()
        return cat
    except NoSuchElementException as e:
        print(f'No "show more" button found: {e}')
        return cat


def paginate_through_cat(pub_categories, requested_num_of_publ, articles_urls,
                         driver, wait, pagination_sleep):
    # Gets the publications categories
    options = pub_categories.find_elements(By.TAG_NAME, 'li')
    categories = True

    # Paginate through all categories of publications
    for i, option in enumerate(options):
        try:
            # moving screen to the element so driver can click a category
            driver.execute_script("arguments[0].scrollIntoView(true);", option)

            # If the text of 'option' contains 'less' it means that all the categories were already checked
            if 'less' in option.text:
                break

            # Gets number of publication in selected category, might be useful one day...
            num_of_articles_in_cat = int(re.sub('([()])+', '', option.text.split()[-1]).replace(',', ''))

            before_click = driver.current_url
            option.click()  # select box (category)
            time.sleep(0.5)

            # Gets numer of pages for the selected category
            num_of_pages_in_cat = utils.get_num_of_pages(driver)

            # selecting cateegory changes url therefore if there is no change in url program skips and tries next one
            if driver.current_url == before_click:
                continue

            if not utils.does_link_text_exist(driver, tag=constants.NEXT_CLASS_NAME):
                # Parse web for urls
                articles_urls += [item.get_attribute("href") for item in wait.until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "result-list-title-link")))]
            else:
                pagination_args = [requested_num_of_publ, articles_urls,
                                   driver, wait, pagination_sleep, num_of_pages_in_cat, categories, i + 1,
                                   len(options)]

                driver = paginate(*pagination_args)
            # moving screen so driver can "unclick" a category
            driver.execute_script("arguments[0].scrollIntoView(true);", option)
            # driver.execute_script(f"window.scrollTo(0, -100);")  # todo sprawdzic czy z tym jest lepiej czy nie
            time.sleep(0.4)
            option.click()  # unselect box (category)
            time.sleep(0.4)

        except StaleElementReferenceException:
            utils.close_link_tab(driver)
            return driver

        if requested_num_of_publ != 0 and len(articles_urls) >= requested_num_of_publ:
            return driver

    return driver


def paginate(requested_num_of_publ, articles_urls, driver, wait, pagination_sleep, num_of_pages,
             categories=False, cat_num=None, cat_max_num=None, tab_opened=False):
    next_btn = constants.NEXT_CLASS_NAME

    if requested_num_of_publ == 0:
        n_loops = -1
    else:
        n_loops = num_of_pages

    # Progress bar
    if categories is True:
        progress = tqdm(desc=f'Category {cat_num} of of {cat_max_num}', total=num_of_pages)
    else:
        progress = tqdm(desc=f'Pagination', total=num_of_pages)

    i = 0

    while i < n_loops or n_loops == -1:
        # Update output progressbar
        progress.update(1)

        # Short break so the server do not block script
        time.sleep(pagination_sleep)  # important: lower than 0.8s values result in error
        # Parse the first view of the web for urls, before pagination strats
        articles_urls += [item.get_attribute("href") for item in wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "result-list-title-link")))]

        # there is fewer publications requested than 100, so all fit in one page
        if n_loops == 1 or num_of_pages == 1:
            return driver

        # Scrolls to the bottom to avoid 'feedback' pop-up
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.3)
        # Opens new tab. As "next" button available - there is more than 100 pubs for given params. And tab is closed
        if utils.does_link_text_exist(driver, tag=next_btn):
            if categories is False:
                wait.until(EC.presence_of_element_located((By.LINK_TEXT, next_btn))).click()
            if not tab_opened and categories is True:
                # Opening 'next button' in new tab instead of clicking it, so the pub categories do not hide
                url = wait.until(EC.presence_of_element_located((By.LINK_TEXT, next_btn))).get_attribute('href')
                time.sleep(0.2)
                driver = utils.open_link_in_new_tab(driver, url)
                time.sleep(0.3)
                tab_opened = True
                i += 1
                continue
            if tab_opened and categories is True:
                wait.until(EC.presence_of_element_located((By.LINK_TEXT, next_btn))).click()

        else:
            utils.close_link_tab(driver)
            return driver

        i += 1

    progress.close()
