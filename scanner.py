# scanner.py

import os
import logging
from exchange_api.htx import get_pairs as htx_get_pairs, get_price_and_volume as htx_get_price_and_volume
from exchange_api.okx import get_pairs as okx_get_pairs, get_price as okx_get_price, get_volume as okx_get_volume
from exchange_api.gateio import get_pairs as gateio_get_pairs, get_price_and_volume as gateio_get_price_and_volume
from exchange_api.bitget import get_pairs as bitget_get_pairs, get_price as bitget_get_price, get_volume as bitget_get_volume
from exchange_api.mexc import get_pairs as mexc_get_pairs, get_price_and_volume as mexc_get_price_and_volume
from exchange_api.kucoin import get_pairs as kucoin_get_pairs, get_price as kucoin_get_price, get_volume as kucoin_get_volume
from exchange_api.coinex import get_pairs as coinex_get_pairs, get_price_and_volume as coinex_get_price_and_volume
from exchange_api.poloniex import get_pairs as poloniex_get_pairs, get_price as poloniex_get_price, get_volume as poloniex_get_volume

# Директория для хранения пар и результатов
pairs_dir = "pairs"
if not os.path.exists(pairs_dir):
    os.makedirs(pairs_dir)

results_file = "scan_results.txt"
unknown_nets_file = "unk_nets.txt"

# Очистка файла результатов перед новым запуском
open(results_file, 'w').close()

EXCHANGES = {
    "HTX": (htx_get_pairs, htx_get_price_and_volume),
    "OKX": (okx_get_pairs, okx_get_price, okx_get_volume),
    "Gate.io": (gateio_get_pairs, gateio_get_price_and_volume),
    "Bitget": (bitget_get_pairs, bitget_get_price, bitget_get_volume),
    "MEXC": (mexc_get_pairs, mexc_get_price_and_volume),
    "Kucoin": (kucoin_get_pairs, kucoin_get_price, kucoin_get_volume),
    "CoinEX": (coinex_get_pairs, coinex_get_price_and_volume),
    "Poloniex": (poloniex_get_pairs, poloniex_get_price, poloniex_get_volume),
}

logger = logging.getLogger(__name__)

def save_pairs_to_file(exchange_name, pairs):
    """
    Сохраняет пары в файл.
    
    :param exchange_name: Имя биржи.
    :param pairs: Список пар.
    """
    filename = os.path.join(pairs_dir, f"{exchange_name}_pairs.txt")
    with open(filename, 'w') as f:
        for pair in pairs:
            f.write(f"{pair}\n")

def load_pairs_from_file(exchange_name):
    """
    Загружает пары из файла.
    
    :param exchange_name: Имя биржи.
    :return: Список пар.
    """
    filename = os.path.join(pairs_dir, f"{exchange_name}_pairs.txt")
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            pairs = [line.strip() for line in f]
        return pairs
    return []

def format_pair_for_report(exchange, pair):
    if exchange in ["Kucoin", "Gate.io", "OKX", "Poloniex"]:
        return pair.replace('-', '').replace('_', '')
    return pair

def format_pair(pair):
    """
    Форматирует пару для отображения, добавляя пробел между валютами.
    
    :param pair: Торговая пара.
    :return: Отформатированная пара.
    """
    if 'USDT' in pair:
        return pair.replace('USDT', ' USDT')
    return pair

def load_nets():
    """
    Загружает сети для монет из файла nets.txt.
    
    :return: Словарь сетей для монет.
    """
    nets = {}
    with open("nets.txt", 'r') as f:
        for line in f:
            if '/' in line:
                coin, network = line.strip().split('/')
                if coin in nets:
                    nets[coin].append(network)
                else:
                    nets[coin] = [network]
    return nets

def get_network_for_coin(coin, nets):
    """
    Получает сеть для монеты из словаря сетей.
    
    :param coin: Название монеты.
    :param nets: Словарь сетей для монет.
    :return: Сеть для монеты.
    """
    if coin in nets:
        return ", ".join(nets[coin])
    else:
        with open(unknown_nets_file, 'a') as f:
            f.write(f"{coin}\n")
        return "Unknown"

