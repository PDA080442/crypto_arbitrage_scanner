import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
import logging
import os

# Ваши API ключ и секрет
API_KEY = "7K9vUPvEqIJNzWPCO0"
API_SECRET = "8D1uFPTd1MCYTcUzKZT8t7co"

# Базовый URL для API MEXC
BASE_URL = "https://api.mexc.com"

# Настройка логирования
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, "mexc_api.log")
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Очистка файла результатов перед новым запуском
result_dir = "resultstxt"
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

result_file = os.path.join(result_dir, "mexc_result.txt")
open(result_file, 'w').close()

def get_request(endpoint, params=None, auth_required=False):
    """
    Выполняет GET запрос к API MEXC с опциональной аутентификацией.

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
    timestamp = str(int(time.time() * 1000))
    query_string = urlencode(params)
    payload = f"{timestamp}{method}{endpoint}{query_string}"
    signature = hmac.new(API_SECRET.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()

    return {
        'MX-API-KEY': API_KEY,
        'MX-API-SIGN': signature,
        'MX-API-TIMESTAMP': timestamp,
        'Content-Type': 'application/json'
    }

def get_pairs():
    """
    Получает список торговых пар с биржи MEXC.

    :return: Список торговых пар.
    """
    endpoint = "/api/v3/ticker/price"
    data = get_request(endpoint)
    log_info(f"Data received for pairs: {data}")
    return [symbol['symbol'] for symbol in data]

def get_price_and_volume(pair):
    """
    Получает цену и объем в USDT для торговой пары с биржи MEXC.

    :param pair: Торговая пара.
    :return: Цена и объем торговой пары в USDT.
    """
    endpoint = f"/api/v3/ticker/24hr?symbol={pair}"
    data = get_request(endpoint)
    if data:
        price = float(data.get("lastPrice", 0.0))
        volume_usdt = float(data.get("quoteVolume", 0.0))
        return price, volume_usdt
    return 0.0, 0.0

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
            formatted_volume = f"{int(volume_usdt):,}".replace(",", " ")
            message_price = f"Цена для {pair}: {price:.6f}"
            message_volume = f"Объем для {pair}: {formatted_volume}"
            log_info(message_price)
            log_info(message_volume)
            f.write(f"Пара: {pair}, {message_price}, {message_volume}\n")
            f.flush()  # Ensure data is written to the file immediately

    log_info(f"Results have been written to {result_file}")
    print(f"Results have been written to {result_file}")
  