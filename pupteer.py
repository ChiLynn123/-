from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
browser = webdriver.Chrome()
browser.maximize_window()  # 最大化窗口
wait = WebDriverWait(browser, 10) # 等待加载10s

def login():
    browser.get('https://www.itjuzi.com/user/login')
    input = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="create_account_email"]')))
    input.send_keys('irw27812@awsoo.com')
    input = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="create_account_password"]')))
    input.send_keys('test2018')
    submit = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="login_btn"]')))
    submit.click() # 点击登录按钮
    get_page_index()

def get_page_index():
    browser.get('http://radar.itjuzi.com/investevent')
    try:
        print(browser.page_source)  # 输出网页源码
    except Exception as e:
        print(str(e))
login()