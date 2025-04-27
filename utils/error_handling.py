# utils/error_handling.py

import logging
import traceback

# Настройка логирования для ошибок
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('error.log'),  # Логирование ошибок в отдельный файл
        logging.StreamHandler()  # Логирование ошибок в консоль
    ]
)

def handle_error(e):
    """
    Обрабатывает ошибки и возвращает сообщение об ошибке.
    
    :param e: Исключение
    :return: Словарь с сообщением об ошибке
    """
    error_message = str(e)  # Преобразуем исключение в строку для сообщения об ошибке
    stack_trace = traceback.format_exc()  # Получаем полную трассировку стека для отладки
    logging.error(f"An error occurred: {error_message}\n{stack_trace}")  # Логируем сообщение об ошибке и трассировку стека
    
    return {"error": error_message}  # Возвращаем сообщение об ошибке в виде словаря

def log_and_raise(exception):
    """
    Логирует исключение и перебрасывает его дальше.
    
    :param exception: Исключение для логирования и переброса.
    """
    logging.error(f"Exception occurred: {exception}")
    raise exception  # Перебрасываем исключение дальше

def handle_api_error(response):
    """
    Обрабатывает ошибки API запросов.
    
    :param response: Объект ответа запроса.
    :return: Данные ответа, если запрос был успешным.
    :raises Exception: Исключение с сообщением об ошибке, если запрос не успешен.
    """
    try:
        response.raise_for_status()  # Проверяем успешность запроса
        data = response.json()  # Получаем данные ответа в формате JSON
        if "error" in data:  # Проверяем наличие ошибок в данных ответа
            raise Exception(f"API Error: {data['error']}")
        return data  # Возвращаем данные ответа
    except Exception as e:
        handle_error(e)  # Обрабатываем ошибку
        raise

def handle_database_error(exception):
    """
    Обрабатывает ошибки базы данных.
    
    :param exception: Исключение, связанное с базой данных.
    """
    handle_error(exception)  # Обрабатываем ошибку базы данных
    raise exception  # Перебрасываем исключение дальше

def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """
    Глобальный обработчик необработанных исключений.
    
    :param exc_type: Тип исключения.
    :param exc_value: Значение исключения.
    :param exc_traceback: Трассировка стека исключения.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        logging.info("Application interrupted by user")
    else:
        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

# Установка глобального обработчика необработанных исключений
import sys
sys.excepthook = handle_uncaught_exception
