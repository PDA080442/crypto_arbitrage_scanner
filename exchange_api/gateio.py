import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
import logging
import os

# Ваши API ключ и секрет
API_KEY = "bd1fcf4b-3835-4a67-bc1f-4b43c43a92a8"
API_SECRET = "aeff8b34-04a5-48c4-9d90-3e44a45b4828"

# Базовый URL для API Gate.io
BASE_URL = "https://api.gateio.ws"

# Настройка логирования
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, "gateio_api.log")
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Очистка файла результатов перед новым запуском
result_dir = "resultstxt"
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

result_file = os.path.join(result_dir, "gateio_result.txt")
open(result_file, 'w').close()

# Директория для хранения пар
pairs_dir = "pairs"
if not os.path.exists(pairs_dir):
    os.makedirs(pairs_dir)

pairs_file = os.path.join(pairs_dir, "Gate.io_pairs.txt")
open(pairs_file, 'w').close()

def get_request(endpoint, params=None, auth_required=False):
    """
    Выполняет GET запрос к API Gate.io с опциональной аутентификацией.

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
    query_string = urlencode(params) if params else ""
    payload = f"{method}\n{endpoint}\n{query_string}\n{now}"
    signature = hmac.new(API_SECRET.encode('utf-8'), payload.encode('utf-8'), hashlib.sha512).hexdigest()

    return {
        'KEY': API_KEY,
        'SIGN': signature,
        'Timestamp': now,
        'Content-Type': 'application/json'
    }

def get_pairs():
    """
    Получает список торговых пар с биржи Gate.io.

    :return: Список торговых пар.
    """
    endpoint = "/api/v4/spot/currency_pairs"
    data = get_request(endpoint, auth_required=False)  # Пробуем без аутентификации
    log_info(f"Data received for pairs: {data}")
    return [symbol['id'] for symbol in data] if isinstance(data, list) else []

def get_price_and_volume(pair):
    """
    Получает цену и объем в USDT для торговой пары с биржи Gate.io.

    :param pair: Торговая пара.
    :return: Цена и объем торговой пары в USDT.
    """
    endpoint = f"/api/v4/spot/tickers?currency_pair={pair}"
    data = get_request(endpoint)
    if data:
        ticker = data[0]
        log_info(f"Ticker data for {pair}: {ticker}")  # Логирование данных тикера
        price = float(ticker["last"])
        volume_base_currency = float(ticker.get("base_volume", 0.0))
        volume_usdt = volume_base_currency * price
        return price, volume_usdt
    return 0.0, 0.0

def log_info(message):
    logger.info(message)
    print(message)

def log_error(message):
    logger.error(message)
    print(message)

def write_pairs_to_file(pairs):
    """
    Записывает пары в файл.
    """
    with open(pairs_file, 'w') as f:
        for pair in pairs:
            f.write(pair + '\n')

def read_pairs_from_file():
    """
    Считывает пары из файла.
    """
    pairs = []
    with open(pairs_file, 'r') as f:
        for line in f:
            pairs.append(line.strip())
    return pairs

if __name__ == "__main__":
    pairs = get_pairs()
    log_info(f"Pairs: {pairs}")

    # Записываем пары в файл
    write_pairs_to_file(pairs)

    # Считываем пары из файла
    pairs_from_file = read_pairs_from_file()

    with open(result_file, 'a') as f:
        for pair in pairs_from_file:
            price, volume_usdt = get_price_and_volume(pair)  # Используем оригинальную пару для запроса данных
            display_pair = pair.replace('_', '')  # Удаляем разделитель для отображения
            formatted_volume = f"{int(volume_usdt):,}".replace(",", " ")
            message_price = f"Цена для {display_pair}: {price:.6f}"
            message_volume = f"Объем для {display_pair}: {formatted_volume}"
            log_info(message_price)
            log_info(message_volume)
            f.write(f"Пара: {display_pair}, {message_price}, {message_volume}\n")
            f.flush()  # Ensure data is written to the file immediately

    log_info(f"Results have been written to {result_file}")
    print(f"Results have been written to {result_file}")
 