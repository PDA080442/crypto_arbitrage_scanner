# tests/test_network_info.py

import unittest
from unittest.mock import patch, MagicMock
from utils.network_info import get_eth_transfer_fee, get_network_info
from utils.logger import setup_logger, log_info, log_error

class TestNetworkInfo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Настраивает логирование перед выполнением всех тестов.
        """
        setup_logger()  # Инициализация логирования
        log_info("Starting Network Info tests")  # Запись в лог о начале тестов

    @patch('utils.network_info.requests.get')
    def test_get_eth_transfer_fee(self, mock_get):
        """
        Тестирует получение комиссии за перевод ETH.
        """
        # Создаем мок ответа от API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "1",
            "result": {
                "SafeGasPrice": "50"
            }
        }
        mock_get.return_value = mock_response

        try:
            fee = get_eth_transfer_fee()  # Вызов тестируемой функции
            log_info(f"get_eth_transfer_fee result: {fee}")  # Логируем результат

            self.assertIsInstance(fee, float, "Fee should be a float")  # Проверка, что результат является числом с плавающей точкой
            self.assertGreater(fee, 0, "Fee should be greater than 0")  # Проверка, что комиссия больше 0
        except Exception as e:
            log_error(f"Exception in test_get_eth_transfer_fee: {e}")  # Логирование ошибки
            self.fail(f"Exception occurred: {e}")  # Пометка теста как проваленного

    @patch('utils.network_info.get_eth_transfer_fee')
    def test_get_network_info(self, mock_get_eth_transfer_fee):
        """
        Тестирует получение информации о сети для криптовалютной пары.
        """
        mock_get_eth_transfer_fee.return_value = 0.00005  # Пример значения комиссии

        try:
            info = get_network_info("ETH/USD")  # Вызов тестируемой функции
            log_info(f"get_network_info result: {info}")  # Логируем результат

            self.assertEqual(info["network"], "Ethereum", "Network should be 'Ethereum'")  # Проверка, что сеть - Ethereum
            self.assertIsInstance(info["transfer_cost"], float, "Transfer cost should be a float")  # Проверка, что комиссия - float
            self.assertGreater(info["transfer_cost"], 0, "Transfer cost should be greater than 0")  # Проверка, что комиссия больше 0
            self.assertEqual(info["transfer_cost"], 0.00005, "Transfer cost should match the mock value")  # Проверка значения комиссии
            self.assertEqual(info["transfer_time"], "10 minutes", "Transfer time should be '10 minutes'")  # Проверка времени перевода
        except Exception as e:
            log_error(f"Exception in test_get_network_info: {e}")  # Логирование ошибки
            self.fail(f"Exception occurred: {e}")  # Пометка теста как проваленного

    @patch('utils.network_info.requests.get')
    def test_get_eth_transfer_fee_api_error(self, mock_get):
        """
        Тестирует получение комиссии за перевод ETH при ошибке API.
        """
        # Создаем мок ответа с ошибкой от API
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with self.assertRaises(Exception, msg="Should raise an exception for API error"):
            get_eth_transfer_fee()  # Проверка, что функция выбрасывает исключение при ошибке API

    @patch('utils.network_info.requests.get')
    def test_get_eth_transfer_fee_invalid_response(self, mock_get):
        """
        Тестирует получение комиссии за перевод ETH при некорректном ответе API.
        """
        # Создаем мок некорректного ответа от API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "0",
            "result": {}
        }
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError, msg="Should raise a ValueError for invalid API response"):
            get_eth_transfer_fee()  # Проверка, что функция выбрасывает исключение при некорректном ответе API

    @classmethod
    def tearDownClass(cls):
        """
        Завершает логирование после выполнения всех тестов.
        """
        log_info("Network Info tests completed")  # Запись в лог о завершении тестов

if __name__ == "__main__":
    unittest.main()  # Запуск всех тестов
