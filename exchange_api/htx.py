# htx.py

import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode
import logging
import os

# Ваши API ключ и секрет
API_KEY = "bd1fcf4b-3835-4a67-bc1f-4b43c43a92a8"
API_SECRET = "aeff8b34-04a5-48c4-9d90-3e44a45b4828"

# Базовый URL для API HTX
BASE_URL = "https://api.htx.com"

# Настройка логирования
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, "htx_api.log")
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levellevelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Очистка файла результатов перед новым запуском
result_dir = "resultstxt"
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

result_file = os.path.join(result_dir, "htx_result.txt")
open(result_file, 'w').close()

def get_request(endpoint, params=None, auth_required=False):
    """
    Выполняет GET запрос к API HTX с опциональной аутентификацией.

    :param endpoint: Конечная точка API.
    :param params: Параметры запроса.
    :param auth_required: Флаг, требуется ли аутентификация.
    :return: Ответ запроса в формате JSON.
    """
    url = f"{BASE_URL}{endpoint}"
    if params is None:
        params = {}
    headers = create_auth_headers("GET", endpoint, params) if auth_required else {}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        log_info(f"Response from {url}: {response.text}")
        return response.json()
    except requests.RequestException as e:
        log_error(f"Request to {url} failed: {e}")
        return {}

def create_auth_headers(method, endpoint, params):
    """
    Создает заголовки аутентификации для запроса.

    :param method: HTTP метод.
    :param endpoint: Конечная точка API.
    :param params: Параметры запроса.
    :return: Словарь с заголовками.
    """
    now = str(int(time.time() * 1000))
    str_to_sign = f"{method}{endpoint}{now}{urlencode(params)}"
    signature = hmac.new(API_SECRET.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    return {
        'HT-ACCESS-KEY': API_KEY,
        'HT-ACCESS-SIGN': signature,
        'HT-ACCESS-TIMESTAMP': now,
        'Content-Type': 'application/json'
    }

def get_pairs():
    """
    Получает список торговых пар с биржи HTX.

    :return: Список торговых пар.
    """
    endpoint = "/v1/common/symbols"
    data = get_request(endpoint, auth_required=True)
    log_info(f"Data received for pairs: {data}")
    return [symbol['symbol'].upper() for symbol in data.get("data", [])]

def get_price_and_volume(pair):
    """
    Получает цену и объем в USDT за последние 24 часа для торговой пары с биржи HTX.

    :param pair: Торговая пара.
    :return: Цена и объем торговой пары в USDT за последние 24 часа.
    """
    endpoint = f"/market/detail/merged?symbol={pair.lower()}"
    data = get_request(endpoint)
    if data and data.get("status") == "ok" and "tick" in data:
        ticker = data["tick"]
        price = float(ticker["close"])
        volume_base_currency = float(ticker.get("vol", 0.0))
        volume_usdt = volume_base_currency * price
        return price, volume_base_currency
    return 0.0, 0.0

def format_pair(pair):
    """
    Форматирует пару для отображения, добавляя пробел между валютами.
    
    :param pair: Торговая пара.
    :return: Отформатированная пара.
    """
    if 'USDT' in pair:
        return pair.replace('USDT', ' USDT')
    return pair

def log_info(message):
    logger.info(message)
    print(message)

def log_error(message):
    logger.error(message)
    print(message)

if __name__ == "__main__":
    pairs = get_pairs()
    log_info(f"Pairs: {pairs}")

    with open(result_file, 'a') as f:
        for pair in pairs:
            price, volume_usdt = get_price_and_volume(pair)
            if price == 0.0 and volume_usdt == 0.0:
                log_error(f"Invalid pair skipped: {pair}")
                continue
            formatted_pair = format_pair(pair)
            formatted_volume = f"{int(volume_usdt):,}".replace(",", " ")
            message_price = f"Цена для {formatted_pair}: {price:.6f}"
            message_volume = f"Объем для {formatted_pair}: {formatted_volume}"
            log_info(message_price)
            log_info(message_volume)
            f.write(f"Пара: {formatted_pair}, {message_price}, {message_volume}\n")
            f.flush()  # Ensure data is written to the file immediately

    log_info(f"Results have been written to {result_file}")
    print(f"Results have been written to {result_file}")
   