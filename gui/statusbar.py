import tkinter as tk
from tkinter import ttk

class StatusBar(ttk.Frame):
    """
    Многострочный статус-бар. Отображает последние N сообщений.
    """
    def __init__(self, parent, max_lines=5, height=4, **kwargs):
        super().__init__(parent, **kwargs)
        self.max_lines = max_lines
        self.messages = []  # храним последние сообщения

        # Создаём текстовое поле для вывода
        self.text = tk.Text(
            self,
            height=height,
            wrap=tk.WORD,
            relief=tk.SUNKEN,
            bd=1,
            bg='#f0f0f0',
            font=('TkDefaultFont', 9),
            state=tk.DISABLED,
            takefocus=0
        )
        self.text.pack(fill=tk.BOTH, expand=True)

        # Начальное сообщение
        self.set_message("Готово")

    def set_message(self, msg: str):
        """
        Добавляет новое сообщение в статус-бар.
        Если строк больше max_lines, удаляет самую старую.
        """
        # Добавляем в список
        self.messages.append(msg)
        # Оставляем только последние max_lines
        if len(self.messages) > self.max_lines:
            self.messages = self.messages[-self.max_lines:]

        # Обновляем отображение
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        # Вставляем сообщения, разделяя переводом строки
        full_text = "\n".join(self.messages)
        self.text.insert(tk.END, full_text)
        self.text.config(state=tk.DISABLED)
        # Прокручиваем вниз, чтобы видеть последнее сообщение
        self.text.see(tk.END)

    def clear(self):
        """Очищает все сообщения."""
        self.messages = []
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)

    def set_error(self, msg: str):
        """Удобный метод для вывода ошибки с пометкой."""
        self.set_message(f"Ошибка: {msg}")