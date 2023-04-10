
from allTypes.strategy import ExpiryType, EntryType, StopLossType, StockSymbol, OptionType, ExchangeType
from .date_kit import next_expiry_date_kite



def nearest_strike_price(
    stock_symbol: StockSymbol,
    atm: int,
    otm: int = None
) -> int:
    if otm is not None:
        if otm < 0:
            raise Exception("OTM value cannot be negative")
        elif otm > 0:
            if (stock_symbol == StockSymbol.BANKNIFTY or stock_symbol == StockSymbol.FINNIFTY) and otm % 100 != 0:
                raise Exception(
                    f"OTM value must be a multiple of 100 for {stock_symbol}")
            elif stock_symbol == StockSymbol.NIFTY and otm % 50 != 0:
                raise Exception(
                    f"OTM value must be a multiple of 50 for {stock_symbol}")

        if stock_symbol == StockSymbol.BANKNIFTY or stock_symbol == StockSymbol.FINNIFTY:
            return (round(atm / 100) * 100 + otm, round(atm / 100) * 100 - otm)
        elif stock_symbol == StockSymbol.NIFTY:
            return (round(atm / 50) * 50 + otm, round(atm / 50) * 50 - otm)

    else:
        if stock_symbol == StockSymbol.BANKNIFTY or stock_symbol == StockSymbol.FINNIFTY:
            return round(atm / 100) * 100
        elif stock_symbol == StockSymbol.NIFTY:
            return round(atm / 50) * 50


def nearest_premium_price(
    get_ltp: callable,
    stock_symbol: StockSymbol,
    expiry_type: ExpiryType,
    strike_price: int,
    user_value: int,
) -> int:

    strike_list = []

    atm_ce = get_ltp(
        exchange=ExchangeType.NFO,
        symbol=stock_symbol,
        option_type=OptionType.CALL,
        strike_price=strike_price,
        expiry_date=next_expiry_date_kite(expiry_type)
    )
    
    atm_pe = get_ltp(
        exchange=ExchangeType.NFO,
        symbol=stock_symbol,
        option_type=OptionType.PUT,
        strike_price=strike_price,
        expiry_date=next_expiry_date_kite(expiry_type)
    )

    for i in range(-8, 8):
        strike = (atm_ce // 100 + i) * 100
        strike_list.append(strike)
        print(*strike_list)
        for strike in strike_list:
            diff = abs(ltp - strike)
            if (diff < prev_diff):
                closest_strike = strike
                prev_diff = diff
    return closest_strike
