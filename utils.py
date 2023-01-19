from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


def does_element_exist(driver, tag):
    print(f'utils driver {driver}')

    try:
        element_exist = driver.find_element(By.CLASS_NAME, tag).is_displayed()
    except NoSuchElementException:
        element_exist = False
        print("Pagination: all pages parsed")

    return element_exist
