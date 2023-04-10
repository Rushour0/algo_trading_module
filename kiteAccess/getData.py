from kiteconnect import KiteConnect

def getHistoricalData(kite : KiteConnect, instrument_token, from_date, to_date, interval):
    return kite.historical_data(
        instrument_token=instrument_token,
        from_date=from_date,
        to_date=to_date,
        interval=interval,
    )