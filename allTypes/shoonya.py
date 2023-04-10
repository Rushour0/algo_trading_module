class TransactionType:
    BUY = "B"
    SELL = "S"


class ProductType:
    CNC = "C"
    NRML = "M"
    MIS = "I"
    BRACKET = "B"
    COVER = "H"


class ExchangeType:
    NSE = "NSE"
    NFO = "NFO"
    MCX = "MCX"


class OrderType:
    LIMIT = "LMT"
    MARKET = "MKT"
    STOP_LOSS_LIMIT = "SL-LMT"
    STOP_LOSS_MARKET = "SL-MKT"


class RetentionType:
    DAY = "DAY"
    EOS = "EOS"
    IOC = "IOC"
