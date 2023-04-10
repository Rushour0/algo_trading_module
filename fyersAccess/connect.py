
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import pyotp

import time
from fyers_api import fyersModel, accessToken
import dotenv
import os

dotenv.load_dotenv()
"""
In order to get started with Fyers API we would like you to do the following things first.
1. Checkout our API docs :   https://myapi.fyers.in/docs/
2. Create an APP using our API dashboard :   https://myapi.fyers.in/dashboard/
Once you have created an APP you can start using the below SDK 
"""

# Generate an authcode and then make a request to generate an accessToken (Login Flow)

redirect_uri = os.getenv('redirect_uri')
client_id = os.getenv('client_id')
secret_key = os.getenv('secret_key')
grant_type = "authorization_code"
response_type = "code" 
state = "sample"


def getFyers():

    # Connect to the sessionModel object here with the required input parameters
    session = accessToken.SessionModel(
        client_id=client_id,
        redirect_uri=redirect_uri,
        response_type=response_type,
        state=state,
        secret_key=secret_key,
        grant_type=grant_type
    )

    # Make  a request to generate_authcode object this will return a login url which you need to open in your browser from where you can get the generated auth_code
    token_url = session.generate_authcode()

    print(token_url)

    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")

    browser = webdriver.Chrome(chrome_options=chrome_options)

    browser.get(token_url)

    time.sleep(2)

    userid_input = browser.find_element(by=By.ID, value='fy_client_id')

    userid_input.send_keys(os.getenv('userid') + Keys.RETURN)

    time.sleep(2)

    totp = pyotp.TOTP(os.getenv('totp_key')).now()

    totp_input = browser.find_element(by=By.ID, value='first')

    totp_input.send_keys(totp + Keys.RETURN)

    time.sleep(2)

    pin_input = browser.find_elements(by=By.ID, value='first')[1]

    pin_input.send_keys(os.getenv('pin') + Keys.RETURN)

    time.sleep(2)

    print(f"{browser.current_url =}")

    params = browser.current_url.split('?')[1].split('&')

    for param in params:
        if param.startswith('auth_code'):
            auth_code = param.split('=')[1]
    print(auth_code)

    session.set_token(auth_code)
    response = session.generate_token()

    try:
        access_token = response["access_token"]
        print("token: ", access_token)
    except Exception as e:
        print(e, response)

    fyers = fyersModel.FyersModel(
        token=access_token, is_async=False, client_id=client_id, log_path=r"%userprofile%/.logs/")

    browser.close()
    return fyers
