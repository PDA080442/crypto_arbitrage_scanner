# tests/test_exchange_api.py

import unittest
from unittest.mock import patch
from exchange_api import htx
from utils.logger import setup_logger, log_info, log_error

class TestHTXAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Настраивает логирование перед выполнением всех тестов.
        """
        setup_logger()  # Инициализация логирования
        log_info("Starting HTX API tests")  # Запись в лог о начале тестов

    def test_get_pairs(self):
        """
        Тестирует функцию получения торговых пар.
        """
        # Мокаем функцию get_request в модуле exchange_api.htx
        with patch('exchange_api.htx.get_request') as mock_get_request:
            # Определяем возвращаемое значение для мока
            mock_get_request.return_value = {"data": ["BTC/USDT", "ETH/USDT"]}
            try:
                pairs = htx.get_pairs()  # Вызов тестируемой функции
                log_info(f"get_pairs result: {pairs}")  # Логируем результат

                self.assertIsInstance(pairs, list, "Pairs should be a list")  # Проверка, что результат является списком
                self.assertGreater(len(pairs), 0, "Pairs list should not be empty")  # Проверка, что список не пуст
            except Exception as e:
                log_error(f"Exception in test_get_pairs: {e}")  # Логирование ошибки
                self.fail(f"test_get_pairs failed due to exception: {e}")  # Пометка теста как проваленного

    def test_get_price(self):
        """
        Тестирует функцию получения цены торговой пары.
        """
        # Мокаем функцию get_request в модуле exchange_api.htx
        with patch('exchange_api.htx.get_request') as mock_get_request:
            # Определяем возвращаемое значение для мока
            mock_get_request.return_value = {"data": {"price": 30000.0}}
            try:
                price = htx.get_price("BTC/USDT")  # Вызов тестируемой функции
                log_info(f"get_price result: {price}")  # Логируем результат

                self.assertIsInstance(price, float, "Price should be a float")  # Проверка, что результат является числом с плавающей точкой
                self.assertGreater(price, 0, "Price should be greater than 0")  # Проверка, что цена больше 0
            except Exception as e:
                log_error(f"Exception in test_get_price: {e}")  # Логирование ошибки
                self.fail(f"test_get_price failed due to exception: {e}")  # Пометка теста как проваленного

    def test_get_volume(self):
        """
        Тестирует функцию получения объема торговой пары.
        """
        # Мокаем функцию get_request в модуле exchange_api.htx
        with patch('exchange_api.htx.get_request') as mock_get_request:
            # Определяем возвращаемое значение для мока
            mock_get_request.return_value = {"data": {"volume": 1000.0}}
            try:
                volume = htx.get_volume("BTC/USDT")  # Вызов тестируемой функции
                log_info(f"get_volume result: {volume}")  # Логируем результат

                self.assertIsInstance(volume, float, "Volume should be a float")  # Проверка, что результат является числом с плавающей точкой
                self.assertGreater(volume, 0, "Volume should be greater than 0")  # Проверка, что объем больше 0
            except Exception as e:
                log_error(f"Exception in test_get_volume: {e}")  # Логирование ошибки
                self.fail(f"test_get_volume failed due to exception: {e}")  # Пометка теста как проваленного

    @classmethod
    def tearDownClass(cls):
        """
        Завершает логирование после выполнения всех тестов.
        """
        log_info("HTX API tests completed")  # Запись в лог о завершении тестов

if __name__ == "__main__":
    unittest.main()  # Запуск всех тестов
