import zipfile
from io import BytesIO
import pydicom
import numpy as np
from PIL import Image
from .base_loader import BaseLoader
from models.app_state import AppState
from utils.image_processing import normalize_image

class ZipDICOMLoader(BaseLoader):
    def can_load(self, file_path: str) -> bool:
        return file_path.lower().endswith('.zip')

    def load(self, file_path: str, state: AppState) -> None:
        with zipfile.ZipFile(file_path, 'r') as zp:
            # Ищем первый .dcm файл в архиве (упрощённо)
            dcm_files = [f for f in zp.namelist() if f.lower().endswith('.dcm')]
            if not dcm_files:
                raise ValueError("В ZIP-архиве нет DICOM-файлов")
            # Берём первый
            with zp.open(dcm_files[0]) as f:
                dicom_bytes = f.read()
            ds = pydicom.dcmread(BytesIO(dicom_bytes))

        # Теперь обрабатываем как DICOM
        pixel_array = ds.pixel_array
        normalized = normalize_image(pixel_array)
        if len(normalized.shape) == 2:
            normalized = np.stack([normalized]*3, axis=-1)
        img = Image.fromarray(normalized)

        # Метаданные (аналогично DICOMLoader)
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

        scale = None
        if hasattr(ds, 'ImagerPixelSpacing'):
            scale = ds.ImagerPixelSpacing[0]

        state.original_image = img
        state.scale = scale
        state.image_path = file_path
        state.clear_history()
        state.metadata = metadata