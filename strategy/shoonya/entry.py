
from shoonyaAccess.api_helper import ShoonyaApi, Order
from allTypes import strategy as strategyTypes
from pprint import pprint
from allTypes import shoonya as shoonyaTypes

from ..orders.order_manager import OrderManager
from ..orders.order_log import OrderLog
from ..utils.formatters import stock_name_nfo_shoonya, stock_name_kite_nfo
from ..utils.date_kit import next_expiry_date_shoonya, shoonya_to_kite_expiry


def place_order(
    shoonya: ShoonyaApi,
    order_manager: OrderManager,
    transaction_type: shoonyaTypes.TransactionType,
    product_type: shoonyaTypes.ProductType,
    order_type: shoonyaTypes.OrderType,
    option_type: strategyTypes.OptionType,
    stock_symbol: str,
    expiry_date: str,
    strike_price: int,
    quantity: int,
    price: float,
    exchange_type: shoonyaTypes.ExchangeType = shoonyaTypes.ExchangeType.NFO

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

    order_dict = shoonya.place_order(order)

    order_log = OrderLog(
        kite_symbol=stock_name_kite_nfo(
            symbol=stock_symbol,
            strike_price=strike_price,
            option_type=option_type,
            expiry_date=shoonya_to_kite_expiry(expiry_date)
        ),
        id=order_dict['norenordno'],
        order=order,
        time=order_dict['request_time'],
        is_stop_loss=(order_type == shoonyaTypes.OrderType.LIMIT)
    )

    order_manager.add_order(order_log)

    return order_log.order_id
