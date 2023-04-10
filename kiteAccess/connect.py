
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from kiteconnect import KiteConnect
import time
import pyotp
import dotenv
import os

dotenv.load_dotenv()

api_key = os.getenv('api_key')
secret_key = os.getenv('secret_key')
user_id = os.getenv('user_id')
password = os.getenv('password')
totp_key = os.getenv('totp_key')


def getKite():
    kite = KiteConnect(api_key=api_key)

    login_url = "https://kite.trade/connect/login?api_key=" + api_key

    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-crash-reporter")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-in-process-stack-traces")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--output=/dev/null")

    browser = webdriver.Chrome(chrome_options=chrome_options)

    browser.get(login_url)

    sess_id = browser.current_url.split('=')[-1]
    time.sleep(1)

    user_id_input = browser.find_element(by=By.ID, value='userid')
    password_input = browser.find_element(by=By.ID, value='password')

    user_id_input.send_keys(user_id)
    password_input.send_keys(password + Keys.RETURN)

    time.sleep(2)

    totp_input = browser.find_elements(By.TAG_NAME, value='input')[0]

    totp_url = browser.current_url

    totp = pyotp.TOTP(totp_key)
    current_totp = totp.now()

    totp_input.send_keys(current_totp + Keys.RETURN)

    while browser.current_url == totp_url:
        time.sleep(1)
    # print(f"{browser.current_url =}")

    params = browser.current_url.split('?')[1].split('&')

    for param in params:
        if param.startswith('request_token'):
            request_token = param.split('=')[1]

    browser.close()

    data = kite.generate_session(request_token, api_secret=secret_key)

    kite.set_access_token(data["access_token"])

    return kite


if __name__ == "__main__":
    totp = pyotp.TOTP(totp_key)
    current_totp = totp.now()
    print(current_totp)
