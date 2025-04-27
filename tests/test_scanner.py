import unittest
from unittest.mock import patch, MagicMock
from scanner import scan_for_arbitrage, save_opportunity, fetch_data_from_exchange
from data.models import ArbitrageOpportunity
from utils.logger import setup_logger, log_info, log_error

class TestScanner(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Настраивает логирование перед выполнением всех тестов.
        """
        setup_logger()  # Инициализация логирования
        log_info("Starting Scanner tests")  # Запись в лог о начале тестов

    def setUp(self):
        """
        Настройка тестов.
        """
        # Создание мок-объектов для бирж
        self.buy_exchange = MagicMock()
        self.sell_exchange = MagicMock()

        # Пример данных о криптовалютной паре
        self.pair = 'ETH/USD'
        self.proxies = {
            "http": "http://proxy.example.com:8080",
            "https": "https://proxy.example.com:8080"
        }

    @patch('scanner.EXCHANGES', {'BuyExchange': MagicMock(), 'SellExchange': MagicMock()})
    def test_fetch_data_from_exchange(self, mock_exchanges):
        """
        Тестирует функцию получения данных о криптовалютной паре.
        """
        # Настройка мока для ответа
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = {"price": 3000, "volume": 10}
        self.buy_exchange.get_pair_data.return_value = mock_response

        result = fetch_data_from_exchange(self.buy_exchange, self.pair, self.proxies)
        log_info(f"fetch_data_from_exchange result: {result}")

        # Проверка, что данные о цене и объеме получены правильно
        self.assertEqual(result['price'], 3000)
        self.assertEqual(result['volume'], 10)

    @patch('data.models.session')
    def test_save_opportunity(self, mock_session):
        """
        Тестирует сохранение арбитражной возможности в базу данных.
        """
        # Пример данных об арбитражной возможности
        opportunity = {
            "pair": self.pair,
            "buy_exchange": "BuyExchange",
            "sell_exchange": "SellExchange",
            "buy_price": 3000,
            "sell_price": 3100,
            "network": "Ethereum",
            "transfer_fee": 0.01,
            "transfer_time": "10 minutes",
            "spread": 3.33,
            "buy_volume": 10,
            "sell_volume": 10,
            "scan_time": "2024-07-23 12:00:00"
        }

        # Тестирование функции
        save_opportunity(opportunity)
        
        # Проверка вызова метода
        mock_session.add.assert_called_once()  # Проверка, что метод добавления записи вызван один раз
        mock_session.commit.assert_called_once()  # Проверка, что метод коммита вызван один раз

    @patch('scanner.EXCHANGES', {'BuyExchange': MagicMock(), 'SellExchange': MagicMock()})
    @patch('scanner.get_network_info')
    @patch('scanner.save_opportunity')
    def test_scan_for_arbitrage(self, mock_save_opportunity, mock_get_network_info, mock_exchanges):
        """
        Тестирует функцию сканирования для арбитража.
        """
        # Настройка мока для получения данных о парах
        mock_exchanges['BuyExchange'].get_pairs.return_value = ['ETH/USD']
        mock_exchanges['SellExchange'].get_pairs.return_value = ['ETH/USD']
        
        mock_response_buy = MagicMock(status_code=200)
        mock_response_buy.json.return_value = {"price": 3000, "volume": 10}
        mock_response_sell = MagicMock(status_code=200)
        mock_response_sell.json.return_value = {"price": 3100, "volume": 10}
        
        mock_exchanges['BuyExchange'].get_pair_data.return_value = mock_response_buy
        mock_exchanges['SellExchange'].get_pair_data.return_value = mock_response_sell
        mock_get_network_info.return_value = {"network": "Ethereum", "transfer_cost": 0.01, "transfer_time": "10 minutes"}

        # Выполнение функции
        results = scan_for_arbitrage(
            buy_exchange_name='BuyExchange',
            sell_exchange_name='SellExchange',
            min_spread=1.0,
            min_volume=1.0,
            proxies=self.proxies
        )
        log_info(f"scan_for_arbitrage results: {results}")

        # Проверка результатов
        self.assertIsInstance(results, list)  # Проверка, что результат является списком
        self.assertGreater(len(results), 0)  # Проверка, что список не пуст
        self.assertEqual(results[0]['pair'], 'ETH/USD')  # Проверка, что пара соответствует ожидаемой

    @patch('scanner.EXCHANGES', {'BuyExchange': MagicMock(), 'SellExchange': MagicMock()})
    @patch('scanner.get_network_info')
    @patch('scanner.save_opportunity')
    def test_scan_for_arbitrage_no_opportunity(self, mock_save_opportunity, mock_get_network_info, mock_exchanges):
        """
        Тестирует функцию сканирования для арбитража, когда нет арбитражных возможностей.
        """
        # Настройка мока для получения данных о парах
        mock_exchanges['BuyExchange'].get_pairs.return_value = ['ETH/USD']
        mock_exchanges['SellExchange'].get_pairs.return_value = ['ETH/USD']
        
        mock_response_buy = MagicMock(status_code=200)
        mock_response_buy.json.return_value = {"price": 3000, "volume": 10}
        mock_response_sell = MagicMock(status_code=200)
        mock_response_sell.json.return_value = {"price": 3000, "volume": 10}
        
        mock_exchanges['BuyExchange'].get_pair_data.return_value = mock_response_buy
        mock_exchanges['SellExchange'].get_pair_data.return_value = mock_response_sell
        mock_get_network_info.return_value = {"network": "Ethereum", "transfer_cost": 0.01, "transfer_time": "10 minutes"}

        # Выполнение функции
        results = scan_for_arbitrage(
            buy_exchange_name='BuyExchange',
            sell_exchange_name='SellExchange',
            min_spread=1.0,
            min_volume=1.0,
            proxies=self.proxies
        )
        log_info(f"scan_for_arbitrage results when no opportunity: {results}")

        # Проверка результатов
        self.assertIsInstance(results, list)  # Проверка, что результат является списком
        self.assertEqual(len(results), 0)  # Проверка, что список пуст

    @patch('scanner.EXCHANGES', {'BuyExchange': MagicMock(), 'SellExchange': MagicMock()})
    @patch('scanner.get_network_info')
    @patch('scanner.save_opportunity')
    def test_scan_for_arbitrage_exception(self, mock_save_opportunity, mock_get_network_info, mock_exchanges):
        """
        Тестирует функцию сканирования для арбитража, когда возникает исключение.
        """
        # Настройка мока для получения данных о парах
        mock_exchanges['BuyExchange'].get_pairs.side_effect = Exception("Test exception")
        
        with self.assertRaises(Exception):
            scan_for_arbitrage(
                buy_exchange_name='BuyExchange',
                sell_exchange_name='SellExchange',
                min_spread=1.0,
                min_volume=1.0,
                proxies=self.proxies
            )
        log_info("scan_for_arbitrage exception test passed")

    @classmethod
    def tearDownClass(cls):
        """
        Завершает логирование после выполнения всех тестов.
        """
        log_info("Scanner tests completed")  # Запись в лог о завершении тестов

if __name__ == "__main__":
    unittest.main()
