# arbitrage-trader
Cryptocurrency Auto Arbitrage Trader

The Crypto Arbitrage Trader is written in Python, specifically designed to run as a daemon process on MacOS, and could easily run on Linux. This code has not been tested in a Windows Python environment, although it *should* work. I may make a script for Windows at some point, but this script is currently not expected to function in a Windows environment. The script has a "test" mode, to allow performance monitoring without live trades on the exchanges, so please use that first!

- The script's call frequency is every 60 minutes to prevent rate-limiting on the exchanges and it executes any arbitrage opportunities during each call.
- This script is designed to maintain a portfolio of BTC, ETC, and XRP, although you could modify it to your portfolio preferences
- The script uses Yahoo Finance for market data comparison.

To achieve "high/er frequency" trading, you could spread a portfolio across all three exchanges (Coinbase, Gemini, Binance) and leverage multiple instances of this script, scheduled "X" minutes apart from one another. I would consider this an experimental feature. In other words, I have not tried/tested it with this script, but in theory, it would work.  Example: Coinbase at 0, Gemini at 15, Binance at 30, and Coinbase at 45, would give you a run on a portion of the "total portfolio" every 15 minutes, without also making a call to the same exchange API every 15 minutes. You just want to play around with the run definition (search for "Main Trading Loop") in the script. In theory, it'd work, but the exchange APIs may rate-limit you if you're not careful.

Use this script at your own risk! Remember, whether you use this script, or another trading "bot," you are responsible for the trades in your portfolio. Trade wisely, and never trade more than you can live without! PLEASE ALWAYS TRADE IN THE EXCHANGE SANDBOX FIRST WITH ANY NEW BOTS/SCRIPTS/AUTOMATED TECHNIQUES.

Another approach to safely testing this script or other "bot" traders would be to transfer your existing portfolio of selected coins into a wallet, and then buy a small amount of "seed coins" in the live portfolio. That way you can execute live trades without also messing with your "real" portfolio. This will "cost" money though, in gas fees to move back and forth to the wallet, so it may not be practical for large portfolios.

Here are the key characteristics of the arbitrage logic:

=Simple Price Differential=

- Uses a straightforward comparison between external market price (from Yahoo Finance) and exchange bid price
- Focuses on selling at the exchange bid price rather than buying at the ask price

=Profit-Oriented=

- Only considers opportunities where the exchange bid exceeds the market price
- Aims to capitalize on buying at market price (assumed available) and selling at exchange bid

=Threshold-Based=

- Implements a minimum profit threshold (0.5%) to filter out marginal opportunities
- Helps account for trading fees and execution risk

=Installation and Usage=

Prerequisites for Python environment on MacOS:
<code>pip3 install python-daemon lockfile ccxt yfinance schedule</code>

Create the Files and Folders:
- Save the script as crypto_trader.py
- Make executable: chmod +x crypto_trader.py
- Create necessary directories:

<code>sudo mkdir -p /var/lib/crypto_trader
sudo mkdir -p /var/log
sudo chown $USER /var/lib/crypto_trader /var/log</code>

Configuration:

The script includes a placeholder **_load_config** method. In production, you should:

- Create a **config.ini** file with API credentials
- Modify **_load_config** to read from this file Example **config.ini**:

<code>[coinbase]
api_key = your_key
api_secret = your_secret
sandbox_key = your_sandbox_key
sandbox_secret = your_sandbox_secret

[gemini]
api_key = your_key
api_secret = your_secret
sandbox_key = your_sandbox_key
sandbox_secret = your_sandbox_secret

[binance]
api_key = your_key
api_secret = your_secret
sandbox_key = your_sandbox_key
sandbox_secret = your_sandbox_secret</code>

Usage:

<code># Run with Coinbase in live mode
./crypto_trader.py --exchange coinbase

# Run with Gemini in test mode
./crypto_trader.py --exchange gemini --test</code>

=Features=

- Exchange Support
-- Coinbase
-- Gemini
-- Binance
-- Easily extensible to other CCXT-supported exchanges

- Trading Logic
-- Hourly trade execution
-- Arbitrage detection (>0.5% profit potential)
-- Fixed trade size (0.01 units)
-- Portfolio tracking

- Safety Features
-- Rate limiting enabled
-- Test mode support
-- Error logging
-- Graceful shutdown

- Monitoring
-- Logs to /var/log/crypto_trader.log
-- Includes timestamps and error details

- Class Structure
-- CryptoTrader (Abstract Base Class)
-- Defines core trading functionality
-- Implements portfolio management
-- Handles scheduling and logging

- CoinbaseTrader, GeminiTrader, BinanceTrader
-- Exchange-specific implementations
-- Handle API initialization

- Methods
-- get_finance_data(): Fetches market data from Yahoo Finance
-- calculate_arbitrage(): Identifies trading opportunities
-- execute_trades(): Places orders based on arbitrage
-- run(): Main daemon loop
-- _initialize_exchange(): Sets up exchange connection

- Error Handling
-- Logs all errors to file
-- Continues running after recoverable errors
-- Implements a 5-minute delay after critical errors

- Troubleshooting
-- Check /var/log/crypto_trader.log for errors
-- Verify API credentials
-- Ensure sufficient permissions
-- Test connectivity in test mode first
