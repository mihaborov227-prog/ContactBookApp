import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import random

class ContactBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Книга контактов")
        self.root.geometry("550x500")
        self.root.resizable(False, False)

        self.contacts = []          # список контактов {id, name, phone, email}
        self.filtered_contacts = [] # для отображения после фильтрации

        # Загрузка данных из JSON при старте
        self.load_contacts()

        # Интерфейс
        self.create_widgets()

    def create_widgets(self):
        # Рамка для ввода
        input_frame = tk.LabelFrame(self.root, text="Новый контакт", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(input_frame, text="Имя *:").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(input_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(input_frame, text="Телефон *:").grid(row=1, column=0, sticky="w")
        self.phone_entry = tk.Entry(input_frame, width=30)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(input_frame, text="Email:").grid(row=2, column=0, sticky="w")
        self.email_entry = tk.Entry(input_frame, width=30)
        self.email_entry.grid(row=2, column=1, padx=5, pady=2)

        btn_add = tk.Button(input_frame, text="Добавить контакт", command=self.add_contact, bg="lightgreen")
        btn_add.grid(row=3, column=0, columnspan=2, pady=10)

        # Рамка для фильтрации
        filter_frame = tk.LabelFrame(self.root, text="Поиск", padx=10, pady=10)
        filter_frame.pack(pady=5, padx=10, fill="x")

        tk.Label(filter_frame, text="Имя содержит:").pack(side="left", padx=5)
        self.filter_entry = tk.Entry(filter_frame, width=20)
        self.filter_entry.pack(side="left", padx=5)
        btn_filter = tk.Button(filter_frame, text="Фильтровать", command=self.filter_contacts)
        btn_filter.pack(side="left", padx=5)
        btn_clear_filter = tk.Button(filter_frame, text="Сброс", command=self.clear_filter)
        btn_clear_filter.pack(side="left", padx=5)

        # Список контактов
        list_frame = tk.LabelFrame(self.root, text="Список контактов", padx=10, pady=10)
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        columns = ("ID", "Имя", "Телефон", "Email")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col=="ID" else 130)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Кнопка удаления
        btn_delete = tk.Button(self.root, text="Удалить выбранный контакт", command=self.delete_contact, bg="lightcoral")
        btn_delete.pack(pady=5)

        # Отображаем контакты
        self.refresh_display()

    # Валидация
    def validate_contact(self, name, phone, email):
        if not name.strip():
            messagebox.showerror("Ошибка", "Имя не может быть пустым")
            return False
        if not phone.strip():
            messagebox.showerror("Ошибка", "Телефон не может быть пустым")
            return False
        # Простейшая проверка телефона: только цифры, +, -, пробелы
        if not all(c.isdigit() or c in '+ -()' for c in phone):
            messagebox.showerror("Ошибка", "Телефон содержит недопустимые символы")
            return False
        if email.strip() and "@" not in email:
            messagebox.showerror("Ошибка", "Email должен содержать '@'")
            return False
        return True

    def add_contact(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()

        if not self.validate_contact(name, phone, email):
            return

        # Генерация уникального ID (случайное число + проверка)
        while True:
            new_id = random.randint(1000, 9999)
            if not any(c["id"] == new_id for c in self.contacts):
                break

        contact = {
            "id": new_id,
            "name": name.strip(),
            "phone": phone.strip(),
            "email": email.strip()
        }
        self.contacts.append(contact)
        self.save_contacts()
        self.clear_entries()
        self.refresh_display()
        messagebox.showinfo("Успех", "Контакт добавлен")

    def delete_contact(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите контакт для удаления")
            return
        # Получаем ID из выбранной строки
        item = self.tree.item(selected[0])
        contact_id = item['values'][0]
        # Удаляем из списка
        self.contacts = [c for c in self.contacts if c["id"] != contact_id]
        self.save_contacts()
        self.refresh_display()
        messagebox.showinfo("Успех", "Контакт удалён")

    def filter_contacts(self):
        search = self.filter_entry.get().strip().lower()
        if not search:
            self.clear_filter()
            return
        self.filtered_contacts = [c for c in self.contacts if search in c["name"].lower()]
        self.update_treeview(self.filtered_contacts)

    def clear_filter(self):
        self.filter_entry.delete(0, tk.END)
        self.filtered_contacts = []
        self.update_treeview(self.contacts)

    def update_treeview(self, contact_list):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for c in contact_list:
            self.tree.insert("", tk.END, values=(c["id"], c["name"], c["phone"], c["email"]))

    def refresh_display(self):
        # Обновляем отображение c учётом фильтра
        if self.filtered_contacts:
            self.update_treeview(self.filtered_contacts)
        else:
            self.update_treeview(self.contacts)

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)

    def load_contacts(self):
        if os.path.exists("contacts.json"):
            try:
                with open("contacts.json", "r", encoding="utf-8") as f:
                    self.contacts = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить контакты: {e}")
                self.contacts = []
        else:
            # Пример начальных данных (для теста)
            self.contacts = [
                {"id": 1001, "name": "Иван Петров", "phone": "+7 123 456-78-90", "email": "ivan@example.com"},
                {"id": 1002, "name": "Мария Сидорова", "phone": "89123456789", "email": "maria@example.com"}
            ]
            self.save_contacts()

    def save_contacts(self):
        try:
            with open("contacts.json", "w", encoding="utf-8") as f:
                json.dump(self.contacts, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить контакты: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactBookApp(root)
    root.mainloop()