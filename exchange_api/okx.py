import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
import logging
import os

# Ваши API ключ, секрет и пароль
API_KEY = "9cd99cb2-af3b-4805-a772-b18150c0bce3"
API_SECRET = "4E8400287AB067EA3FAACE2135D32CB2"
API_PASSPHRASE = "PopravkinDanil080442!!!"

# Базовый URL для API OKX
BASE_URL = "https://www.okx.com"

# Настройка логирования
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, "okx_api.log")
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
  
# Очистка файла результатов перед новым запуском
result_dir = "resultstxt"
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

result_file = os.path.join(result_dir, "okx_result.txt")
open(result_file, 'w').close()

# Файл для хранения пар
pairs_dir = "pairs"
if not os.path.exists(pairs_dir):
    os.makedirs(pairs_dir)

pairs_file = os.path.join(pairs_dir, "OKX_pairs.txt")

def get_request(endpoint, params=None, auth_required=False):
    """
    Выполняет GET запрос к API OKX с опциональной аутентификацией.

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
        log_info(f"Ответ от {url}: {response.text}")
        return response.json()
    except requests.RequestException as e:
        log_error(f"Запрос к {url} не удался: {e}")
        return {}

def create_auth_headers(method, endpoint, params):
    """
    Создает заголовки аутентификации для запроса.

    :param method: HTTP метод.
    :param endpoint: Конечная точка API.
    :param params: Параметры запроса.
    :return: Словарь с заголовками.
    """
    now = str(time.time())
    str_to_sign = f"{now}{method}{endpoint}{urlencode(params)}"
    signature = hmac.new(API_SECRET.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest()
    signature_base64 = hashlib.sha256(signature).hexdigest()

    return {
        'OK-ACCESS-KEY': API_KEY,
        'OK-ACCESS-SIGN': signature_base64,
        'OK-ACCESS-TIMESTAMP': now,
        'OK-ACCESS-PASSPHRASE': API_PASSPHRASE,
        'Content-Type': 'application/json'
    }

def get_pairs():
    """
    Получает список торговых пар с биржи OKX.

    :return: Список торговых пар.
    """
    endpoint = "/api/v5/market/tickers?instType=SPOT"
    data = get_request(endpoint)
    return [symbol['instId'] for symbol in data.get("data", [])]

def get_price(pair):
    """
    Получает цену для торговой пары с биржи OKX.

    :param pair: Торговая пара.
    :return: Цена торговой пары.
    """
    endpoint = f"/api/v5/market/ticker?instId={pair}"
    data = get_request(endpoint)
    if data and "data" in data:
        return float(data["data"][0]["last"])
    return 0.0

def get_volume(pair):
    """
    Получает объем для торговой пары с биржи OKX.

    :param pair: Торговая пара.
    :return: Объем торговой пары.
    """
    endpoint = f"/api/v5/market/ticker?instId={pair}"
    data = get_request(endpoint)
    if data and "data" in data:
        return float(data["data"][0]["volCcy24h"])
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
            price, volume_usdt = get_price(pair), get_volume(pair)
            if price == 0.0 and volume_usdt == 0.0:
                log_error(f"Invalid pair skipped: {pair}")
                continue
            formatted_volume = f"{int(volume_usdt):,}".replace(",", " ")
            display_pair = pair.replace('-', '')  # Удаляем разделитель для отображения
            message_price = f"Цена для {display_pair}: {price:.6f}"
            message_volume = f"Объем для {display_pair}: {formatted_volume}"
            log_info(message_price)
            log_info(message_volume)
            f.write(f"Пара: {display_pair}, {message_price}, {message_volume}\n")
            f.flush()  # Ensure data is written to the file immediately

    log_info(f"Results have been written to {result_file}")
    print(f"Results have been written to {result_file}")