def save_results_to_file(results):
    """
    Сохраняет результаты сканирования в файл.
    
    :param results: Список результатов.
    """
    with open(results_file, 'a') as f:
        for result in results:
            f.write(f"{result}\n")

def scan_for_arbitrage(buy_exchange, sell_exchange, min_spread, min_volume, stop_event):
    if not buy_exchange or not sell_exchange:
        logger.info("Либо buy_exchange, либо Sell_exchange пусто.")
        return []

    buy_pairs_func, buy_price_and_volume_func = EXCHANGES[buy_exchange][:2]
    sell_pairs_func, sell_price_and_volume_func = EXCHANGES[sell_exchange][:2]

    # Загрузка пар из файлов, если они существуют, иначе получение пар с биржи и сохранение в файлы
    buy_pairs = load_pairs_from_file(buy_exchange)
    if not buy_pairs:
        logger.info(f"Загрузка пар для {buy_exchange} из API.")
        buy_pairs = buy_pairs_func()
        save_pairs_to_file(buy_exchange, buy_pairs)
    else:
        logger.info(f"Загрузка пар для {buy_exchange} из файла: {buy_pairs}")

    sell_pairs = load_pairs_from_file(sell_exchange)
    if not sell_pairs:
        logger.info(f"Загрузка пар для {sell_exchange} из API.")
        sell_pairs = sell_pairs_func()
        save_pairs_to_file(sell_exchange, sell_pairs)
    else:
        logger.info(f"Загрузка пар для {sell_exchange} из файла: {sell_pairs}")

    nets = load_nets()
    opportunities = []

    for buy_pair in buy_pairs:
        formatted_buy_pair = format_pair_for_report(buy_exchange, buy_pair)
        for sell_pair in sell_pairs:
            formatted_sell_pair = format_pair_for_report(sell_exchange, sell_pair)
            if stop_event.is_set():
                logger.info("Сканирование остановлено пользователем")
                break

            if formatted_buy_pair == formatted_sell_pair and "USDT" in buy_pair:
                logger.info(f"Обработка пары {buy_pair}")
                if len(EXCHANGES[buy_exchange]) == 2:
                    buy_price, buy_volume = buy_price_and_volume_func(buy_pair)
                else:
                    buy_price = EXCHANGES[buy_exchange][1](buy_pair)
                    buy_volume = EXCHANGES[buy_exchange][2](buy_pair)

                if len(EXCHANGES[sell_exchange]) == 2:
                    sell_price, sell_volume = sell_price_and_volume_func(sell_pair)
                else:
                    sell_price = EXCHANGES[sell_exchange][1](sell_pair)
                    sell_volume = EXCHANGES[sell_exchange][2](sell_pair)

                logger.info(f"Цена покупки: {buy_price}, Цена продажи: {sell_price}, Объем покупок: {buy_volume}, объем продаж: {sell_volume}")

                if buy_price and sell_price:
                    spread = (sell_price - buy_price) / buy_price * 100
                    if spread >= min_spread:
                        if buy_volume >= min_volume and sell_volume >= min_volume:
                            coin = buy_pair.split('USDT')[0]
                            network = get_network_for_coin(coin, nets)
                            opportunity = {
                                "Пара": format_pair(formatted_buy_pair),
                                "Биржа покупки": buy_exchange,
                                "Биржа продажи": sell_exchange,
                                "Цена покупки": buy_price,
                                "Цена продажи": sell_price,
                                "Спред": spread,
                                "Объем покупок": buy_volume,
                                "Объем продаж": sell_volume,
                                "Сеть": network
                            }
                            opportunities.append(opportunity)
                            logger.info(f"Возможности для арбитража найдены: {opportunity}")
                        else:
                            logger.info(f"Объема недостаточно для пары {buy_pair}: Объем покупки={buy_volume}, Объем продажи={sell_volume}")
                    else:
                        logger.info(f"Спред недостаточен для пары {buy_pair}: Спред={spread}")
                else:
                    logger.info(f"Цена недоступна за пару {buy_pair}: Цена покупки={buy_price}, Цена продажи={sell_price}")

    # Сохранение результатов в файл
    save_results_to_file(opportunities)

    return opportunities
