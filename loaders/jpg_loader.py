from PIL import Image
from .base_loader import BaseLoader
from models.app_state import AppState

class JPGLoader(BaseLoader):
    def can_load(self, file_path: str) -> bool:
        ext = file_path.lower()
        return ext.endswith('.jpg') or ext.endswith('.jpeg') or ext.endswith('.png')

    def load(self, file_path: str, state: AppState) -> None:
        img = Image.open(file_path)
        # Приводим к RGB (для единообразия)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        state.original_image = img
        state.scale = None          # для обычных изображений масштаб не нужен
        state.image_path = file_path
        state.clear_history()
        state.metadata = {
            'format': img.format,
            'size': img.size,
            'mode': img.mode,
            'type': 'jpg/png'
        }