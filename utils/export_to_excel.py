import pandas as pd
import os
import logging

# Настройка логирования
log_filename = "export.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def log_info(message):
    logger.info(message)
    print(message)

def log_error(message):
    logger.error(message)
    print(message)

def load_scan_results(filename="scan_results.txt"):
    """
    Загружает результаты сканирования из текстового файла и преобразует их в список словарей.

    :param filename: Путь к файлу с результатами сканирования.
    :return: Список словарей с данными об арбитражных возможностях.
    """
    results = []
    try:
        if not os.path.exists(filename):
            log_info(f"Файл {filename} не найден.")
            return results

        with open(filename, 'r') as f:
            for line in f:
                result = eval(line.strip())
                results.append(result)

        log_info(f"Успешно загружены результаты из {filename}.")
    except Exception as e:
        log_error(f"Ошибка при загрузке результатов сканирования: {e}")
    
    return results

def export_to_excel(filename="arbitrage_opportunities.xlsx"):
    """
    Экспортирует арбитражные возможности из файла scan_results.txt в Excel.

    :param filename: Путь к файлу Excel.
    """
    try:
        # Загружаем данные из файла scan_results.txt
        opportunities = load_scan_results()
        if not opportunities:
            log_info("Нет данных для экспорта.")
            return

        # Преобразуем список словарей в DataFrame
        df = pd.DataFrame(opportunities)
        
        # Экспортируем данные в Excel файл
        df.to_excel(filename, index=False)  # Записываем в файл без индексов
        log_info(f"Данные успешно экспортированы в {filename}.")
    except Exception as e:
        log_error(f"Исключение произошло при экспорте в Excel: {e}")
        raise

# Пример использования функции
if __name__ == "__main__":
    export_to_excel("arbitrage_opportunities.xlsx")
