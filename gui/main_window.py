import os
import tkinter as tk
from tkinter import ttk, filedialog, Menu, messagebox
from models.app_state import AppState
from loaders import LoaderFactory
from gui.canvas import ImageCanvas
from gui.toolbar import Toolbar
from gui.statusbar import StatusBar

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Анализатор стоматологических снимков")
        self.root.state('zoomed')

        self.state = AppState()
        # Добавляем поле metadata (если его нет в AppState)
        self.state.metadata = {}

        self._create_widgets()
        self._create_menu()

    def _create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Canvas (левая часть)
        canvas_frame = ttk.LabelFrame(main_frame, text="Просмотр снимка", padding="5")
        canvas_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        self.statusbar = StatusBar(self.root, max_lines=5, height=4)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas = ImageCanvas(canvas_frame, self.state, self.statusbar)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Правая панель управления
        control_frame = ttk.LabelFrame(main_frame, text="Управление", padding="10")
        control_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        control_frame.columnconfigure(0, weight=1)   # чтобы дочерние элементы растягивались
        control_frame.rowconfigure(0, weight=0)      # toolbar не растягивается по вертикали
        control_frame.rowconfigure(1, weight=1)      # описание занимает оставшееся место
        control_frame.rowconfigure(2, weight=1)      # метаданные занимают оставшееся место

        # 1. Панель инструментов (кнопки) – теперь используем grid
        self.toolbar = Toolbar(control_frame, self.state, self.canvas, self.statusbar)
        self.toolbar.grid(row=0, column=0, sticky="we", padx=5, pady=5)   # растягиваем по ширине

        # 2. Панель описания
        desc_frame = ttk.LabelFrame(control_frame, text="Описание снимка", padding="5")
        desc_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        desc_frame.columnconfigure(0, weight=1)
        desc_frame.rowconfigure(0, weight=1)

        self.desc_text = tk.Text(desc_frame, wrap=tk.WORD, height=8)
        self.desc_text.grid(row=0, column=0, sticky="nsew")
        desc_scroll = ttk.Scrollbar(desc_frame, command=self.desc_text.yview)
        desc_scroll.grid(row=0, column=1, sticky="ns")
        self.desc_text.config(yscrollcommand=desc_scroll.set)
        self.desc_text.insert(tk.END, "Описание появится здесь после генерации...")
        self.desc_text.config(state=tk.DISABLED)

        # 3. Панель метаданных
        meta_frame = ttk.LabelFrame(control_frame, text="Метаданные снимка", padding="5")
        meta_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        meta_frame.columnconfigure(0, weight=1)
        meta_frame.rowconfigure(0, weight=1)

        self.meta_text = tk.Text(meta_frame, wrap=tk.WORD, height=10)
        self.meta_text.grid(row=0, column=0, sticky="nsew")
        meta_scroll = ttk.Scrollbar(meta_frame, command=self.meta_text.yview)
        meta_scroll.grid(row=0, column=1, sticky="ns")
        self.meta_text.config(yscrollcommand=meta_scroll.set)
        self.meta_text.insert(tk.END, "Метаданные появятся здесь после загрузки...")
        self.meta_text.config(state=tk.DISABLED)

    def _create_menu(self):
        menubar = Menu(self.root)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label='Открыть...', command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label='Сохранить характеристику', command=self.save_file)
        file_menu.add_command(label='Сохранить характеристику как...', command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label='Выход', command=self.root.quit)
        menubar.add_cascade(label='Файл', menu=file_menu)
        self.root.config(menu=menubar)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Открыть файл",
            filetypes=[("Все поддерживаемые", "*.dcm *.zip *.jpg *.jpeg *.png"),
                       ("DICOM", "*.dcm"),
                       ("ZIP архив", "*.zip"),
                       ("Изображения", "*.jpg *.jpeg *.png")]
        )
        if not file_path:
            return

        loader = LoaderFactory.get_loader(file_path)
        if loader is None:
            self.statusbar.set_error("Неподдерживаемый формат файла")
            return

        try:
            loader.load(file_path, self.state)
            self.canvas.refresh()
            self.update_metadata_display()
            self.statusbar.set_message(f"Загружено: {os.path.basename(file_path)}")
        except Exception as e:
            self.statusbar.set_error(str(e))
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")

    def update_metadata_display(self):
        self.meta_text.config(state=tk.NORMAL)
        self.meta_text.delete(1.0, tk.END)
        if hasattr(self.state, 'metadata') and self.state.metadata:
            for key, value in self.state.metadata.items():
                self.meta_text.insert(tk.END, f"{key}: {value}\n")
        else:
            self.meta_text.insert(tk.END, "Метаданные не найдены")
        self.meta_text.config(state=tk.DISABLED)

    def save_file(self):
        self.statusbar.set_message("Функция сохранения будет реализована позже")

    def save_file_as(self):
        self.statusbar.set_message("Функция сохранения будет реализована позже")

    def run(self):
        self.root.mainloop()