import streamlit as st

# Selenium
import selenium
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

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


@st.experimental_singleton
def chrome_init(options):
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)


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
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')
    driver = chrome_init(options)
    # driver = edge_init(options)
    # driver = firefox_init()

    if window == 'Maximized':
        driver.maximize_window()
    elif window == 'Hidden':
        driver.set_window_position(-2000, 0)

    return driver
