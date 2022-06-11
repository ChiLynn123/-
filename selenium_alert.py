import time
import logging
from copy import deepcopy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException

logging.basicConfig(level=logging.DEBUG)
def crawl(url, page_load_strategy):
    _start_time = time.time()
    options = Options()
    desired_capabilities = deepcopy(DesiredCapabilities.CHROME)  
    desired_capabilities["pageLoadStrategy"] = page_load_strategy
    driver = webdriver.Chrome(options=options, desired_capabilities=desired_capabilities)
    url = 'http://{}'.format(url) if not url.startswith('http') else url
    driver.get(url)
    page_source = driver.page_source
    try:
        page_source = driver.page_source
    except UnexpectedAlertPresentException as e:
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.dismiss()
        except TimeoutException:
            print("deal alert")
            page_source = driver.page_source
    print('Elasped time {:0.2f}'.format(time.time()-_start_time))
    return page_source
