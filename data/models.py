import os
import sys
import uuid
from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func

# Добавим текущий путь в sys.path, чтобы модули могли быть найдены
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_logger, log_info, log_error

# Настройка логирования
setup_logger()

# Создание базового класса для моделей
Base = declarative_base()

class ArbitrageOpportunity(Base):
    """
    Модель для хранения арбитражных возможностей в базе данных.
    """
    __tablename__ = 'arbitrage_opportunity'
    
    # Уникальный идентификатор, используем UUID
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Криптовалютная пара (например, ETH/USD)
    pair = Column(String, nullable=False)
    
    # Биржа покупки
    buy_exchange = Column(String, nullable=False)
    
    # Биржа продажи
    sell_exchange = Column(String, nullable=False)
    
    # Цена покупки
    buy_price = Column(Float, nullable=False)
    
    # Цена продажи
    sell_price = Column(Float, nullable=False)
    
    # Сеть (например, Ethereum)
    network = Column(String, nullable=False)
    
    # Комиссия за перевод
    transfer_fee = Column(Float, nullable=False)
    
    # Время перевода
    transfer_time = Column(String, nullable=False)
    
    # Спред
    spread = Column(Float, nullable=False)
    
    # Объем покупки
    buy_volume = Column(Float, nullable=False)
    
    # Объем продажи
    sell_volume = Column(Float, nullable=False)
    
    # Время сканирования, автоматически заполняется текущим временем
    scan_time = Column(DateTime, server_default=func.now(), nullable=False)

# Настройка подключения к базе данных
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///your_database.db')  # Использование переменной окружения для URL базы данных

def initialize_database():
    """
    Инициализация базы данных и создание таблиц.
    """
    try:
        # Создание движка базы данных
        engine = create_engine(DATABASE_URL, echo=True)  # echo=True для отладки, можно убрать в продакшене
        log_info(f"Database engine created with URL: {DATABASE_URL}")

        # Создание сессии
        Session = sessionmaker(bind=engine)
        session = Session()
        log_info("Database session created")

        # Создание всех таблиц
        Base.metadata.create_all(engine)
        log_info("All tables created successfully.")
        
        return session
    except Exception as e:
        log_error(f"Error creating tables: {e}")
        raise  # Перебрасываем исключение дальше для критических ошибок

# Создание сессии для использования в других модулях
session = initialize_database()
