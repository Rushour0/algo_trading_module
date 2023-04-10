import os
import subprocess
import sys
import time
from kiteconnect import KiteConnect
from shoonyaAccess.api_helper import ShoonyaApi, Order
from datetime import datetime
from allTypes import strategy as strategyTypes
from allTypes import shoonya as shoonyaTypes
from .orders.order_log import OrderLog
from .utils.formatters import colorstr, stock_name_kite_nfo, stock_name_kite_nse, stock_name_nfo_shoonya
from .utils.date_kit import next_expiry_date_kite, next_expiry_date_shoonya
from .utils.support_functions import nearest_strike_price, nearest_premium_price
from .orders.order_manager import OrderManager, ProfitLoss
from .shoonya import place_order


class Strategy:
    def __init__(
        self,
        kite: KiteConnect,
        shoonya: ShoonyaApi,
        strategy_name: str,
        strategy_id: int,
        trailing_stop_loss_type: strategyTypes.TrailingStopLossType,
        trailing_stop_loss_value: float,
        trailing_stop_loss_increment: float,
        target_type: strategyTypes.TargetType,
        target_value: float,
        entry_type: strategyTypes.EntryType,
        entry_time: datetime,
        exit_time: datetime,
        expiry_type: strategyTypes.ExpiryType,
        no_of_lots: int,
        re_entry_after_stop_loss: int,
        re_entry_after_target: int,
        stock_symbol: strategyTypes.StockSymbol,
        stop_loss_type: strategyTypes.StopLossType,
        stop_loss_value: float,
        entry_price: float = None,
        is_paper_trade: bool = True,
        otm_value: int = 0,
    ):
        print("Strategy init")
        Strategy.kite = kite
        Strategy.shoonya = shoonya
        self.trailing_stop_loss_type = trailing_stop_loss_type
        self.trailing_stop_loss_value = trailing_stop_loss_value
        self.trailing_stop_loss_original = trailing_stop_loss_value
        self.trailing_stop_loss_increment = trailing_stop_loss_increment
        self.target_type = target_type
        self.target_value = target_value
        self.strategy_name = strategy_name
        self.strategy_id = strategy_id
        self.stock_symbol = stock_symbol
        self.stop_loss_type = stop_loss_type
        self.stop_loss_value = stop_loss_value
        self.entry_type = entry_type
        self.re_entry_after_stop_loss = re_entry_after_stop_loss
        self.re_entry_after_target = re_entry_after_target
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.expiry_type = expiry_type
        self.no_of_lots = no_of_lots
        self.lot_size = 25
        self.order_manager = OrderManager(self.strategy_id, True)
        self.is_paper_trade = is_paper_trade
        self.number_of_exits_with_target = 0
        self.number_of_exits_with_stop_loss = 0
        self.otm_value = otm_value
        self.entry_price = entry_price

    def run(self):
        OrderManager.set_shoonya_api(shoonya=self.shoonya)
        OrderManager.set_kite_api(kite=self.kite)
        OrderManager.change_paper_trade(self.is_paper_trade)

        self.entry_criteria()

        while True:

            time.sleep(2.5)
            os.system('cls' if os.name == 'nt' else 'clear')
            self.trailing_stop_loss()
            self.profit_target_hit()
            self.order_manager.show_orders()
            self.exit_criteria()

    def exit_criteria(self, otm_value=0):
        # Check if the strategy has expired
        if datetime.now() > self.exit_time:
            self.force_exit()
            exit(0)
        # Check if the strategy has reached the target
        else:
            self.order_manager.get_all_orders()

    def force_exit(self):
        # close all positions
        self.order_manager.store_orders()
        self.order_manager.cancel_all_orders()

    def exit_handler(self, signum, frame):
        print(colorstr("bright_yellow",
              "Do you want to exit the strategy? (y/N) : "), end="")
        if input().lower() == "y":
            print(colorstr("bright_red", "Exiting the strategy"))
            self.force_exit()
            exit(0)

    @staticmethod
    def get_ltp(
        exchange: strategyTypes.ExchangeType,
        symbol: strategyTypes.StockSymbol,
        option_type: strategyTypes.OptionType = None,
        strike_price: int = None,
        expiry_date: str = None,
    ) -> float:
        try:
            if exchange == strategyTypes.ExchangeType.NSE:
                name = stock_name_kite_nse(symbol)

            elif exchange == strategyTypes.ExchangeType.NFO:
                if option_type is None or strike_price is None or expiry_date is None:
                    raise Exception(
                        "Option type, strike price and expiry date are required for NFO")

                name = stock_name_kite_nfo(
                    symbol,
                    option_type,
                    strike_price,
                    expiry_date
                )
            print(name)
            ltp = Strategy.kite.ltp([name])[name]['last_price']
            print(ltp)
            return float(ltp)

        except Exception as e:
            print(name, "Failed : {} ".format(e))

    def get_positions(self):
        return self.shoonya.get_positions()

    def load_strategy(self):
        pass

    # Will be deprecated later on
    def strategy_execute(self):
        # Days to run the strategy
        pass

    def entry_criteria(self,  user_value=0):

        if self.entry_time > datetime.now():
            while self.entry_time > datetime.now():
                time.sleep(5)
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"Entry Time is {self.entry_time.strftime('%H:%M:%S')}")

        if self.number_of_exits_with_stop_loss == 0 and self.number_of_exits_with_target == 0:
            pass
        elif self.number_of_exits_with_stop_loss < self.re_entry_after_stop_loss:
            self.number_of_exits_with_stop_loss += 1
            self.re_entry_after_stop_loss -= 1
        elif self.number_of_exits_with_target == self.re_entry_after_target:
            self.number_of_exits_with_target += 1
            self.re_entry_after_target -= 1

        atm = self.get_ltp(strategyTypes.ExchangeType.NSE, self.stock_symbol)
        print("ATM :", atm)

        strike_prices = {}
        if self.entry_type == strategyTypes.EntryType.ATM:

            strike_price = nearest_strike_price(
                stock_symbol=self.stock_symbol,
                atm=atm,
            )

            print("Strike Price :", strike_price)

            strike_prices[strategyTypes.OptionType.CALL] = strike_price
            strike_prices[strategyTypes.OptionType.PUT] = strike_price

            expiry_date = next_expiry_date_kite(self.expiry_type)

            atm_ce = self.get_ltp(
                exchange=strategyTypes.ExchangeType.NFO,
                symbol=self.stock_symbol,
                option_type=strategyTypes.OptionType.CALL,
                strike_price=strike_price,
                expiry_date=expiry_date
            )

            atm_pe = self.get_ltp(
                exchange=strategyTypes.ExchangeType.NFO,
                symbol=self.stock_symbol,
                option_type=strategyTypes.OptionType.PUT,
                strike_price=strike_price,
                expiry_date=expiry_date
            )

            print("ATM CE :", atm_ce)
            print("ATM PE :", atm_pe)

        # Sell CE & PE at ATM ( Rounded to nearest 100 ) ± OTM Value ( + for call, - for put )

        elif self.entry_type == strategyTypes.EntryType.OTM:
            if self.otm_value == 0:
                print(colorstr("red", "No OTM Value provided"))
                exit(0)

            strike_price_ce, strike_price_pe = nearest_strike_price(
                stock_symbol=self.stock_symbol,
                atm=atm,
                otm=self.otm_value
            )

            print("Strike Price CE :", strike_price_ce)
            print("Strike Price PE :", strike_price_pe)

            strike_prices[strategyTypes.OptionType.CALL] = strike_price_ce
            strike_prices[strategyTypes.OptionType.PUT] = strike_price_pe

            atm_ce = self.get_ltp(
                exchange=strategyTypes.ExchangeType.NFO,
                symbol=self.stock_symbol,
                option_type=strategyTypes.OptionType.CALL,
                strike_price=strike_price_ce,
                expiry_date=next_expiry_date_kite(self.expiry_type)
            )

            atm_pe = self.get_ltp(
                exchange=strategyTypes.ExchangeType.NFO,
                symbol=self.stock_symbol,
                option_type=strategyTypes.OptionType.PUT,
                strike_price=strike_price_pe,
                expiry_date=next_expiry_date_kite(self.expiry_type)
            )

            print("OTM CE :", atm_ce)
            print("OTM PE :", atm_pe)

        elif self.entry_type == strategyTypes.EntryType.USER_DEFINED:
            # TODO: Add user specified strike price entry

            nearest_premium_price(
                self.stock_symbol,
                self.expiry_type,
                self.entry_price
            )

            print("Strike Price :", strike_price)

            atm_ce = self.get_ltp(
                exchange=strategyTypes.ExchangeType.NFO,
                symbol=self.stock_symbol,
                option_type=strategyTypes.OptionType.CALL,
                strike_price=strike_price,
                expiry_date=next_expiry_date_kite(self.expiry_type)
            )

            atm_pe = self.get_ltp(
                exchange=strategyTypes.ExchangeType.NFO,
                symbol=self.stock_symbol,
                option_type=strategyTypes.OptionType.PUT,
                strike_price=strike_price,
                expiry_date=next_expiry_date_kite(self.expiry_type)
            )

            print("ATM CE :", atm_ce)
            print("ATM PE :", atm_pe)

        # Kite Expiry Dates
        kite_expiry_dates = {
            strategyTypes.OptionType.PUT: stock_name_kite_nfo(
                symbol=self.stock_symbol,
                option_type=strategyTypes.OptionType.PUT,
                strike_price=strike_prices[strategyTypes.OptionType.PUT],
                expiry_date=next_expiry_date_kite(self.expiry_type)
            ),
            strategyTypes.OptionType.CALL: stock_name_kite_nfo(
                symbol=self.stock_symbol,
                option_type=strategyTypes.OptionType.CALL,
                strike_price=strike_prices[strategyTypes.OptionType.CALL],
                expiry_date=next_expiry_date_kite(self.expiry_type)
            )
        }
        
        # Take Entry
        entry_orders = self.take_entry(
            atm_ce,
            atm_pe,
            strike_prices[strategyTypes.OptionType.CALL],
            strike_prices[strategyTypes.OptionType.PUT],
            kite_expiry_dates
        )
        
        # Set Stop Loss
        stop_loss_orders = self.stop_loss(
            atm_ce,
            atm_pe,
            strike_prices[strategyTypes.OptionType.CALL],
            strike_prices[strategyTypes.OptionType.PUT],
            kite_expiry_dates
        )

        # Link Orders
        for eo, slo in zip(entry_orders, stop_loss_orders):
            self.order_manager.link_orders([eo, slo])

        # Sell CE & PE at Closest Premium ( User specified ) ( 3 types - above premium >=, below premium <=, nearest premium <= or >= )

    def trailing_stop_loss(self):
        # Trailing stop loss ( for individual orders ) with percentage checking, points checking or no trailing stop loss
        list_profit_loss = self.order_manager.individual_profit_loss()
        # TODO: Add trailing stop loss for overall profit loss
        if self.trailing_stop_loss_type == strategyTypes.TrailingStopLossType.NONE:
            return
        
        if self.trailing_stop_loss_type == strategyTypes.TrailingStopLossType.PERCENTAGE:
            for profit_loss in list_profit_loss:
                print(profit_loss.order_id , profit_loss.percentage, self.trailing_stop_loss_value)
                if profit_loss.percentage >= self.trailing_stop_loss_value:
                    order_price = profit_loss.points / profit_loss.percentage * 100
                    self.order_manager.increment_stop_loss(
                        profit_loss.order_id, self.trailing_stop_loss_increment * order_price / 100)
                    self.trailing_stop_loss_value += self.trailing_stop_loss_original

        elif self.trailing_stop_loss_type == strategyTypes.TrailingStopLossType.POINTS:
            for profit_loss in list_profit_loss:
                print(profit_loss.order_id , profit_loss.percentage, self.trailing_stop_loss_value)
                if profit_loss.points >= self.trailing_stop_loss_value:
                    self.order_manager.increment_stop_loss(
                        profit_loss.order_id, self.trailing_stop_loss_increment)
                    self.trailing_stop_loss_value += self.trailing_stop_loss_original
        # Trailing stop loss ( overall - orders' total loss percentage is checked ) with percentage checking, points checking or no trailing stop loss

    def profit_target_hit(self):
        # Profit target ( for individual ) with percentage checking, points checking or no profit target
        if self.check_profit_loss()[self.target_type] >= self.target_value:
            self.order_manager.cancel_all_orders()

    def check_profit_loss(self):
        # Check profits ( for individual ) with percentage checking, points checking or no profit target
        [total_profit_loss,
            percentage_profit_loss] = self.order_manager.cummulative_profit_loss()
        return {strategyTypes.TargetType.POINTS: total_profit_loss, strategyTypes.TargetType.PERCENTAGE: percentage_profit_loss}

    def take_entry(self, atm_ce: float, atm_pe: float, strike_price_ce: int, strike_price_pe: int, kite_expiry_dates: list[str]) -> list[int]:
        order_ids = []
        expiry_date = next_expiry_date_shoonya(self.expiry_type)
        order_ids.append(
            # Add order id to list
            self.order_manager.place_order(
                transaction_type=shoonyaTypes.TransactionType.SELL,
                product_type=shoonyaTypes.ProductType.NRML,
                order_type=shoonyaTypes.OrderType.MARKET,
                option_type=strategyTypes.OptionType.CALL,
                stock_symbol=self.stock_symbol,
                expiry_date=expiry_date,
                strike_price=strike_price_ce,
                quantity=self.no_of_lots * self.lot_size,
                price=atm_ce,
                kite_symbol=kite_expiry_dates[strategyTypes.OptionType.CALL]
            )
        )
        order_ids.append(
            self.order_manager.place_order(
                transaction_type=shoonyaTypes.TransactionType.SELL,
                product_type=shoonyaTypes.ProductType.NRML,
                order_type=shoonyaTypes.OrderType.MARKET,
                option_type=strategyTypes.OptionType.PUT,
                stock_symbol=self.stock_symbol,
                expiry_date=expiry_date,
                quantity=self.no_of_lots * self.lot_size,
                strike_price=strike_price_pe,
                price=atm_pe,
                kite_symbol=kite_expiry_dates[strategyTypes.OptionType.PUT]
            )
        )

        return order_ids

    def stop_loss(self, atm_ce, atm_pe, strike_price_ce, strike_price_pe, kite_expiry_dates) -> list[int]:
        order_ids = []
        expiry_date = next_expiry_date_shoonya(self.expiry_type)
        # Stop loss ( for individual orders ) with percentage checking, points checking or no stop loss

        if self.stop_loss_type == strategyTypes.StopLossType.POINTS:
            atm_ce = atm_ce - self.lot_size
            atm_pe = atm_pe + self.lot_size

        elif self.stop_loss_type == strategyTypes.StopLossType.PERCENTAGE:
            atm_ce = atm_ce * \
                (1 + self.stop_loss_value / 100)
            atm_pe = atm_pe * \
                (1 + self.stop_loss_value / 100)

        order_ids.append(
            self.order_manager.place_order(
                transaction_type=shoonyaTypes.TransactionType.BUY,
                product_type=shoonyaTypes.ProductType.MIS,
                order_type=shoonyaTypes.OrderType.STOP_LOSS_LIMIT,
                option_type=strategyTypes.OptionType.CALL,
                stock_symbol=self.stock_symbol,
                expiry_date=expiry_date,
                strike_price=strike_price_ce,
                quantity=self.no_of_lots * self.lot_size,
                price=atm_ce,
                kite_symbol=kite_expiry_dates[strategyTypes.OptionType.CALL]
            )
        )
        order_ids.append(
            self.order_manager.place_order(
                transaction_type=shoonyaTypes.TransactionType.BUY,
                product_type=shoonyaTypes.ProductType.MIS,
                order_type=shoonyaTypes.OrderType.STOP_LOSS_LIMIT,
                option_type=strategyTypes.OptionType.PUT,
                stock_symbol=self.stock_symbol,
                expiry_date=expiry_date,
                strike_price=strike_price_pe,
                quantity=self.no_of_lots * self.lot_size,
                price=atm_pe,
                kite_symbol=kite_expiry_dates[strategyTypes.OptionType.PUT]
            )
        )
        return order_ids
        # Stop loss ( overall - orders' total loss percentage is checked ) with percentage checking, points checking or no stop loss

        # Stop loss with trailing stop loss

        # Re-entry after hitting stop loss
