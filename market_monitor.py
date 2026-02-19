"""
JARVIS - Market Monitor
Kriptovalyuta va aksiya narxlarini real vaqtda kuzatish.
"""
import requests
from utils import setup_logger

class MarketMonitor:
    def __init__(self):
        self.logger = setup_logger("MarketMonitor")
        # Biz bepul va kalit talab qilmaydigan API-lardan foydalanamiz
        self.crypto_api = "https://api.coingecko.com/api/v3/simple/price"
        self.stock_api = "https://query1.finance.yahoo.com/v7/finance/quote"

    def get_crypto_price(self, symbol="bitcoin"):
        """Kriptovalyuta narxini olish"""
        symbol = symbol.lower()
        params = {
            'ids': symbol,
            'vs_currencies': 'usd'
        }
        try:
            response = requests.get(self.crypto_api, params=params)
            data = response.json()
            if symbol in data:
                price = data[symbol]['usd']
                return f"{symbol.capitalize()} narxi hozirda {price} AQSH dollarini tashkil etmoqda, janob."
            else:
                return f"Kechirasiz, {symbol} bo'yicha ma'lumot topilmadi."
        except Exception as e:
            self.logger.error(f"Crypto API error: {e}")
            return f"Kriptovalyuta narxini olishda xatolik: {e}"

    def get_stock_price(self, symbol="AAPL"):
        """Aksiya narxini olish (Yahoo Finance orqali)"""
        symbol = symbol.upper()
        url = f"{self.stock_api}?symbols={symbol}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            result = data['quoteResponse']['result']
            if result:
                price = result[0]['regularMarketPrice']
                name = result[0].get('longName', symbol)
                return f"{name} ({symbol}) aksiyasi narxi {price} dollarni tashkil etmoqda, janob."
            else:
                return f"Kechirasiz, {symbol} aksiyasi bo'yicha ma'lumot topilmadi."
        except Exception as e:
            self.logger.error(f"Stock API error: {e}")
            return f"Aksiya narxini olishda xatolik: {e}"

    def get_raw_crypto_price(self, symbol="bitcoin"):
        """Get only the numeric price"""
        symbol = symbol.lower()
        try:
            response = requests.get(self.crypto_api, params={'ids': symbol, 'vs_currencies': 'usd'})
            data = response.json()
            return data.get(symbol, {}).get('usd', 0)
        except: return 0

    def get_raw_stock_price(self, symbol="AAPL"):
        """Get only the numeric price"""
        symbol = symbol.upper()
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(f"{self.stock_api}?symbols={symbol}", headers=headers)
            data = response.json()
            result = data['quoteResponse']['result']
            return result[0]['regularMarketPrice'] if result else 0
        except: return 0

if __name__ == "__main__":

    # Test
    mm = MarketMonitor()
    print(mm.get_crypto_price("bitcoin"))
    print(mm.get_stock_price("TSLA"))
