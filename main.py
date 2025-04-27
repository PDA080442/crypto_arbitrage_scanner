import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from threading import Thread, Event
from scanner import scan_for_arbitrage
from utils.export_to_excel import export_to_excel
import logging
import atexit

# Инициализация логирования
log_filename = "scanner.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Список доступных бирж
EXCHANGES = [
    "Пустое поле",
    "HTX",
    "OKX",
    "Gate.io",
    "Bitget",
    "MEXC",
    "Kucoin",
    "CoinEX",
    "Poloniex"
]

# Флаг для остановки сканирования
stop_scan_flag = Event()
results_list = []

def validate_inputs():
    """
    Валидирует вводимые данные.
    """
    buy_ex = buy_exchange_var.get()
    sell_ex = sell_exchange_var.get()
    min_sp = min_spread_entry.get()
    min_vol = min_volume_entry.get()

    if buy_ex == "Пустое поле":
        buy_ex = ""
    if sell_ex == "Пустое поле":
        sell_ex = ""

    try:
        min_sp = float(min_sp) if min_sp else 0.0
        min_vol = float(min_vol) if min_vol else 0.0
    except ValueError:
        logger.error("Неверный числовой ввод спреда или объема.")
        messagebox.showerror("Ошибка", "Пожалуйста, введите допустимые числовые значения.")
        return None, None, None, None, False

    return buy_ex, sell_ex, min_sp, min_vol, True

def start_scan_thread():
    """
    Запускает сканирование в отдельном потоке.
    """
    def run_scan():
        stop_scan_flag.clear()
        buy_ex, sell_ex, min_sp, min_vol, valid = validate_inputs()
        if not valid:
            return

        logger.info(f"Запускаем сканирование: Биржа покупки={buy_ex}, Биржа продажи={sell_ex}, Минимальный спред={min_sp}, Минимальный объем={min_vol}")
        try:
            results_text.config(state=tk.NORMAL)
            results_text.delete(1.0, tk.END)
            results_text.insert(tk.END, "Сканирование...\n")
            results_text.config(state=tk.DISABLED)
            result = scan_for_arbitrage(buy_ex, sell_ex, min_sp, min_vol, stop_scan_flag)

            global results_list
            results_list = result

            if result:
                results_text.config(state=tk.NORMAL)
                results_text.insert(tk.END, "Найдены возможности для арбитража.\n")
                for opportunity in result:
                    results_text.insert(tk.END, f"{opportunity}\n")
                results_text.config(state=tk.DISABLED)

                export_options()
            else:
                results_text.config(state=tk.NORMAL)
                results_text.insert(tk.END, "Не найдено возможностей для арбитража.\n")
                results_text.config(state=tk.DISABLED)
                logger.info("Не найдены возможности для арбитража")
                messagebox.showwarning("Предупреждение", "Не найдено возможностей для арбитража.")
        except Exception as e:
            logger.error(f"Ошибка во время сканирования: {e}")
            root.after(0, lambda: messagebox.showerror("Ошибка", f"Произошла ошибка во время сканирования: {e}"))

    Thread(target=run_scan).start()

def stop_scan():
    """
    Останавливает процесс сканирования.
    """
    stop_scan_flag.set()
    logger.info("Сканирование остановлено пользователем")

def save_results_to_file():
    """
    Сохраняет результаты сканирования в текстовый файл.
    """
    with open("scan_results.txt", "w") as f:
        for result in results_list:
            f.write(f"{result}\n")
    logger.info("Результаты сканирования сохранены в scan_results.txt")

# Регистрация функции для вызова при завершении программы
atexit.register(save_results_to_file)

def custom_log_info(message):
    """
    Логирует информационные сообщения и выводит их в текстовое поле.
    
    :param message: Сообщение для логирования
    """
    logger.info(message)
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, f"INFO: {message}\n")
    log_text.config(state=tk.DISABLED)

def custom_log_error(message):
    """
    Логирует сообщения об ошибках и выводит их в текстовое поле.
    
    :param message: Сообщение для логирования
    """
    logger.error(message)
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, f"Ошибка: {message}\n")
    log_text.config(state=tk.DISABLED)

# Перенаправление логов в текстовое поле
logging.getLogger().handlers = [logging.StreamHandler()]

def update_results(results):
    """
    Обновляет результаты в текстовом виджете.
    
    :param results: Результаты сканирования
    """
    results_text.config(state=tk.NORMAL)
    results_text.delete(1.0, tk.END)
    if "error" in results:
        results_text.insert(tk.END, f"Ошибка: {results['error']}\n")
    else:
        for result in results:
            results_text.insert(tk.END, f"{result}\n")
    results_text.config(state=tk.DISABLED)

