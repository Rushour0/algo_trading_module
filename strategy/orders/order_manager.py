from datetime import datetime
import sys
from kiteconnect import KiteConnect
from shoonyaAccess.api_helper import ShoonyaApi

from .order_log import OrderLog
from .proxy_trader import ProxyTrader
from ..utils.formatters import stock_name_nfo_shoonya, stock_name_kite_nfo, colorstr
from ..utils.date_kit import next_expiry_date_shoonya, shoonya_to_kite_expiry

from allTypes import strategy as strategyTypes, shoonya as shoonyaTypes
from shoonyaAccess.api_helper import Order


class ProfitLoss:
    def __init__(self, order_id: int, points: float, percentage: float):
        self.order_id = order_id
        self.points = points
        self.percentage = percentage


class OrderManager:
    orders = {}  # type: dict[int, OrderLog]
    history = {}  # type: dict[int, OrderLog]

    def __init__(self, strategy_id: int, is_paper_trade: bool = True):
        self.strategy_id = strategy_id
        OrderManager.is_paper_trade = is_paper_trade
        OrderManager.proxy_trader = ProxyTrader()
        OrderLog.set_proxy_trader(OrderManager.proxy_trader)
        OrderLog.change_paper_trade(is_paper_trade)

    @staticmethod
    def set_shoonya_api(shoonya: ShoonyaApi):
        OrderManager.shoonya = shoonya
        OrderLog.set_shoonya_api(shoonya)

    @staticmethod
    def set_kite_api(kite: KiteConnect):
        OrderManager.kite = kite
        OrderLog.set_kite_api(kite)

    @staticmethod
    def change_paper_trade(is_paper_trade: bool):
        OrderManager.is_paper_trade = is_paper_trade
        OrderLog.change_paper_trade(is_paper_trade)

    def place_order(
        self,
        transaction_type: shoonyaTypes.TransactionType,
        product_type: shoonyaTypes.ProductType,
        order_type: shoonyaTypes.OrderType,
        option_type: strategyTypes.OptionType,
        stock_symbol: str,
        expiry_date: str,
        strike_price: int,
        quantity: int,
        price: float,
        kite_symbol:str,
    ):

        order = Order(
            buy_or_sell=transaction_type,
            product_type=product_type,
            tradingsymbol=stock_name_nfo_shoonya(
                symbol=stock_symbol,
                strike_price=strike_price,
                option_type=option_type,
                expiry_date=expiry_date
            ),
            price_type=order_type,
            quantity=quantity,
            price=price,
            trigger_price=price,
            discloseqty=quantity,
            retention=shoonyaTypes.RetentionType.DAY
        )

        if OrderManager.is_paper_trade:
            print(colorstr("bright_yellow", "bold", "Paper trade mode"))
            order_dict = self.proxy_trader.place_order(order)
        else:
            order_dict = self.shoonya.place_order(order)

        order_log = OrderLog(
            kite_symbol=kite_symbol,
            id=order_dict['norenordno'],
            order=order,
            time=order_dict['request_time'],
            is_stop_loss=(order_type != shoonyaTypes.OrderType.MARKET)
        )

        self.add_order(order_log)

        return order_log.order_id

    def add_order(self, order_log: OrderLog):
        if order_log.order_id in self.orders:
            print(colorstr("bright_red", "bold", "Order already exists"))
        else:
            self.orders[order_log.order_id] = order_log
            print(colorstr("bright_green", "bold", "Order added"))

    def get_all_orders(self):
        if len(self.orders) > 0:
            return self.orders
        return colorstr("bright_red", "bold", "No orders found")

    def get_order(self, order_id: int):
        if order_id in self.orders:
            print(colorstr("bright_green", "bold", "Order found"))
            return self.orders[order_id]
        return False

    def show_orders(self):

        sys.stdout.write(f"Strategy ID: {self.strategy_id}")
        sys.stdout.write("\n")
        sys.stdout.write(colorstr("bright_white", "bold",
                                  f"Order-ID\tBuy\\Sell\tExchange-Symbol\tOrder-Type\tSymbol\t\t\tQuantity\tPrice\tStatus\t\tTime"))
        sys.stdout.write("\n")
        for order in self.orders.values():
            sys.stdout.write(order.__str__())
            sys.stdout.write("\n")
        print(colorstr("bright_blue", "bold","Total profit/loss :"), self.cummulative_profit_loss()[0])

    def add_to_history(self, order_log: OrderLog):
        del self.orders[order_log.order_id]  # remove from orders
        self.history[order_log.order_id] = order_log  # add to history
        print(colorstr("bright_green", "bold", "Order moved to history"))

    def link_orders(self, order_ids: tuple[int]):
        if len(order_ids) == 2:
            self.orders[order_ids[0]].linked_order_id = order_ids[1]
            self.orders[order_ids[1]].linked_order_id = order_ids[0]
            print(colorstr("bright_green", "bold", "Orders linked successfully"))
        else:
            print(colorstr("bright_red", "bold",
                  "Invalid number of orders to link - 2 expected"))

    def individual_profit_loss(self) -> list[ProfitLoss]:
        profit_loss = []
        for order in self.orders.values():
            if not order.is_stop_loss:
                order_profit_loss = order.check_profit_loss()
                profit_loss.append(
                    ProfitLoss(
                        order_id=order.order_id,
                        points=order_profit_loss,
                        percentage=(order_profit_loss / order.price) * 100
                    )
                )
        return profit_loss

    def cummulative_profit_loss(self) -> float:
        total_profit_loss = 0
        total_initial_price = 0
        for order in self.orders.values():
            if not order.is_stop_loss:
                total_initial_price += order.price
                total_profit_loss += order.check_profit_loss()
        percentage_profit_loss = (total_profit_loss / total_initial_price) * 100
        return [total_profit_loss, percentage_profit_loss]

    def cancel_order(self, order_id: int):
        if order_id in self.orders:
            self.orders[order_id].cancel_order()
            print(colorstr("bright_green", "bold", "Order cancelled successfully"))
            self.add_to_history(self.orders[order_id])
        else:
            print(colorstr("bright_red", "bold", "Order not found"))

    def increment_stop_loss(self, order_id: int, increment: float):
        # TODO: Implement this

        profit_increased_order = self.get_order(order_id)

        linked_order = self.get_order(profit_increased_order.linked_order_id)

        return_value = linked_order.modify_order(
            linked_order.price - increment)

        if return_value:
            linked_order.price -= increment
            return True
        return False

    def cancel_all_orders(self):
        for order in self.orders.values():
            order.cancel_order()
        print(colorstr("bright_green", "bold", "All orders cancelled successfully"))

    def store_orders(self):
        with open("orders.csv", "w") as file:
            file.write(
                "Order-ID,Buy\\Sell,Order-Type,Symbol,Quantity,Price,Time,Status,Is-Stop-Loss,Linked-Order-ID\n")
            for order_log in self.orders.values():
                file.write(order_log.csv() + "\n")

    