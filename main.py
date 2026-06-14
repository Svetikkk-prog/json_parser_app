# добавлено: улучшенная обработка ошибок

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json

class JSONParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сервис парсинга JSON")
        self.root.geometry("900x650")
        self.api_url = "http://localhost:5000"
        self.setup_ui()

    def setup_ui(self):
        # Основной фрейм с отступами
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Заголовок
        title_label = ttk.Label(main_frame, text="Управление товарами", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))

        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        ttk.Button(button_frame, text="Загрузить JSON", command=self.load_json_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить список", command=self.refresh_list).pack(side=tk.LEFT, padx=5)

        # Таблица для списка элементов
        list_frame = ttk.LabelFrame(main_frame, text="Список элементов", padding="5")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        columns = ('ID', 'Name', 'Description', 'Price')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col == 'ID' else 150 if col == 'Price' else 250)

        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Форма для редактирования
        form_frame = ttk.LabelFrame(main_frame, text="Форма элемента", padding="10")
        form_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)

        # Переменные для полей
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.price_var = tk.DoubleVar()

        # Поле ID (только чтение)
        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        id_entry = ttk.Entry(form_frame, textvariable=self.id_var, state='readonly', width=10)
        id_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        # Поле Name
        ttk.Label(form_frame, text="Название:*").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=40)
        name_entry.grid(row=1, column=1, columnspan=3, sticky=tk.W, padx=5, pady=2)

        # Поле Description
        ttk.Label(form_frame, text="Описание:*").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        desc_entry = ttk.Entry(form_frame, textvariable=self.desc_var, width=40)
        desc_entry.grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=5, pady=2)

        # Поле Price
        ttk.Label(form_frame, text="Цена:*").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        price_entry = ttk.Entry(form_frame, textvariable=self.price_var, width=15)
        price_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

        # Кнопки формы
        form_button_frame = ttk.Frame(form_frame)
        form_button_frame.grid(row=4, column=0, columnspan=4, pady=10)
        self.add_button = ttk.Button(form_button_frame, text="Добавить", command=self.create_item)
        self.add_button.pack(side=tk.LEFT, padx=5)
        self.update_button = ttk.Button(form_button_frame, text="Обновить", command=self.update_item, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=5)
        self.delete_button = ttk.Button(form_button_frame, text="Удалить", command=self.delete_item, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        self.clear_button = ttk.Button(form_button_frame, text="Очистить", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Привязка выбора строки
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Загрузка начальных данных
        self.refresh_list()

        # Настройка растягивания
        form_frame.columnconfigure(1, weight=1)

    def load_json_file(self):
        """Загрузка внешнего JSON-файла и копирование в data.json."""
        file_path = filedialog.askopenfilename(
            title="Выберите JSON-файл",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Базовая проверка структуры
                if not isinstance(data, list):
                    raise ValueError("Файл должен содержать массив товаров")
                with open('data.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Успех", "JSON-файл успешно загружен!")
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def refresh_list(self):
        """Обновить таблицу из API."""
        try:
            response = requests.get(f"{self.api_url}/items", timeout=3)
            if response.status_code == 200:
                items = response.json()
                # Очистить таблицу
                for item in self.tree.get_children():
                    self.tree.delete(item)
                # Добавить элементы
                for item in items:
                    self.tree.insert('', tk.END, values=(
                        item['id'],
                        item['name'],
                        item['description'],
                        f"{item['price']:.2f}"
                    ))
            else:
                messagebox.showerror("Ошибка API", f"Не удалось получить данные. Код: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка соединения", f"Не удалось подключиться к API:\n{str(e)}\n\nЗапустите api_service.py")

    def clear_form(self):
        """Очистить поля ввода и отключить кнопки Update/Delete."""
        self.id_var.set("")
        self.name_var.set("")
        self.desc_var.set("")
        self.price_var.set(0.0)
        self.update_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)

    def on_tree_select(self, event):
        """Заполнить форму при выборе строки в таблице."""
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            if values:
                self.id_var.set(str(values[0]))
                self.name_var.set(values[1])
                self.desc_var.set(values[2])
                # Удаляем возможный символ валюты, просто число
                price_str = values[3].replace(',', '.')
                try:
                    self.price_var.set(float(price_str))
                except:
                    self.price_var.set(0.0)
                self.update_button.config(state=tk.NORMAL)
                self.delete_button.config(state=tk.NORMAL)

    def validate_inputs(self):
        """Проверить поля формы."""
        if not self.name_var.get().strip():
            messagebox.showerror("Ошибка", "Название товара не может быть пустым.")
            return False
        if not self.desc_var.get().strip():
            messagebox.showerror("Ошибка", "Описание товара не может быть пустым.")
            return False
        try:
            price = float(self.price_var.get())
            if price < 0:
                messagebox.showerror("Ошибка", "Цена не может быть отрицательной.")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом.")
            return False
        return True

    def create_item(self):
        """Добавить новый товар."""
        if not self.validate_inputs():
            return
        new_item = {
            'name': self.name_var.get().strip(),
            'description': self.desc_var.get().strip(),
            'price': float(self.price_var.get())
        }
        try:
            response = requests.post(f"{self.api_url}/items", json=new_item, timeout=3)
            if response.status_code == 201:
                messagebox.showinfo("Успех", "Товар добавлен.")
                self.clear_form()
                self.refresh_list()
            else:
                error = response.json().get('error', 'Неизвестная ошибка')
                messagebox.showerror("Ошибка API", f"Не удалось добавить: {error}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Нет соединения с API:\n{str(e)}")

    def update_item(self):
        """Обновить существующий товар."""
        if not self.validate_inputs():
            return
        try:
            item_id = int(self.id_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "ID товара не определён. Выберите товар из таблицы.")
            return
        updated_item = {
            'name': self.name_var.get().strip(),
            'description': self.desc_var.get().strip(),
            'price': float(self.price_var.get())
        }
        try:
            response = requests.put(f"{self.api_url}/items/{item_id}", json=updated_item, timeout=3)
            if response.status_code == 200:
                messagebox.showinfo("Успех", "Товар обновлён.")
                self.clear_form()
                self.refresh_list()
            elif response.status_code == 404:
                messagebox.showwarning("Не найдено", f"Товар с id={item_id} не существует.")
                self.refresh_list()
            else:
                error = response.json().get('error', 'Неизвестная ошибка')
                messagebox.showerror("Ошибка API", f"Не удалось обновить: {error}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Нет соединения с API:\n{str(e)}")

    def delete_item(self):
        """Удалить товар."""
        item_id_str = self.id_var.get()
        if not item_id_str:
            messagebox.showwarning("Нет выбора", "Выберите товар для удаления.")
            return
        item_id = int(item_id_str)
        confirm = messagebox.askyesno("Подтверждение", f"Удалить товар с id={item_id}?")
        if not confirm:
            return
        try:
            response = requests.delete(f"{self.api_url}/items/{item_id}", timeout=3)
            if response.status_code == 204:
                messagebox.showinfo("Успех", "Товар удалён.")
                self.clear_form()
                self.refresh_list()
            elif response.status_code == 404:
                messagebox.showwarning("Не найдено", f"Товар с id={item_id} уже удалён или не существует.")
                self.refresh_list()
            else:
                error = response.json().get('error', 'Неизвестная ошибка')
                messagebox.showerror("Ошибка API", f"Не удалось удалить: {error}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Нет соединения с API:\n{str(e)}")

def main():
    root = tk.Tk()
    app = JSONParserApp(root)
    root.mainloop()

if __name__ == "__main__":main()