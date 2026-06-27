import tkinter as tk
from tkinter import ttk
from models.app_state import AppState
from segmentation.tooth import apply_segmentation
from PIL import Image
import numpy as np

class Toolbar(ttk.Frame):
    def __init__(self, parent, state: AppState, canvas, statusbar):
        super().__init__(parent)
        self.state = state
        self.canvas = canvas
        self.statusbar = statusbar
        self._create_buttons()

    def _create_buttons(self):
        # Настраиваем растяжение колонок внутри toolbar
        for i in range(4):
            self.columnconfigure(i, weight=1)

        btn_rot = ttk.Button(self, text="Вращать", command=self.on_rotate)
        btn_rot.grid(row=0, column=0, pady=5, sticky="we", padx=2)

        btn_zoom = ttk.Button(self, text="Увеличить", command=self.on_toggle_zoom)
        btn_zoom.grid(row=0, column=1, pady=5, sticky="we", padx=2)

        btn_back = ttk.Button(self, text="Назад", command=self.on_undo)
        btn_back.grid(row=0, column=2, pady=5, sticky="we", padx=2)

        btn_measure = ttk.Button(self, text="Измерить расстояние", command=self.on_toggle_measure)
        btn_measure.grid(row=0, column=3, pady=5, sticky="we", padx=2)

        btn_seg = ttk.Button(self, text="Сегментация зуба", command=self.on_segmentation)
        btn_seg.grid(row=1, column=0, columnspan=4, pady=5, sticky="ew", padx=2)

    def on_rotate(self):
        if self.state.original_image is None:
            return
        self.state.push_history()
        rotated = np.rot90(np.array(self.state.original_image))
        self.state.original_image = Image.fromarray(rotated)
        self.canvas.refresh()
        self.statusbar.set_message("Поворот выполнен")

    def on_toggle_zoom(self):
        self.state.zoom_mode = not self.state.zoom_mode
        self.statusbar.set_message("Режим увеличения ВКЛ" if self.state.zoom_mode else "Режим увеличения ВЫКЛ")

    def on_toggle_measure(self):
        self.state.measuring_mode = not self.state.measuring_mode
        self.statusbar.set_message("Режим измерения ВКЛ" if self.state.measuring_mode else "Режим измерения ВЫКЛ")

    def on_undo(self):
        if self.state.pop_history():
            self.canvas.refresh()
            self.statusbar.set_message("Откат выполнен")
        else:
            self.statusbar.set_message("Нет действий для отката")

    def on_segmentation(self):
        self.statusbar.set_message("Функция сегментации появится в следующей версии")
        # if self.state.original_image is None:
        #     return
        # apply_segmentation(self.state)
        # self.canvas.refresh()
        # self.statusbar.set_message("Сегментация выполнена")