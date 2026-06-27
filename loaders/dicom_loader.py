import pydicom
import numpy as np
from PIL import Image
from .base_loader import BaseLoader
from models.app_state import AppState
from utils.image_processing import normalize_image

class DICOMLoader(BaseLoader):
    def can_load(self, file_path: str) -> bool:
        return file_path.lower().endswith('.dcm')

    def load(self, file_path: str, state: AppState) -> None:
        ds = pydicom.dcmread(file_path)
        pixel_array = ds.pixel_array
        # Нормализация
        normalized = normalize_image(pixel_array)
        # Приводим к 3 каналам (повторяем, если ч/б)
        if len(normalized.shape) == 2:
            normalized = np.stack([normalized]*3, axis=-1)
        img = Image.fromarray(normalized)

        # Метаданные
        metadata = {}
        for elem in ds:
            if elem.tag == 0x7FE00010:
                metadata[elem.name] = f"<Pixel Data: {len(elem.value)} bytes>"
            elif elem.VR == "SQ":
                metadata[elem.name] = f"<Sequence with {len(elem.value)} item(s)>"
            else:
                try:
                    metadata[elem.name] = str(elem.value).encode('iso8859-1').decode('cp1251')
                except:
                    metadata[elem.name] = str(elem.value)

        # Масштаб
        scale = None
        if hasattr(ds, 'ImagerPixelSpacing'):
            scale = ds.ImagerPixelSpacing[0]

        # Сохраняем в state
        state.original_image = img
        state.scale = scale
        state.image_path = file_path
        state.clear_history()
        # Сохраняем метаданные в отдельное поле (можно добавить в state)
        state.metadata = metadata  # добавим поле в AppState позже, но для простоты пока используем словарь
        # Временно сохраним как атрибут
        if not hasattr(state, 'metadata'):
            state.metadata = {}
        state.metadata = metadata