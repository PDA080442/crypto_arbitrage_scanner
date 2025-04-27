import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode
import sys
import os
import logging

# Ваши API ключ и секрет
API_KEY = "B2E7BEF5326046DB95A40317ED9BA779"
API_SECRET = "43EE3E5AD26B5C58744A80D399BEFCDF68F4AC64C26FEF0D"

# Базовый URL для API CoinEX
BASE_URL = "https://api.coinex.com"

# Директория для логов
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = os.path.join(log_dir, "coinex_api.log")

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(log_filename),
    logging.StreamHandler(sys.stdout)
])
logger = logging.getLogger(__name__)

# Директория для результатов
results_dir = "resultstxt"
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

results_filepath = os.path.join(results_dir, "coinex_result.txt")

def get_request(endpoint, params=None):
    """
    Выполняет GET запрос к API CoinEX с аутентификацией.

    :param endpoint: Конечная точка API.
    :param params: Параметры запроса.
    :return: Ответ запроса в формате JSON.
    """
    url = f"{BASE_URL}{endpoint}"
    if params is None:
        params = {}
    headers = create_auth_headers("GET", endpoint, params)

    try:
        response = requests.get(url, headers=headers, params=params)
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        logger.info(f"Response body: {response.json()}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Request to {url} failed: {e}")
        return {}

def create_auth_headers(method, endpoint, params):
    """
    Создает заголовки аутентификации для запроса.

    :param method: HTTP метод.
    :param endpoint: Конечная точка API.
    :param params: Параметры запроса.
    :return: Словарь с заголовками.
    """
    timestamp = str(int(time.time()))
    str_to_sign = method + endpoint + timestamp + urlencode(params)
    signature = hmac.new(API_SECRET.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    return {
        'ACCESS-KEY': API_KEY,
        'ACCESS-SIGN': signature,
        'ACCESS-TIMESTAMP': timestamp,
        'Content-Type': 'application/json'
    }

def get_pairs():
    """
    Получает список торговых пар с биржи CoinEX.

    :return: Список торговых пар.
    """
    endpoint = "/v1/market/list"
    data = get_request(endpoint)
    return data.get("data", [])

def get_price_and_volume(pair):
    """
    Получает цену и объем в USDT для торговой пары с биржи CoinEX.

    :param pair: Торговая пара.
    :return: Цена и объем торговой пары в USDT.
    """
    endpoint = f"/v1/market/ticker?market={pair}"
    data = get_request(endpoint)
    if data and "data" in data:
        ticker = data["data"]["ticker"]
        price = float(ticker["last"])  # Получение последней цены
        volume_base_currency = float(ticker.get("vol", 0.0))  # Получение объема в базовой валюте
        volume_usdt = volume_base_currency * price  # Рассчет объема в USDT
        return price, volume_usdt
    return 0.0, 0.0 

# Использование функции:
pair = "BTCUSDT"
price, volume_usdt = get_price_and_volume(pair)
print(f"Цена: {price}, Объем в USDT: {volume_usdt}")


def write_results_to_file(filepath, data):
    """
    Записывает данные в файл.

    :param filepath: Путь к файлу.
    :param data: Данные для записи.
    """
    with open(filepath, 'a') as file:
        file.write(data + '\n')

if __name__ == "__main__":
    # Очистка файла перед записью новых данных
    open(results_filepath, 'w').close()

    # Пример использования функций
    pairs = get_pairs()
    logger.info(f"Pairs: {pairs}")

    for pair in pairs:
        price, volume_usdt = get_price_and_volume(pair)
        formatted_price = f"{price:,.6f}"
        formatted_volume = f"{int(volume_usdt):,}".replace(",", " ")  # Форматируем объем без десятичных знаков и заменяем запятые пробелами
        logger.info(f"Цена для {pair}: {formatted_price}")
        logger.info(f"Объем для {pair}: {formatted_volume}")

        # Запись результатов в файл
        result_data = f"Пара: {pair}, Цена: {formatted_price}, Объем: {formatted_volume}"
        write_results_to_file(results_filepath, result_data)
        
        time.sleep(1)  # Добавляем задержку, чтобы избежать превышения лимита запросов
 