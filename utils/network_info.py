# # utils/network_info.py

# from utils.logger import log_info, log_error
# import requests

# # Вставьте ваш действительный ключ API от Etherscan
# ETHERSCAN_API_KEY = 'XUX63NX7S7WGNQ5ZVFZWGZGWJDN1MJX9WA'

# def get_eth_transfer_fee():
#     """
#     Получает комиссию за перевод ETH в гейгаях (gwei).
#     Возвращает комиссию в ETH.
#     """
#     url = "https://api.etherscan.io/api"
#     params = {
#         "module": "gastracker",
#         "action": "gasoracle",
#         "apikey": ETHERSCAN_API_KEY  # Используйте реальный ключ API
#     }
#     try:
#         log_info(f"Sending request to {url} with params {params}")
#         response = requests.get(url, params=params)
#         response.raise_for_status()  # Проверяет успешность запроса
#         data = response.json()

#         # Логирование для отладки
#         log_info(f"API response: {data}")

#         # Проверка ответа API и возврат значения
#         if data['status'] == '1':  # Убедитесь, что статус успешный
#             gas_price_gwei = float(data['result']['SafeGasPrice'])  # Используем SafeGasPrice для более стабильной цены
#             log_info(f"Gas Price in Gwei: {gas_price_gwei}")
#             return gas_price_gwei / 1e9  # Комиссия в ETH
#         else:
#             error_message = data.get('message', 'Unknown error')
#             log_error(f"API returned an error: {error_message}")
#             raise ValueError(f"API error: {error_message}")
#     except requests.RequestException as req_err:
#         log_error(f"Request error occurred while fetching ETH transfer fee: {req_err}")
#         raise
#     except ValueError as val_err:
#         log_error(f"Value error occurred while fetching ETH transfer fee: {val_err}")
#         raise
#     except Exception as e:
#         log_error(f"Unexpected exception occurred while fetching ETH transfer fee: {e}")
#         raise  # Перебрасываем исключение дальше

# def get_network_info(pair):
#     """
#     Получает информацию о сети для криптовалютной пары.
    
#     :param pair: Криптовалютная пара
#     :return: Словарь с информацией о сети
#     """
#     try:
#         if 'ETH' in pair:
#             transfer_fee = get_eth_transfer_fee()
#             log_info(f"Transfer fee for {pair}: {transfer_fee}")
#             return {
#                 "network": "Ethereum",
#                 "transfer_cost": transfer_fee,
#                 "transfer_time": "10 minutes"  # Временные данные, уточните по необходимости
#             }
#         # Добавьте другие сети и обработку здесь
#         else:
#             log_info(f"Network information for {pair} is unknown.")
#             return {
#                 "network": "Unknown",
#                 "transfer_cost": 0.0,
#                 "transfer_time": "N/A"
#             }
#     except Exception as e:
#         log_error(f"Exception occurred while getting network info for {pair}: {e}")
#         return {
#             "network": "Error",
#             "transfer_cost": 0.0,
#             "transfer_time": "Error"
#         }

# # Пример использования функций
# if __name__ == "__main__":
#     try:
#         eth_fee = get_eth_transfer_fee()
#         print(f"ETH Transfer Fee: {eth_fee} ETH")
        
#         network_info = get_network_info("ETH/USDT")
#         print(f"Network Info: {network_info}")
#     except Exception as e:
#         log_error(f"Error in example usage: {e}")
