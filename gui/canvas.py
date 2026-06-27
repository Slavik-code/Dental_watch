import tkinter as tk
from PIL import Image, ImageTk
from models.app_state import AppState

class ImageCanvas(tk.Canvas):
    def __init__(self, parent, state: AppState, statusbar):
        super().__init__(parent, bg='black')
        self.state = state
        self.statusbar = statusbar
        self.bind("<ButtonPress-1>", self.on_button_press)
        self.bind("<B1-Motion>", self.on_mouse_drag)
        self.bind("<ButtonRelease-1>", self.on_button_release)
        self.bind("<Configure>", self.on_resize)

        # Для измерения и зума
        self.zoom_rect = None
        self.zoom_start = None
        self.measure_line = None
        self.measure_start = None

    def refresh(self):
        """Масштабирует и отображает текущее изображение."""
        if self.state.original_image is None:
            self.delete("all")
            return
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1 or h <= 1:
            return
        img = self.state.original_image
        ratio = min(w / img.width, h / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        if new_size[0] <= 0 or new_size[1] <= 0:
            return
        resized = img.resize(new_size, Image.LANCZOS)
        self.state.current_photo = ImageTk.PhotoImage(resized)
        self.delete("all")
        self.create_image(w//2, h//2, image=self.state.current_photo, anchor='center')

    def on_resize(self, event):
        self.refresh()

    def on_button_press(self, event):
        if self.state.zoom_mode:
            self.zoom_start = (event.x, event.y)
            self.zoom_rect = self.create_rectangle(
                event.x, event.y, event.x, event.y, outline='green'
            )
        elif self.state.measuring_mode:
            self.measure_start = (event.x, event.y)
            self.measure_line = self.create_line(
                event.x, event.y, event.x, event.y, fill='green', width=2
            )

    def on_mouse_drag(self, event):
        if self.state.zoom_mode and self.zoom_rect:
            self.coords(self.zoom_rect, self.zoom_start[0], self.zoom_start[1], event.x, event.y)
        elif self.state.measuring_mode and self.measure_line:
            self.coords(self.measure_line, self.measure_start[0], self.measure_start[1], event.x, event.y)

    def on_button_release(self, event):
        if self.state.zoom_mode:
            self._apply_zoom(event)
            self.state.zoom_mode = False
            self.statusbar.set_message("Режим увеличения выключен")
        elif self.state.measuring_mode:
            self._finish_measure(event)
            self.state.measuring_mode = False
            self.statusbar.set_message("Режим измерения выключен")

    def _apply_zoom(self, event):
        if self.state.original_image is None:
            return
        x0, y0 = self.zoom_start
        x1, y1 = event.x, event.y
        self.delete(self.zoom_rect)
        self.zoom_rect = None
        if abs(x1-x0) < 2 or abs(y1-y0) < 2:
            return

        # Координаты на исходном изображении
        img = self.state.original_image
        cw = self.winfo_width()
        ch = self.winfo_height()
        # Вычисляем смещение, так как изображение отцентрировано
        ratio = min(cw / img.width, ch / img.height)
        disp_w = int(img.width * ratio)
        disp_h = int(img.height * ratio)
        offset_x = (cw - disp_w) // 2
        offset_y = (ch - disp_h) // 2

        left = max(0, int((x0 - offset_x) / ratio))
        upper = max(0, int((y0 - offset_y) / ratio))
        right = min(img.width, int((x1 - offset_x) / ratio))
        lower = min(img.height, int((y1 - offset_y) / ratio))

        if right - left <= 1 or lower - upper <= 1:
            return

        # Сохраняем историю
        self.state.push_history()
        cropped = img.crop((left, upper, right, lower))
        self.state.original_image = cropped
        self.refresh()
        self.statusbar.set_message("Увеличение выполнено")

    def _finish_measure(self, event):
        if self.state.original_image is None:
            return
        x0, y0 = self.measure_start
        x1, y1 = event.x, event.y
        self.delete(self.measure_line)
        self.measure_line = None
        if abs(x1-x0) < 2 or abs(y1-y0) < 2:
            return

        img = self.state.original_image
        cw = self.winfo_width()
        ch = self.winfo_height()
        ratio = min(cw / img.width, ch / img.height)
        offset_x = (cw - int(img.width * ratio)) // 2
        offset_y = (ch - int(img.height * ratio)) // 2

        img_x0 = (x0 - offset_x) / ratio
        img_y0 = (y0 - offset_y) / ratio
        img_x1 = (x1 - offset_x) / ratio
        img_y1 = (y1 - offset_y) / ratio

        pixel_dist = ((img_x1 - img_x0)**2 + (img_y1 - img_y0)**2) ** 0.5
        if self.state.scale is not None:
            mm_dist = pixel_dist * self.state.scale
            msg = f"Расстояние: {mm_dist:.2f} мм"
        else:
            msg = f"Расстояние: {pixel_dist:.1f} пикселей"
        self.statusbar.set_message(msg)