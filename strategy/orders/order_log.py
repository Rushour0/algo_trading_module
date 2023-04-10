import os
from kiteconnect import KiteConnect
from ..utils.formatters import colorstr
from allTypes import strategy as strategyTypes
from datetime import datetime
from shoonyaAccess.api_helper import Order, ShoonyaApi
from allTypes import shoonya as shoonyaTypes
from .proxy_trader import ProxyTrader


class OrderLog:
    log_file_name = f"logs/log {datetime.now().strftime('%d-%m-%Y %H.%M.%S')}.csv"
    is_paper_trade = True
    shoonya = None
    kite = None

    def __init__(
        self,
        kite_symbol: str,
        id: int,
        order: Order,
        time: datetime,
        is_stop_loss: bool = False,
    ):
        self.order_id = id
        self.buy_or_sell = order.buy_or_sell
        self.order_type = order.price_type
        self.symbol = order.tradingsymbol
        self.kite_symbol = kite_symbol
        self.quantity = order.quantity
        self.price = round(order.price, 2)
        self.time = time
        self.exchange_symbol = order.exchange
        self.order_re_entry_count = 0
        self.status = strategyTypes.OrderStatus.ENTERED
        self.is_stop_loss = is_stop_loss
        self.linked_order_id = None
        self.log_order()

    @staticmethod
    def set_shoonya_api(shoonya: ShoonyaApi):
        OrderLog.shoonya = shoonya

    @staticmethod
    def set_kite_api(kite: KiteConnect):
        OrderLog.kite = kite

    @staticmethod
    def change_paper_trade(is_paper_trade: bool):
        OrderLog.is_paper_trade = is_paper_trade

    @staticmethod
    def set_proxy_trader(proxy_trader: ProxyTrader):
        OrderLog.proxy_trader = proxy_trader

    def show_order(self):
        print(self)

    def modify_order(self, price):
        if OrderLog.is_paper_trade:
            return_value = OrderLog.proxy_trader.modify_order(
                self.order_id, price)
        else:
            return_value = self.shoonya.modify_order(self.order_id, price)

        if return_value != None:
            self.price = price
            self.time = datetime.now()
            self.log_order()
            return True
        return False

    def cancel_order(self):
        if OrderLog.is_paper_trade:
            OrderLog.proxy_trader.cancel_order(self.order_id)
        else:
            OrderLog.shoonya.cancel_order(self.order_id)

        self.status = strategyTypes.OrderStatus.CANCELLED
        self.time = datetime.now()
        self.log_order()

    def check_profit_loss(self):
        # TODO: Check profit using kite api
        ltp = self.kite.ltp([self.kite_symbol])[self.kite_symbol]['last_price']
        ltp = float(ltp)
        profit_loss = self.price - ltp
        # if profit_loss > 0:
        #     print(colorstr("bright_green", "bold", f"Profit of {profit_loss} on {self.symbol} order id {self.order_id}"))
        # elif profit_loss < 0:
        #     print(colorstr("bright_red", "bold", f"Loss of {profit_loss} on {self.symbol} order id {self.order_id}"))
        return profit_loss

    def __str__(self):
        return colorstr(f"bright_{'green' if self.buy_or_sell == shoonyaTypes.TransactionType.BUY else 'red'}", "bold", f"{self.order_id}\t{'BUY' if self.buy_or_sell == shoonyaTypes.TransactionType.BUY else 'SELL'}\t\t{self.exchange_symbol}\t\t{self.order_type}\t\t{self.symbol}\t{self.quantity}\t\t{self.price}\t{self.status}\t\t{self.time}")

    def csv(self):
        return f"{self.order_id},{self.buy_or_sell},{self.order_type},{self.symbol},{self.quantity},{self.price},{self.time},{self.status},{self.is_stop_loss},{self.linked_order_id}"

    def log_order(self):
        try:
            os.mkdir("logs")
        except FileExistsError:
            pass
        finally:
            # print(self.log_file_name, os.listdir("logs"))
            if self.log_file_name.split('/')[1] in os.listdir("logs"):
                # print("Logging order Append Mode")
                with open(self.log_file_name, "a") as file:
                    file.write(self.csv() + "\n")
            else:
                # print("Logging order Write Mode")
                with open(self.log_file_name, "w") as file:
                    file.write(
                        "Order-ID,Buy\\Sell,Order-Type,Symbol,Quantity,Price,Time,Status,Is-Stop-Loss,Linked-Order-ID\n")
                    file.write(self.csv() + "\n")
