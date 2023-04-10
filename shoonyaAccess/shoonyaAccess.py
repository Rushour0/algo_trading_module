import os
import logging
import pyotp
from .api_helper import ShoonyaApi
from dotenv import load_dotenv

# logging.basicConfig(level=logging.DEBUG)

load_dotenv()

userid = os.getenv('shoonya_userid')
password = os.getenv('shoonya_password')
vendor_code = os.getenv('shoonya_vendor_code')
api_secret = os.getenv('shoonya_api_secret')
imei = os.getenv('shoonya_imei')
totp_key = os.getenv('shoonya_totp_key')


def getShoonya():
    # credentials
    api = ShoonyaApi()

    # Find TOTP
    totp = pyotp.TOTP(totp_key)
    totp = totp.now()

    # make the api call
    ret = api.login(userid=userid,
                    password=password,
                    twoFA=totp,
                    vendor_code=vendor_code,
                    api_secret=api_secret,
                    imei=imei)

    # api.set_session(userid, password, ret['susertoken'])

    return ret, api


if __name__ == "__main__":
    # enable dbug to see request and responses
    logging.basicConfig(level=logging.DEBUG)

    # getShoonya()
    totp = pyotp.TOTP(totp_key)
    totp = totp.now()
    print(f"{totp = }")
