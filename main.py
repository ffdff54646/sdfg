import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Дневник погоды")
        self.root.geometry("800x600")
        
        # Данные
        self.entries = []          # Все записи
        self.filtered_entries = [] # Отфильтрованные записи
        
        # Создание интерфейса
        self.create_input_frame()
        self.create_table()
        self.create_filter_frame()
        self.create_action_buttons()
        
        # Загрузка последнего файла, если существует
        self.data_file = Path("weather_diary.json")
        if self.data_file.exists():
            self.load_from_file(self.data_file)
            self.refresh_table()
    
    def create_input_frame(self):
        """Поля для ввода новой записи"""
        input_frame = ttk.LabelFrame(self.root, text="Новая запись", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=2)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Температура
        ttk.Label(input_frame, text="Температура (°C):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # Описание погоды
        ttk.Label(input_frame, text="Описание:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.desc_entry = ttk.Entry(input_frame, width=30)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=2)
        
        # Осадки (да/нет)
        ttk.Label(input_frame, text="Осадки:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.precip_var = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Да", variable=self.precip_var).grid(row=3, column=1, sticky=tk.W, padx=5)
        
        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить запись", command=self.add_entry).grid(row=4, column=0, columnspan=2, pady=10)
    
    def create_table(self):
        """Таблица для отображения записей"""
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")
        
        self.tree.column("date", width=100)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=300)
        self.tree.column("precipitation", width=80)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_filter_frame(self):
        """Панель фильтрации"""
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=2)
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(filter_frame, text="Фильтр по дате", command=self.filter_by_date).grid(row=0, column=2, padx=5)
        
        # Фильтр по температуре (выше порога)
        ttk.Label(filter_frame, text="Температура выше (°C):").grid(row=1, column=0, padx=5, pady=2)
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(filter_frame, text="Фильтр по температуре", command=self.filter_by_temperature).grid(row=1, column=2, padx=5)
        
        # Кнопка сброса фильтра
        ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter).grid(row=2, column=0, columnspan=3, pady=5)
    
    def create_action_buttons(self):
        """Кнопки сохранения и загрузки"""
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(action_frame, text="Сохранить в JSON", command=self.save_to_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Загрузить из JSON", command=self.load_from_json).pack(side=tk.LEFT, padx=5)
    
    def validate_date(self, date_str):
        """Проверка формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_temperature(self, temp_str):
        """Проверка, что температура - число"""
        try:
            float(temp_str)
            return True
        except ValueError:
            return False
    
    def add_entry(self):
        """Добавление новой записи"""
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precip = self.precip_var.get()
        
        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        if not self.validate_temperature(temp):
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        if not desc:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return
        
        # Создание записи
        entry = {
            "date": date,
            "temperature": float(temp),
            "description": desc,
            "precipitation": "Да" if precip else "Нет"
        }
        
        self.entries.append(entry)
        self.reset_filter()  # Обновляем отображение (сбрасываем фильтр)
        
        # Очистка полей
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)
        
        messagebox.showinfo("Успех", "Запись добавлена")
    
    def refresh_table(self, entries_to_show=None):
        """Обновление таблицы"""
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        if entries_to_show is None:
            entries_to_show = self.filtered_entries if self.filtered_entries else self.entries
        
        for entry in entries_to_show:
            self.tree.insert("", tk.END, values=(
                entry["date"],
                entry["temperature"],
                entry["description"],
                entry["precipitation"]
            ))
    
    def filter_by_date(self):
        """Фильтрация по точной дате"""
        date_filter = self.filter_date_entry.get().strip()
        if not date_filter:
            messagebox.showwarning("Предупреждение", "Введите дату для фильтрации")
            return
        if not self.validate_date(date_filter):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        
        self.filtered_entries = [e for e in self.entries if e["date"] == date_filter]
        self.refresh_table(self.filtered_entries)
        if not self.filtered_entries:
            messagebox.showinfo("Результат", "Записей с такой датой не найдено")
    
    def filter_by_temperature(self):
        """Фильтрация по температуре (выше заданного порога)"""
        temp_str = self.filter_temp_entry.get().strip()
        if not temp_str:
            messagebox.showwarning("Предупреждение", "Введите порог температуры")
            return
        if not self.validate_temperature(temp_str):
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        
        threshold = float(temp_str)
        self.filtered_entries = [e for e in self.entries if e["temperature"] > threshold]
        self.refresh_table(self.filtered_entries)
        if not self.filtered_entries:
            messagebox.showinfo("Результат", f"Записей с температурой выше {threshold}°C не найдено")
    
    def reset_filter(self):
        """Сброс фильтрации"""
        self.filtered_entries = []
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.refresh_table(self.entries)
    
    def save_to_json(self):
        """Сохранение всех записей в JSON файл"""
        try:
            filename = "weather_diary.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
    
    def load_from_json(self, filename=None):
        """Загрузка записей из JSON файла"""
        if filename is None:
            filename = "weather_diary.json"
        try:
            with open(filename, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, list):
                self.entries = loaded
                self.reset_filter()
                messagebox.showinfo("Успех", f"Загружено {len(self.entries)} записей")
            else:
                messagebox.showerror("Ошибка", "Неверный формат файла")
        except FileNotFoundError:
            messagebox.showerror("Ошибка", f"Файл {filename} не найден")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
    
    def load_from_file(self, filepath):
        """Внутренний метод для загрузки при старте"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                self.entries = json.load(f)
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
