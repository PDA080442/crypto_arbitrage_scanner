import unittest
import os
import pandas as pd
from utils.export_to_excel import export_to_excel
from data.models import ArbitrageOpportunity, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from utils.logger import setup_logger, log_info, log_error

class TestExcelExporter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Настраивает тестовую базу данных и добавляет пример данных перед запуском всех тестов.
        """
        setup_logger()  # Настройка логирования
        log_info("Setting up test database")

        # Настройка тестовой базы данных
        cls.engine = create_engine('sqlite:///test_database.db')  # Создание движка базы данных
        Base.metadata.create_all(cls.engine)  # Создание всех таблиц в базе данных
        cls.Session = sessionmaker(bind=cls.engine)  # Создание класса сессии
        cls.session = cls.Session()  # Инициализация сессии

        # Добавление примера данных об арбитражной возможности
        example_opportunity = ArbitrageOpportunity(
            id=str(uuid.uuid4()),  # Уникальный идентификатор
            pair="BTC/USDT",  # Криптовалютная пара
            buy_exchange="HTX",  # Биржа покупки
            sell_exchange="OKX",  # Биржа продажи
            buy_price=30000.0,  # Цена покупки
            sell_price=30500.0,  # Цена продажи
            network="Ethereum",  # Сеть
            transfer_fee=0.01,  # Комиссия за перевод
            transfer_time="10 minutes",  # Время перевода
            spread=1.67,  # Спред
            buy_volume=100.0,  # Объем покупки
            sell_volume=100.0,  # Объем продажи
            scan_time="2024-07-24 12:00:00"  # Время сканирования
        )
        cls.session.add(example_opportunity)  # Добавление записи в сессию
        cls.session.commit()  # Сохранение изменений в базе данных
        log_info("Test data added to database")

    @classmethod
    def tearDownClass(cls):
        """
        Удаляет тестовую базу данных после завершения всех тестов.
        """
        log_info("Tearing down test database")
        cls.session.close()  # Закрытие сессии
        Base.metadata.drop_all(cls.engine)  # Удаление всех таблиц
        os.remove('test_database.db')  # Удаление файла базы данных
        log_info("Test database removed")

    def test_export_to_excel(self):
        """
        Тестирует функцию экспорта данных в Excel.
        """
        log_info("Running test_export_to_excel")

        # Имя тестового файла
        test_filename = "test_arbitrage_report.xlsx"

        try:
            # Вызов функции экспорта
            export_to_excel(test_filename)
            log_info(f"Excel file created: {test_filename}")

            # Проверка, что файл создан
            self.assertTrue(os.path.exists(test_filename), "Excel file should be created")

            # Проверка содержимого файла
            df = pd.read_excel(test_filename)  # Чтение данных из Excel файла
            self.assertFalse(df.empty, "Excel file should not be empty")  # Проверка, что файл не пуст
            expected_columns = [
                "pair", "buy_exchange", "sell_exchange", "buy_price", "sell_price", 
                "network", "transfer_fee", "transfer_time", "spread", 
                "buy_volume", "sell_volume", "scan_time"
            ]
            # Проверка, что все ожидаемые колонки присутствуют в файле
            self.assertTrue(all(col in df.columns for col in expected_columns), "Excel file should contain all expected columns")

            # Проверка данных
            self.assertEqual(df.iloc[0]["pair"], "BTC/USDT")
            self.assertEqual(df.iloc[0]["buy_exchange"], "HTX")
            self.assertEqual(df.iloc[0]["sell_exchange"], "OKX")
            self.assertEqual(df.iloc[0]["buy_price"], 30000.0)
            self.assertEqual(df.iloc[0]["sell_price"], 30500.0)
            self.assertEqual(df.iloc[0]["network"], "Ethereum")
            self.assertEqual(df.iloc[0]["transfer_fee"], 0.01)
            self.assertEqual(df.iloc[0]["transfer_time"], "10 minutes")
            self.assertEqual(df.iloc[0]["spread"], 1.67)
            self.assertEqual(df.iloc[0]["buy_volume"], 100.0)
            self.assertEqual(df.iloc[0]["sell_volume"], 100.0)
            self.assertEqual(df.iloc[0]["scan_time"], "2024-07-24 12:00:00")

            log_info("Data in Excel file is correct")

        except Exception as e:
            log_error(f"Exception during test_export_to_excel: {e}")
            self.fail(f"Test failed due to exception: {e}")

        finally:
            # Удаление тестового файла
            if os.path.exists(test_filename):
                os.remove(test_filename)
                log_info(f"Test file removed: {test_filename}")

if __name__ == "__main__":
    unittest.main()
