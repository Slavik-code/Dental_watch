"""
Класс для хранения всего состояния приложения.
Вместо глобальных переменных используем один объект.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Any
from PIL import Image

@dataclass
class AppState:
    # Изображения
    current_photo: Optional[Any] = None      # PhotoImage для отображения на Canvas
    original_image: Optional[Image.Image] = None  # PIL Image (текущее)

    # Пути и метаданные
    image_path: Optional[str] = None
    description: Optional[str] = None
    save_path: Optional[str] = None

    # Масштаб DICOM (мм/пиксель)
    scale: Optional[float] = None

    # История для отката
    history: List[Image.Image] = field(default_factory=list)
    history_scales: List[float] = field(default_factory=list)

    # Режимы мыши
    zoom_mode: bool = False
    zoom_rect: Optional[int] = None
    zoom_start: Optional[Tuple[int, int]] = None

    measuring_mode: bool = False
    measure_line: Optional[int] = None
    measure_start: Optional[Tuple[int, int]] = None

    def push_history(self):
        """Сохраняет текущее изображение и масштаб перед изменением."""
        if self.original_image is not None:
            self.history.append(self.original_image.copy())
            if self.scale is not None:
                self.history_scales.append(self.scale)

    def pop_history(self) -> bool:
        """Восстанавливает последнее сохранённое состояние."""
        if self.history:
            self.original_image = self.history.pop()
            if self.history_scales:
                self.scale = self.history_scales.pop()
            return True
        return False

    def clear_history(self):
        self.history.clear()
        self.history_scales.clear()