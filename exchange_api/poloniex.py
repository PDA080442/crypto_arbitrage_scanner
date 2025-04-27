import requests
import logging
import os
import time

# Ваши API ключ и секрет
API_KEY = "7LWG66E8-Y56PB1PX-N8TZ0FKK-VGQYG7A4"
API_SECRET = "bc17ae2f2b28213a5e3a272f3e7b34d1287c76c0"

# Базовый URL для API Poloniex
BASE_URL = "https://api.poloniex.com"

# Настройка логирования
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, "poloniex_api.log")
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Очистка файла результатов перед новым запуском
result_dir = "resultstxt"
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

result_file = os.path.join(result_dir, "poloniex_result.txt")
open(result_file, 'w').close()

# Файл для хранения пар
pairs_dir = "pairs"
if not os.path.exists(pairs_dir):
    os.makedirs(pairs_dir)

pairs_file = os.path.join(pairs_dir, "POLONIEX_pairs.txt")

def get_request(endpoint, params=None):
    """
    Выполняет GET запрос к API Poloniex с аутентификацией.

    :param endpoint: Конечная точка API.
    :param params: Параметры запроса.
    :return: Ответ запроса в формате JSON.
    """
    url = f"{BASE_URL}{endpoint}"
    if params is None:
        params = {}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        log_info(f"Ответ от {url}: {response.text}")
        return response.json()
    except requests.RequestException as e:
        log_error(f"Запрос к {url} не удался: {e}")
        return {}

def get_pairs():
    """
    Получает список торговых пар с биржи Poloniex.

    :return: Список торговых пар.
    """
    endpoint = "/markets"
    data = get_request(endpoint)
    return [symbol['symbol'] for symbol in data if 'USDT' in symbol['symbol']] if data else []

def get_price(pair):
    """
    Получает цену для торговой пары с биржи Poloniex.

    :param pair: Торговая пара.
    :return: Цена торговой пары.
    """
    endpoint = f"/markets/{pair}/price"
    data = get_request(endpoint)
    if data and "price" in data:
        return float(data["price"])
    return 0.0

def get_volume(pair):
    """
    Получает объем для торговой пары с биржи Poloniex в USDT.

    :param pair: Торговая пара.
    :return: Объем торговой пары в USDT.
    """
    endpoint = "/markets/ticker24h"
    data = get_request(endpoint)
    if data:
        for ticker in data:
            if ticker['symbol'] == pair:
                price = get_price(pair)
                if 'quoteVolume' in ticker:
                    return float(ticker['quoteVolume'])
                elif 'quantity' in ticker:
                    return float(ticker['quantity']) * price
                elif 'amount' in ticker:
                    return float(ticker['amount']) * price
    return 0.0

def save_pairs_to_file(pairs):
    """
    Сохраняет пары в файл.

    :param pairs: Список пар.
    """
    with open(pairs_file, 'w') as f:
        for pair in pairs:
            f.write(f"{pair}\n")

def load_pairs_from_file():
    """
    Загружает пары из файла.

    :return: Список пар.
    """
    with open(pairs_file, 'r') as f:
        pairs = [line.strip() for line in f]
    return pairs

def log_info(message):
    logger.info(message)
    print(message)

def log_error(message):
    logger.error(message)
    print(message)

if __name__ == "__main__":
    pairs = get_pairs()
    log_info(f"Pairs: {pairs}")

    # Сохранение пар в файл
    save_pairs_to_file(pairs)

    with open(result_file, 'a') as f:
        # Загрузка пар из файла и форматирование для отчета
        pairs = load_pairs_from_file()
        for pair in pairs:
            price = get_price(pair)
            volume_usdt = get_volume(pair)
            if price == 0.0 and volume_usdt == 0.0:
                log_error(f"Invalid pair skipped: {pair}")
                continue
            formatted_volume = f"{int(volume_usdt):,}".replace(",", " ")
            display_pair = pair.replace('_', '')  # Удаляем разделитель для отображения
            message_price = f"Цена для {display_pair}: {price:.6f}"
            message_volume = f"Объем для {display_pair}: {formatted_volume}"
            log_info(message_price)
            log_info(message_volume)
            f.write(f"Пара: {display_pair}, {message_price}, {message_volume}\n")
            f.flush()  # Ensure data is written to the file immediately

    log_info(f"Results have been written to {result_file}")
    print(f"Results have been written to {result_file}")
  