import requests
import pandas as pd
import yfinance as yf
from typing import Dict, List, Optional
import time

class IndianStockDataFetcher:
    def __init__(self):
        self.base_url = "https://latest-stock-price.p.rapidapi.com"
        self.nse_url = "https://www.nseindia.com/api"

    def get_nse_stocks(self) -> List[Dict]:
        """Fetch NSE stock data using free endpoints"""
        try:
            # NSE equity list
            url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                return self.get_fallback_nifty50_stocks()

        except Exception as e:
            print(f"Error fetching NSE data: {e}")
            return self.get_fallback_nifty50_stocks()

    def get_fallback_nifty50_stocks(self) -> List[Dict]:
        """Fallback Nifty 50 stock list with symbols"""
        nifty50_symbols = [
            'ADANIPORTS', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE',
            'BAJAJFINSV', 'BPCL', 'BHARTIARTL', 'BRITANNIA', 'CIPLA',
            'COALINDIA', 'DIVISLAB', 'DRREDDY', 'EICHERMOT', 'GRASIM',
            'HCLTECH', 'HDFCBANK', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO',
            'HINDUNILVR', 'ICICIBANK', 'ITC', 'INDUSINDBK', 'INFY',
            'JSWSTEEL', 'KOTAKBANK', 'LT', 'M&M', 'MARUTI',
            'NTPC', 'NESTLEIND', 'ONGC', 'POWERGRID', 'RELIANCE',
            'SBILIFE', 'SBIN', 'SUNPHARMA', 'TCS', 'TATACONSUM',
            'TATAMOTORS', 'TATASTEEL', 'TECHM', 'TITAN', 'ULTRACEMCO',
            'UPL', 'WIPRO'
        ]

        return [{'symbol': symbol} for symbol in nifty50_symbols]

    def get_stock_details_yfinance(self, symbol: str) -> Optional[Dict]:
        """Get detailed stock information using yfinance"""
        try:
            # Add .NS suffix for NSE stocks
            yf_symbol = f"{symbol}.NS"
            stock = yf.Ticker(yf_symbol)

            # Get stock info
            info = stock.info
            hist = stock.history(period="1mo")

            if hist.empty:
                return None

            latest_price = hist['Close'].iloc[-1]
            volume = hist['Volume'].iloc[-1]

            # Calculate momentum (30-day price change)
            if len(hist) > 1:
                momentum = ((latest_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
            else:
                momentum = 0

            return {
                'symbol': symbol,
                'companyName': info.get('longName', symbol),
                'currentPrice': round(latest_price, 2),
                'volume': int(volume),
                'marketCap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'pb_ratio': info.get('priceToBook', 0),
                'roe': info.get('returnOnEquity', 0),
                'profit_margin': info.get('profitMargins', 0),
                'momentum_30d': round(momentum, 2),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown')
            }

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    def get_multiple_stocks_data(self, symbols: List[str], max_stocks: int = 20) -> pd.DataFrame:
        """Fetch data for multiple stocks with rate limiting"""
        stock_data = []

        for i, symbol in enumerate(symbols[:max_stocks]):
            print(f"Fetching data for {symbol} ({i+1}/{min(len(symbols), max_stocks)})")
            data = self.get_stock_details_yfinance(symbol)

            if data:
                stock_data.append(data)

            # Rate limiting to avoid being blocked
            time.sleep(0.5)

        return pd.DataFrame(stock_data)