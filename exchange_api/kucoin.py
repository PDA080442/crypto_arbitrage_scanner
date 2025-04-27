import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
import sys
import os
import logging

# Директория для логов
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = os.path.join(log_dir, "kucoin_api.log")

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(log_filename),
    logging.StreamHandler(sys.stdout)
])
logger = logging.getLogger(__name__)

# Ваши API ключ, секрет и пароль
API_KEY = "6277f8c07e72f4000666f2da"
API_SECRET = "16941bb2-79ea-4da6-8d39-000bf1b7df39"
API_PASSPHRASE = "PopravkinDanil080442"

# Базовый URL для API KuCoin
BASE_URL = "https://api.kucoin.com"

# Директория для результатов
results_dir = "resultstxt"
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

results_filepath = os.path.join(results_dir, "kucoin_result.txt")

# Директория для пар
pairs_dir = "pairs"
if not os.path.exists(pairs_dir):
    os.makedirs(pairs_dir)

pairs_filepath = os.path.join(pairs_dir, "kucoin_pairs.txt")

def get_request(endpoint, params=None):
    """
    Выполняет GET запрос к API KuCoin с аутентификацией.

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
        logger.info(f"Response body: {response.text}")
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
    now = str(int(time.time() * 1000))
    str_to_sign = now + method + endpoint + urlencode(params)
    signature = hmac.new(API_SECRET.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest()
    signature_base64 = signature.hex()

    return {
        'KC-API-KEY': API_KEY,
        'KC-API-SIGN': signature_base64,
        'KC-API-TIMESTAMP': now,
        'KC-API-PASSPHRASE': API_PASSPHRASE,
        'Content-Type': 'application/json'
    }

def get_pairs():
    """
    Получает список торговых пар с биржи KuCoin.

    :return: Список торговых пар.
    """
    endpoint = "/api/v1/symbols"
    data = get_request(endpoint)
    return [symbol['symbol'] for symbol in data.get("data", [])]

def get_price(pair):
    """
    Получает цену для торговой пары с биржи KuCoin.

    :param pair: Торговая пара.
    :return: Цена торговой пары.
    """
    endpoint = f"/api/v1/market/orderbook/level1?symbol={pair}"
    data = get_request(endpoint)
    if data and "data" in data:
        return float(data["data"]["price"])
    return 0.0

def get_volume(pair):
    """
    Получает объем для торговой пары с биржи KuCoin.

    :param pair: Торговая пара.
    :return: Объем торговой пары.
    """
    endpoint = f"/api/v1/market/stats?symbol={pair}"
    data = get_request(endpoint)
    if data and "data" in data:
        return float(data["data"]["volValue"])
    return 0.0

def write_pairs_to_file(filepath, pairs):
    """
    Записывает пары в файл.

    :param filepath: Путь к файлу.
    :param pairs: Список пар.
    """
    with open(filepath, 'w') as file:
        for pair in pairs:
            file.write(pair + '\n')

def read_pairs_from_file(filepath):
    """
    Считывает пары из файла и удаляет символ "-".

    :param filepath: Путь к файлу.
    :return: Список пар без символа "-".
    """
    pairs = []
    with open(filepath, 'r') as file:
        for line in file:
            pair = line.strip().replace('-', '')
            pairs.append(pair)
    return pairs

def write_results_to_file(filepath, data):
    """
    Записывает данные в файл.

    :param filepath: Путь к файлу.
    :param data: Данные для записи.
    """
    with open(filepath, 'a') as file:
        file.write(data + '\n')

if __name__ == "__main__":
    # Очистка файлов перед записью новых данных
    open(results_filepath, 'w').close()
    open(pairs_filepath, 'w').close()

    # Получение и запись пар
    pairs = get_pairs()
    write_pairs_to_file(pairs_filepath, pairs)
    logger.info(f"Pairs: {pairs}")

    # Считывание пар для использования в API
    api_pairs = [line.strip() for line in open(pairs_filepath, 'r')]

    # Считывание пар и удаление символа "-" для отчета
    formatted_pairs = read_pairs_from_file(pairs_filepath)

    for api_pair, formatted_pair in zip(api_pairs, formatted_pairs):
        price = get_price(api_pair)
        volume = get_volume(api_pair)
        formatted_price = f"{price:,.6f}"
        formatted_volume = f"{int(volume):,}".replace(",", " ")  # Форматируем объем без десятичных знаков и заменяем запятые пробелами
        logger.info(f"Цена для {formatted_pair}: {formatted_price}")
        logger.info(f"Объем для {formatted_pair}: {formatted_volume}")

        # Запись результатов в файл
        result_data = f"Пара: {formatted_pair}, Цена: {formatted_price}, Объем: {formatted_volume}"
        write_results_to_file(results_filepath, result_data)

        time.sleep(1)  # Добавляем задержку, чтобы избежать превышения лимита запросов

    logger.info(f"Results have been written to {results_filepath}")
    print(f"Results have been written to {results_filepath}")
  