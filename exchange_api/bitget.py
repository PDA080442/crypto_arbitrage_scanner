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

log_filename = os.path.join(log_dir, "bitget_api.log")

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(log_filename),
    logging.StreamHandler(sys.stdout)
])
logger = logging.getLogger(__name__)

# Ваши API ключ, секрет и пароль
API_KEY = "bg_7842cf926886ad54fe813eeccb3a24a7"
API_SECRET = "4ccde3bdad36f5e27b31bbf154992bf842c4682c4eb5c93f4b2a6f5b488b35fc"
API_PASSPHRASE = "PopravkinDanil080442"

# Базовый URL для API Bitget
BASE_URL = "https://api.bitget.com"

# Директория для результатов
results_dir = "resultstxt"
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

results_filepath = os.path.join(results_dir, "bitget_result.txt")

def get_request(endpoint, params=None):
    """
    Выполняет GET запрос к API Bitget с аутентификацией.

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
    signature_base64 = hashlib.sha256(signature).hexdigest()

    return {
        'BG-ACCESS-KEY': API_KEY,
        'BG-ACCESS-SIGN': signature_base64,
        'BG-ACCESS-TIMESTAMP': now,
        'BG-ACCESS-PASSPHRASE': API_PASSPHRASE,
        'Content-Type': 'application/json'
    }

def get_pairs():
    """
    Получает список торговых пар с биржи Bitget.

    :return: Список торговых пар.
    """
    endpoint = "/api/spot/v1/public/products"
    data = get_request(endpoint)
    return [symbol['symbol'].replace('_SPBL', '') for symbol in data.get("data", [])]

def get_price(pair):
    """
    Получает цену для торговой пары с биржи Bitget.

    :param pair: Торговая пара.
    :return: Цена торговой пары.
    """
    endpoint = f"/api/spot/v1/market/ticker"
    params = {'symbol': f"{pair}_SPBL"}
    data = get_request(endpoint, params)
    logger.info(f"Data received for price: {data}")  # Добавлено логирование для отладки
    if data and "data" in data:
        if isinstance(data["data"], list) and len(data["data"]) > 0:
            return float(data["data"][0].get("close", 0.0))  # Изменено получение данных
        elif isinstance(data["data"], dict):
            return float(data["data"].get("close", 0.0))
    logger.error(f"No price data found for pair: {pair}")
    return 0.0

def get_volume(pair):
    """
    Получает объем в USDT для торговой пары с биржи Bitget.

    :param pair: Торговая пара.
    :return: Объем торговой пары в USDT.
    """
    endpoint = f"/api/spot/v1/market/ticker"
    params = {'symbol': f"{pair}_SPBL"}
    data = get_request(endpoint, params)
    logger.info(f"Full data received for volume: {data}")  # Логирование полного ответа API
    if data and "data" in data:
        logger.info(f"Checking data type: {type(data['data'])}")  # Логируем тип данных
        if isinstance(data["data"], list) and len(data["data"]) > 0:
            logger.info(f"Volume data (list): {data['data'][0]}")  # Логируем полные данные
            volume = data["data"][0].get("quoteVol", None)  # Используем "quoteVol" для объема в USDT
            logger.info(f"Extracted volume: {volume}")
            return float(volume) if volume is not None else 0.0  # Убедитесь, что ключ соответствует ожидаемому
        elif isinstance(data["data"], dict):
            logger.info(f"Volume data (dict): {data['data']}")  # Логируем полные данные
            volume = data["data"].get("quoteVol", None)  # Используем "quoteVol" для объема в USDT
            logger.info(f"Extracted volume: {volume}")
            return float(volume) if volume is not None else 0.0
    logger.error(f"No volume data found for pair: {pair}")
    return 0.0

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
        price = get_price(pair)
        volume = get_volume(pair)
        formatted_price = f"{price:,.6f}"
        formatted_volume = f"{int(volume):,}".replace(",", " ")  # Форматируем объем без десятичных знаков и заменяем запятые пробелами
        logger.info(f"Цена для {pair}: {formatted_price}")
        logger.info(f"Объем для {pair}: {formatted_volume}")
        
        # Запись результатов в файл
        result_data = f"Пара: {pair}, Цена: {formatted_price}, Объем: {formatted_volume}"
        write_results_to_file(results_filepath, result_data)
        
        time.sleep(1)  # Добавляем задержку, чтобы избежать превышения лимита запросов
