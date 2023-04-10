import os
from h11 import Data
import pandas as pd
import time
import kiteAccess
import shoonyaAccess
import types
from strategy import runStrategy
import logging


logging.basicConfig(level=logging.CRITICAL)


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    kite = kiteAccess.getKite()
    print(f"{kite = }")

    ret, shoonya = shoonyaAccess.getShoonya()
    
    shoonya.set_session(os.getenv('shoonya_userid'), os.getenv(
        'shoonya_password'), ret['susertoken'])

    print(f"{shoonya = }")
    
    runStrategy(kite, shoonya)
    
    
    inp = input("Enter 'exit' to exit: ")
    while inp != 'exit':
        inp = input("Enter 'exit' to exit: ")
        
main()
