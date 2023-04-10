import signal
import os
from kiteconnect import KiteConnect
from strategy.strategy import Strategy
from shoonyaAccess.api_helper import ShoonyaApi
from strategy.utils.date_kit import next_expiry_date_kite
from allTypes.strategy import OptionType, ExchangeType, StockSymbol
from strategy.utils.formatters import stock_name_kite_nfo
from allTypes import strategy as strategyTypes
from datetime import datetime


def runStrategy(kite: KiteConnect, shoonya: ShoonyaApi) -> None:
    os.system("git pull")
    print("Running strategy")

    if (datetime.today().weekday() in [5, 6]):
        print("Today is a weekend")
        # return    
    strategy = Strategy(
        kite=kite,
        shoonya=shoonya,
        strategy_name="Test",
        strategy_id=1,
        # PERCENTAGE, POINTS
        trailing_stop_loss_type=strategyTypes.TrailingStopLossType.PERCENTAGE,
        trailing_stop_loss_value=-10,
        trailing_stop_loss_increment=20,
        target_type=strategyTypes.TargetType.POINTS,  # PERCENTAGE, POINTS
        target_value=200,
        entry_type=strategyTypes.EntryType.OTM,  # OTM, ATM
        entry_time=datetime.today().replace(hour=10, minute=25, second=25, microsecond=0),
        exit_time=datetime.today().replace(hour=10, minute=26, second=25, microsecond=0),
        expiry_type=strategyTypes.ExpiryType.WEEKLY,
        no_of_lots=2,
        otm_value=100,
        re_entry_after_stop_loss=3,
        re_entry_after_target=0,
        stock_symbol=strategyTypes.StockSymbol.BANKNIFTY,  # BANKNIFTY, NIFTY,FINNIFTY
        stop_loss_type=strategyTypes.StopLossType.PERCENTAGE,  # PERCENTAGE, POINTS, NONE
        stop_loss_value=15,
        is_paper_trade=True
    )

    signal.signal(signal.SIGINT, strategy.exit_handler)

    strategy.run()
