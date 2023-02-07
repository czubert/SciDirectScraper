# Selenium
from selenium import webdriver

# for chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# for EDGE
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# for Firefox
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService

# Chrome
def chrome_options():
    return webdriver.ChromeOptions()


def chrome_init(options):
    return webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))


# EDGE
def edge_options():
    return webdriver.EdgeOptions()


def edge_init(options):
    return webdriver.Edge(options=options, service=EdgeService(EdgeChromiumDriverManager().install()))


def firefox_init():
    return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))


def initialize_driver(window):
    options = chrome_options()
    # options = edge_options()

    # # to supress the error messages/logs
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', True)
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')

    driver = chrome_init(options)
    # driver = edge_init(options)
    # driver = firefox_init()

    if window == 'Maximized':
        driver.maximize_window()
    elif window == 'Hidden':
        driver.set_window_position(-2000, 0)

    return driver