def start_scan():
    """
    Обработчик для кнопки запуска сканирования.
    """
    start_scan_thread()

def export_results():
    """
    Экспортирует результаты в Excel файл.
    """
    filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel файлы", "*.xlsx")])
    if filename:
        try:
            export_to_excel(filename)
            messagebox.showinfo("Экспорт", "Данные успешно экспортированы.")
        except Exception as e:
            custom_log_error(f"Произошла ошибка во время экспорта: {e}")
            messagebox.showerror("Ошибка экспорта", f"Произошла ошибка во время экспорта: {e}")

def export_results_to_text():
    """
    Экспортирует результаты в текстовый файл.
    """
    filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text файлы", "*.txt")])
    if filename:
        try:
            with open(filename, 'w') as f:
                for result in results_list:
                    f.write(f"{result}\n")
            messagebox.showinfo("Экспорт", "Данные успешно экспортированы в текстовый файл.")
        except Exception as e:
            custom_log_error(f"Произошла ошибка во время экспорта в текст: {e}")
            messagebox.showerror("Ошибка экспорта", f"Произошла ошибка во время экспорта в текст: {e}")

def export_options():
    """
    Выводит окно с вариантами экспорта.
    """
    export_window = tk.Toplevel(root)
    export_window.title("Экспорт данных")
    export_window.geometry("300x150")

    ttk.Label(export_window, text="Выберите формат экспорта:").pack(pady=10)

    ttk.Button(export_window, text="Экспорт в Excel", command=lambda: [export_results(), export_window.destroy()]).pack(pady=5)
    ttk.Button(export_window, text="Экспорт в текст", command=lambda: [export_results_to_text(), export_window.destroy()]).pack(pady=5)

# Создание основного окна
root = tk.Tk()
root.title("Сканер Арбитража Криптовалют")
root.geometry("800x600")

# Интерфейс с использованием ttk
style = ttk.Style()
style.configure('TLabel', font=('Arial', 12))
style.configure('TButton', font=('Arial', 12))

main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Поле выбора биржи покупки
ttk.Label(main_frame, text="Биржа покупки").grid(row=0, column=0, padx=10, pady=10, sticky='e')
buy_exchange_var = tk.StringVar()
buy_exchange_combobox = ttk.Combobox(main_frame, textvariable=buy_exchange_var, values=EXCHANGES, state='readonly')
buy_exchange_combobox.grid(row=0, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))
buy_exchange_combobox.set("Пустое поле")

# Поле выбора биржи продажи
ttk.Label(main_frame, text="Биржа продажи").grid(row=1, column=0, padx=10, pady=10, sticky='e')
sell_exchange_var = tk.StringVar()
sell_exchange_combobox = ttk.Combobox(main_frame, textvariable=sell_exchange_var, values=EXCHANGES, state='readonly')
sell_exchange_combobox.grid(row=1, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))
sell_exchange_combobox.set("Пустое поле")

# Поле ввода минимального спреда
ttk.Label(main_frame, text="Минимальный спред (%)").grid(row=2, column=0, padx=10, pady=10, sticky='e')
min_spread_entry = ttk.Entry(main_frame)
min_spread_entry.grid(row=2, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

# Поле ввода минимального объема
ttk.Label(main_frame, text="Минимальный объем").grid(row=3, column=0, padx=10, pady=10, sticky='e')
min_volume_entry = ttk.Entry(main_frame)
min_volume_entry.grid(row=3, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

# Кнопка запуска сканирования
ttk.Button(main_frame, text="Начать сканирование", command=start_scan).grid(row=6, column=0, columnspan=2, pady=20)

# Кнопка остановки сканирования
ttk.Button(main_frame, text="Остановить сканирование", command=stop_scan).grid(row=7, column=0, columnspan=2, pady=10)

# Виджет для отображения результатов
results_text = tk.Text(main_frame, height=10, width=80, font=('Arial', 10), state=tk.DISABLED)
results_text.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky=(tk.W, tk.E))

# Виджет для отображения логов
log_text = tk.Text(main_frame, height=10, width=80, font=('Arial', 10), state=tk.DISABLED)
log_text.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky=(tk.W, tk.E))

# Кнопка экспорта данных
ttk.Button(main_frame, text="Экспорт в Excel", command=export_results).grid(row=10, column=0, columnspan=2, pady=10)

# Кнопка экспорта данных в текстовый файл
ttk.Button(main_frame, text="Экспорт в текст", command=export_results_to_text).grid(row=11, column=0, columnspan=2, pady=10)

# Настройка адаптивного интерфейса
for child in main_frame.winfo_children():
    child.grid_configure(padx=5, pady=5)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(8, weight=1)
main_frame.rowconfigure(9, weight=1)

# Запуск основного цикла
root.mainloop()
