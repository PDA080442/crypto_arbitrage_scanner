# utils/logger.py

import logging

def setup_logger(log_file='app.log', log_level=logging.INFO, console_log_level=logging.WARNING, log_format=None):
    """
    Настраивает логирование для приложения.
    
    :param log_file: Имя файла для логирования
    :param log_level: Уровень логирования для файла
    :param console_log_level: Уровень логирования для консоли
    :param log_format: Формат сообщения для логирования
    """
    if log_format is None:
        log_format = '%(asctime)s - %(levelname)s - %(message)s'  # Формат по умолчанию
    
    # Настройка обработчика для логирования в файл
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Настройка обработчика для логирования в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # Настройка основного логгера
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Установим уровень логирования для основного логгера на DEBUG
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("Настройка регистратора завершена.")

def log_info(message):
    """
    Логирует информационные сообщения.
    
    :param message: Сообщение для логирования
    """
    logging.info(message)

def log_error(message):
    """
    Логирует сообщения об ошибках.
    
    :param message: Сообщение об ошибке для логирования
    """
    logging.error(message)

def log_warning(message):
    """
    Логирует предупреждающие сообщения.
    
    :param message: Сообщение для логирования
    """
    logging.warning(message)

def log_debug(message):
    """
    Логирует отладочные сообщения.
    
    :param message: Сообщение для логирования
    """
    logging.debug(message)

# Пример использования функций логирования
if __name__ == "__main__":
    setup_logger(log_file='app.log', log_level=logging.INFO, console_log_level=logging.DEBUG)
    
    log_info("Это информационное сообщение.")
    log_error("Это сообщение об ошибке.")
    log_warning("Это предупреждающее сообщение.")
    log_debug("Это отладочное сообщение.")
