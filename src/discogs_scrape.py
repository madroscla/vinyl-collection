"""Retrieves additional info from Discogs entry via webscraping that's unavailable via API."""

import re 
from time import process_time

from parsel import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_prices(url):
    """Retrieves lowest, median, and highest sold amounts for a given Discogs entry URL.

       Selenium is used to bypass initial cookie acceptance which covers the page.
    """
    firefox_options = Options()
    firefox_options.add_argument('--headless')
    firefox_options.add_argument("--width=1200")
    firefox_options.add_argument("--height=600")
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', False)
    firefox_options.profile = firefox_profile
    
    driver = webdriver.Firefox(options=firefox_options)
    driver.get(url)
    accept_cookies_button = WebDriverWait(driver, 45).until(
        EC.element_to_be_clickable((By.XPATH, '//button[text()="Accept All Cookies"]'))
    )
    driver.execute_script("arguments[0].click();", accept_cookies_button)
    
    selector = Selector(text=driver.page_source)
    price_labels = ['low', 'median', 'high']
    raw_prices = selector.xpath('//section[@id="release-stats"]//span[contains(., "$")]/text()').getall()
    
    if raw_prices == []:
        prices = [None, None, None]
    else:
        prices = [float(re.sub(r'\,|\$','', price)) for price in raw_prices]
    
    price_dict = {key: value for key, value in zip(price_labels, prices)}
    driver.quit()
    return price_dict