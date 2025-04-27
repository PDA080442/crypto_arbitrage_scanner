"""
Конфигурационный файл для настройки параметров приложения.
"""

import os

# URL-адреса API для каждой биржи
EXCHANGE_API_URLS = {
    "HTX": "https://api.htx.com",
    "OKX": "https://www.okx.com/api",
    "Bybit": "https://api.bybit.com",
    "Gate.io": "https://api.gateio.ws",
    "Bitget": "https://api.bitget.com",
    "MEXC": "https://api.mexc.com",
    "Kucoin": "https://api.kucoin.com",
    "CoinEX": "https://api.coinex.com",
    "Poloniex": "https://api.poloniex.com",
    "CommEX": "https://api.commex.com",
}

# Настройка базы данных
DATABASE_URL = os.getenv('DATABASE_URL', "sqlite:///your_database.db")  # URL подключения к базе данных

# Настройки API ключей для каждой биржи
EXCHANGE_API_KEYS = {
    "Bitget": {
        "API_KEY": os.getenv('BITGET_API_KEY', 'your_bitget_api_key'),
        "API_SECRET": os.getenv('BITGET_API_SECRET', 'your_bitget_api_secret'),
        "API_PASSPHRASE": os.getenv('BITGET_API_PASSPHRASE', 'your_bitget_api_passphrase')
    },
    "Bybit": {
        "API_KEY": os.getenv('BYBIT_API_KEY', 'your_bybit_api_key'),
        "API_SECRET": os.getenv('BYBIT_API_SECRET', 'your_bybit_api_secret')
    },
    "CoinEX": {
        "API_KEY": os.getenv('COINEX_API_KEY', 'your_coinex_api_key'),
        "API_SECRET": os.getenv('COINEX_API_SECRET', 'your_coinex_api_secret')
    },
    "Gate.io": {
        "API_KEY": os.getenv('GATEIO_API_KEY', 'your_gateio_api_key'),
        "API_SECRET": os.getenv('GATEIO_API_SECRET', 'your_gateio_api_secret')
    },
    "HTX": {
        "API_KEY": os.getenv('HTX_API_KEY', 'your_htx_api_key'),
        "API_SECRET": os.getenv('HTX_API_SECRET', 'your_htx_api_secret')
    },
    "Kucoin": {
        "API_KEY": os.getenv('KUCOIN_API_KEY', 'your_kucoin_api_key'),
        "API_SECRET": os.getenv('KUCOIN_API_SECRET', 'your_kucoin_api_secret'),
        "API_PASSPHRASE": os.getenv('KUCOIN_API_PASSPHRASE', 'your_kucoin_api_passphrase')
    },
    "MEXC": {
        "API_KEY": os.getenv('MEXC_API_KEY', 'your_mexc_api_key'),
        "API_SECRET": os.getenv('MEXC_API_SECRET', 'your_mexc_api_secret')
    },
    "OKX": {
        "API_KEY": os.getenv('OKX_API_KEY', 'your_okx_api_key'),
        "API_SECRET": os.getenv('OKX_API_SECRET', 'your_okx_api_secret'),
        "API_PASSPHRASE": os.getenv('OKX_API_PASSPHRASE', 'your_okx_api_passphrase')
    },
    "Poloniex": {
        "API_KEY": os.getenv('POLONIEX_API_KEY', 'your_poloniex_api_key'),
        "API_SECRET": os.getenv('POLONIEX_API_SECRET', 'your_poloniex_api_secret')
    },
    "CommEX": {
        "API_KEY": os.getenv('COMMEX_API_KEY', 'your_commex_api_key'),
        "API_SECRET": os.getenv('COMMEX_API_SECRET', 'your_commex_api_secret')
    }
}

def get_api_credentials(exchange_name):
    """
    Возвращает API ключи и секреты для указанной биржи.

    :param exchange_name: Название биржи.
    :return: Словарь с API ключами и секретами.
    """
    return EXCHANGE_API_KEYS.get(exchange_name, {})

def get_api_url(exchange_name):
    """
    Возвращает URL для указанной биржи.

    :param exchange_name: Название биржи.
    :return: URL для API биржи.
    """
    return EXCHANGE_API_URLS.get(exchange_name, '')

# Пример использования
if __name__ == "__main__":
    exchange_name = "Bitget"
    credentials = get_api_credentials(exchange_name)
    api_url = get_api_url(exchange_name)
    print(f"API URL for {exchange_name}: {api_url}")
    print(f"API credentials for {exchange_name}: {credentials}")
