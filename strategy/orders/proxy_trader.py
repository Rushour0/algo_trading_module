from datetime import datetime
import random
from shoonyaAccess.api_helper import Order
import threading


class ProxyTrader:

    __singleton_lock = threading.Lock()
    __singleton_instance = None

    # define the classmethod
    @classmethod
    def instance(cls):

        # check for the singleton instance
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()

        # return the singleton instance
        return cls.__singleton_instance

    def __init__(self):
        self.orders = {}  # type: dict[int, OrderLog]
        self.logs = []  # type: list[OrderLog]
        self.portfolio = {}  # type: dict[str, int]

    def place_order(self, order: Order):
        order_dict = {
            'norenordno': random.randint(1000000000, 9999999999),
            'request_time': datetime.now(),
        }
        return order_dict

    def modify_order(self, order_id, price):
        return_value = {
            'norenordno': order_id,
            'price': price,
            'request_time': datetime.now()
        }
        return return_value

    def cancel_order(self, order_id):
        return_value = {
            'norenordno': order_id,
            'status': 'CANCELLED',
            'request_time': datetime.now()
        }
        return return_value

    def get_order(self):
        pass

    def get_orders(self):
        pass
