from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


def does_element_exist(driver, tag):
    try:
        # element_exist = wait.until(EC.visibility_of_element_located((selector, tag)))
        element_exist = driver.find_element(By.CLASS_NAME, tag).is_displayed()
        print(element_exist)
    except NoSuchElementException as e:
        element_exist = False
        print("Element doesn't exists", e)
    return element_exist
