import unittest
from scanner import scan_for_arbitrage
from utils.logger import setup_logger, log_info, log_error
from data.models import session, ArbitrageOpportunity

class TestIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Настраивает логирование и инициализацию перед выполнением всех тестов.
        """
        setup_logger()  # Настройка логирования
        log_info("Starting integration tests")  # Запись в лог о начале выполнения тестов

    def setUp(self):
        """
        Очищает базу данных перед каждым тестом.
        """
        self.session = session
        self.session.query(ArbitrageOpportunity).delete()
        self.session.commit()

    def tearDown(self):
        """
        Очищает базу данных после каждого теста.
        """
        self.session.query(ArbitrageOpportunity).delete()
        self.session.commit()

    def test_integration_htx_okx(self):
        """
        Тестирует интеграцию различных модулей приложения для пар HTX и OKX.
        """
        log_info("Running integration test for scan_for_arbitrage: HTX -> OKX")  # Запись в лог о начале теста
        try:
            result = scan_for_arbitrage("HTX", "OKX", 0.1, 1000)  # Выполнение функции сканирования арбитража
            log_info(f"scan_for_arbitrage result: {result}")  # Запись результата в лог
            
            self.assertIsInstance(result, list, "Result should be a list")  # Проверка, что результат является списком
            if result:
                self._validate_result_structure(result[0])  # Проверка структуры первого элемента результата
                
                # Проверяем, что запись была добавлена в базу данных
                db_result = self.session.query(ArbitrageOpportunity).first()
                self.assertIsNotNone(db_result, "Database should have at least one record")
                self._validate_db_record(db_result)
        except Exception as e:
            log_error(f"Exception during integration test for HTX -> OKX: {e}")  # Логирование ошибки
            self.fail(f"Integration test for HTX -> OKX failed due to exception: {e}")  # Пометка теста как проваленного

    def test_integration_bybit_gateio(self):
        """
        Тестирует интеграцию различных модулей приложения для пар Bybit и Gate.io.
        """
        log_info("Running integration test for scan_for_arbitrage: Bybit -> Gate.io")  # Запись в лог о начале теста
        try:
            result = scan_for_arbitrage("Bybit", "Gate.io", 0.1, 1000)  # Выполнение функции сканирования арбитража
            log_info(f"scan_for_arbitrage result: {result}")  # Запись результата в лог
            
            self.assertIsInstance(result, list, "Result should be a list")  # Проверка, что результат является списком
            if result:
                self._validate_result_structure(result[0])  # Проверка структуры первого элемента результата
                
                # Проверяем, что запись была добавлена в базу данных
                db_result = self.session.query(ArbitrageOpportunity).first()
                self.assertIsNotNone(db_result, "Database should have at least one record")
                self._validate_db_record(db_result)
        except Exception as e:
            log_error(f"Exception during integration test for Bybit -> Gate.io: {e}")  # Логирование ошибки
            self.fail(f"Integration test for Bybit -> Gate.io failed due to exception: {e}")  # Пометка теста как проваленного

    def _validate_result_structure(self, result_item):
        """
        Проверяет структуру результата.
        
        :param result_item: элемент результата для проверки
        """
        self.assertIn("pair", result_item, "Result item should contain 'pair'")  # Проверка наличия ключа 'pair'
        self.assertIn("buy_exchange", result_item, "Result item should contain 'buy_exchange'")  # Проверка наличия ключа 'buy_exchange'
        self.assertIn("sell_exchange", result_item, "Result item should contain 'sell_exchange'")  # Проверка наличия ключа 'sell_exchange'
        self.assertIn("buy_price", result_item, "Result item should contain 'buy_price'")  # Проверка наличия ключа 'buy_price'
        self.assertIn("sell_price", result_item, "Result item should contain 'sell_price'")  # Проверка наличия ключа 'sell_price'
        self.assertIn("network", result_item, "Result item should contain 'network'")  # Проверка наличия ключа 'network'
        self.assertIn("transfer_fee", result_item, "Result item should contain 'transfer_fee'")  # Проверка наличия ключа 'transfer_fee'
        self.assertIn("transfer_time", result_item, "Result item should contain 'transfer_time'")  # Проверка наличия ключа 'transfer_time'
        self.assertIn("spread", result_item, "Result item should contain 'spread'")  # Проверка наличия ключа 'spread'
        self.assertIn("buy_volume", result_item, "Result item should contain 'buy_volume'")  # Проверка наличия ключа 'buy_volume'
        self.assertIn("sell_volume", result_item, "Result item should contain 'sell_volume'")  # Проверка наличия ключа 'sell_volume'
        self.assertIn("scan_time", result_item, "Result item should contain 'scan_time'")  # Проверка наличия ключа 'scan_time'

    def _validate_db_record(self, db_record):
        """
        Проверяет запись в базе данных.
        
        :param db_record: запись из базы данных для проверки
        """
        self.assertIsInstance(db_record.pair, str, "pair should be a string")
        self.assertIsInstance(db_record.buy_exchange, str, "buy_exchange should be a string")
        self.assertIsInstance(db_record.sell_exchange, str, "sell_exchange should be a string")
        self.assertIsInstance(db_record.buy_price, float, "buy_price should be a float")
        self.assertIsInstance(db_record.sell_price, float, "sell_price should be a float")
        self.assertIsInstance(db_record.network, str, "network should be a string")
        self.assertIsInstance(db_record.transfer_fee, float, "transfer_fee should be a float")
        self.assertIsInstance(db_record.transfer_time, str, "transfer_time should be a string")
        self.assertIsInstance(db_record.spread, float, "spread should be a float")
        self.assertIsInstance(db_record.buy_volume, float, "buy_volume should be a float")
        self.assertIsInstance(db_record.sell_volume, float, "sell_volume should be a float")
        self.assertIsInstance(db_record.scan_time, str, "scan_time should be a string")

    @classmethod
    def tearDownClass(cls):
        """
        Завершает логирование после выполнения всех тестов.
        """
        log_info("Integration tests completed")  # Запись в лог о завершении выполнения тестов

if __name__ == "__main__":
    unittest.main()  # Запуск всех тестов
