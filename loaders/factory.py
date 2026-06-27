from .dicom_loader import DICOMLoader
from .zip_loader import ZipDICOMLoader
from .jpg_loader import JPGLoader

class LoaderFactory:
    _loaders = [DICOMLoader(), ZipDICOMLoader(), JPGLoader()]  # можно добавить JPG/PNG

    @classmethod
    def get_loader(cls, file_path: str):
        for loader in cls._loaders:
            if loader.can_load(file_path):
                return loader
        return None