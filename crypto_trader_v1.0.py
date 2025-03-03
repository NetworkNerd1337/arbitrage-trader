# Author: Ryan Huff (ryanthomashuff.com)
# Date: March 02, 2025
# Use at your own risk - NO GUARANTEES
# Using this script implies consent that you accept the inherent risks of automating trading in your exchange accounts

#!/usr/bin/env python3

import time
import daemon
import lockfile
import signal
import logging
import sys
import os
from enum import Enum
from abc import ABC, abstractmethod
import ccxt  # Crypto exchange library
import yfinance as yf  # Yahoo Finance API
import schedule

class ExchangeType(Enum):
    COINBASE = "coinbase"
    GEMINI = "gemini"
    BINANCE = "binance"

class CryptoTrader(ABC):
    def __init__(self, config_path="config.ini", test_mode=False):
        self.test_mode = test_mode
        self.portfolio = {"BTC": 0.0, "ETH": 0.0, "XRP": 0.0}
        self.logger = self._setup_logging()
        self.running = True
        self.config = self._load_config(config_path)
        self.exchange = self._initialize_exchange()
        self.finance_data = None
        
    def _setup_logging(self):
        logger = logging.getLogger('CryptoTrader')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('/var/log/crypto_trader.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _load_config(self, config_path):
        # In a production environment, this would read from a config file
        # For this example, returning hardcoded config
        return {
            'coinbase': {
                'api_key': 'your_coinbase_api_key',
                'api_secret': 'your_coinbase_secret',
                'sandbox_key': 'your_sandbox_key',
                'sandbox_secret': 'your_sandbox_secret'
            },
            'gemini': {
                'api_key': 'your_gemini_api_key',
                'api_secret': 'your_gemini_secret',
                'sandbox_key': 'your_sandbox_key',
                'sandbox_secret': 'your_sandbox_secret'
            },
            'binance': {
                'api_key': 'your_binance_api_key',
                'api_secret': 'your_binance_secret',
                'sandbox_key': 'your_sandbox_key',
                'sandbox_secret': 'your_sandbox_secret'
            }
        }

    @abstractmethod
    def _initialize_exchange(self):
        pass

    def get_finance_data(self):
        """Fetch market data from Yahoo Finance"""
        try:
            tickers = ['BTC-USD', 'ETH-USD', 'XRP-USD']
            self.finance_data = yf.download(tickers, period='1h', interval='1h')
            self.logger.info("Successfully fetched finance data")
        except Exception as e:
            self.logger.error(f"Error fetching finance data: {str(e)}")

    def calculate_arbitrage(self):
        """Calculate potential arbitrage opportunities"""
        if not self.finance_data or self.finance_data.empty:
            return None
        
        opportunities = {}
        for symbol in ['BTC', 'ETH', 'XRP']:
            market_price = self.finance_data['Close'][f'{symbol}-USD'].iloc[-1]
            try:
                order_book = self.exchange.fetch_order_book(f'{symbol}/USD')
                bid = order_book['bids'][0][0] if order_book['bids'] else None
                ask = order_book['asks'][0][0] if order_book['asks'] else None
                
                if bid and ask and market_price:
                    profit_potential = (bid - market_price) / market_price * 100
                    if profit_potential > 0.5:  # 0.5% threshold
                        opportunities[symbol] = {
                            'profit_potential': profit_potential,
                            'market_price': market_price,
                            'exchange_bid': bid,
                            'exchange_ask': ask
                        }
            except Exception as e:
                self.logger.error(f"Error calculating arbitrage for {symbol}: {str(e)}")
        
        return opportunities

    def execute_trades(self):
        """Execute trades based on arbitrage opportunities"""
        opportunities = self.calculate_arbitrage()
        if not opportunities:
            self.logger.info("No arbitrage opportunities found")
            return

        for symbol, data in opportunities.items():
            try:
                amount = 0.01  # Fixed trade size for example
                if not self.test_mode:
                    order = self.exchange.create_limit_buy_order(
                        f'{symbol}/USD',
                        amount,
                        data['market_price']
                    )
                    self.portfolio[symbol] += amount
                    self.logger.info(f"Executed buy order for {symbol}: {order}")
                else:
                    self.logger.info(f"Test mode: Would buy {amount} {symbol} at {data['market_price']}")
            except Exception as e:
                self.logger.error(f"Trade execution error for {symbol}: {str(e)}")

    def run(self):
        """Main trading loop"""
        schedule.every(1).hours.do(self.get_finance_data)
        schedule.every(1).hours.do(self.execute_trades)
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in main loop: {str(e)}")
                time.sleep(300)  # Wait 5 minutes before retrying

    def stop(self):
        """Graceful shutdown"""
        self.running = False
        self.logger.info("Shutting down trader")

class CoinbaseTrader(CryptoTrader):
    def _initialize_exchange(self):
        exchange_config = self.config['coinbase']
        return ccxt.coinbase({
            'apiKey': exchange_config['sandbox_key'] if self.test_mode else exchange_config['api_key'],
            'secret': exchange_config['sandbox_secret'] if self.test_mode else exchange_config['api_secret'],
            'enableRateLimit': True,
            'test': self.test_mode
        })

class GeminiTrader(CryptoTrader):
    def _initialize_exchange(self):
        exchange_config = self.config['gemini']
        return ccxt.gemini({
            'apiKey': exchange_config['sandbox_key'] if self.test_mode else exchange_config['api_key'],
            'secret': exchange_config['sandbox_secret'] if self.test_mode else exchange_config['api_secret'],
            'enableRateLimit': True,
            'test': self.test_mode
        })

class BinanceTrader(CryptoTrader):
    def _initialize_exchange(self):
        exchange_config = self.config['binance']
        return ccxt.binance({
            'apiKey': exchange_config['sandbox_key'] if self.test_mode else exchange_config['api_key'],
            'secret': exchange_config['sandbox_secret'] if self.test_mode else exchange_config['api_secret'],
            'enableRateLimit': True,
            'test': self.test_mode
        })

def signal_handler(signum, frame, trader):
    trader.stop()
    sys.exit(0)

def run_daemon(exchange_type, test_mode=False):
    trader_classes = {
        ExchangeType.COINBASE: CoinbaseTrader,
        ExchangeType.GEMINI: GeminiTrader,
        ExchangeType.BINANCE: BinanceTrader
    }
    
    trader = trader_classes[exchange_type](test_mode=test_mode)
    
    with daemon.DaemonContext(
        working_directory='/var/lib/crypto_trader',
        umask=0o002,
        pidfile=lockfile.FileLock('/var/run/crypto_trader.pid'),
        signal_map={
            signal.SIGTERM: lambda signum, frame: signal_handler(signum, frame, trader),
            signal.SIGINT: lambda signum, frame: signal_handler(signum, frame, trader)
        }
    ):
        trader.run()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Crypto Trading Daemon")
    parser.add_argument('--exchange', 
                       type=str, 
                       choices=['coinbase', 'gemini', 'binance'],
                       required=True,
                       help='Exchange to connect to')
    parser.add_argument('--test', 
                       action='store_true',
                       help='Run in test mode using sandbox API')
    
    args = parser.parse_args()
    exchange_map = {
        'coinbase': ExchangeType.COINBASE,
        'gemini': ExchangeType.GEMINI,
        'binance': ExchangeType.BINANCE
    }
    
    run_daemon(exchange_map[args.exchange], args.test)
