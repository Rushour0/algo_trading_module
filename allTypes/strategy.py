class StopLossType:
    POINTS = 'POINTS'
    PERCENTAGE = 'PERCENTAGE'
    NONE = 'NONE'

class ExpiryType:
    WEEKLY = 'WEEKLY'
    MONTHLY = 'MONTHLY'
    
class EntryType:
    ATM = 'ATM'
    OTM = 'OTM'
    USER_DEFINED = 'USER_DEFINED'
    
class OrderStatus:
    ENTERED = "ENTERED"
    EXITED = "EXITED"
    RE_ENTRY = "RE_ENTRY"
    CANCELLED = "CANCELLED"

class TargetType:
    POINTS = "POINTS"
    PERCENTAGE = "PERCENTAGE"

class TrailingStopLossType:
    POINTS = "POINTS"
    PERCENTAGE = "PERCENTAGE"
    NONE = "NONE"

class OptionType:
    CALL = "CE"
    PUT = "PE"


class ExchangeType:
    NSE = "NSE"
    NFO = "NFO"


class StockSymbol:
    BANKNIFTY = "BANKNIFTY"
    NIFTY = "NIFTY"
    FINNIFTY = "FINNIFTY"
    CRUDEOIL = "CRUDEOIL"

    @staticmethod
    def get_list():
        return [attr for attr in dir(StockSymbol)
                if not callable(getattr(StockSymbol, attr)) and not attr.startswith("__")]


class NFOStockSymbol(StockSymbol):
    BANKNIFTY = "BANKNIFTY"
    NIFTY = "NIFTY"
    FINNIFTY = "FINNIFTY"

    @staticmethod
    def get_list():
        return [attr for attr in dir(NFOStockSymbol)
                if not callable(getattr(NFOStockSymbol, attr)) and not attr.startswith("__")]


class NSEStockSymbol(StockSymbol):
    BANKNIFTY = "NIFTY BANK"
    NIFTY = "NIFTY"
    FINNIFTY = "FINNIFTY"
    CRUDEOIL = "CRUDEOIL"
    
    @staticmethod
    def get_list():
        return [attr for attr in dir(NSEStockSymbol)
                if not callable(getattr(NSEStockSymbol, attr)) and not attr.startswith("__")]


class KiteStock:
    NSENIFTY = f"{ExchangeType.NSE}:{NFOStockSymbol.NIFTY}"
    NSEBANKNIFTY = f"{ExchangeType.NSE}:{NFOStockSymbol.BANKNIFTY}"
    NSEFINNIFTY = f"{ExchangeType.NSE}:{NFOStockSymbol.FINNIFTY}"

    NFOBANKNIFTY = f"{ExchangeType.NFO}:{NFOStockSymbol.BANKNIFTY}"
    NFONIFTY = f"{ExchangeType.NFO}:{NFOStockSymbol.NIFTY}"
    NFOFINNIFTY = f"{ExchangeType.NFO}:{NFOStockSymbol.FINNIFTY}"


if __name__ == "__main__":
    NFOStockSymbol.get_list(NFOStockSymbol)
