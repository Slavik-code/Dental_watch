from abc import ABC, abstractmethod
from models.app_state import AppState

class BaseLoader(ABC):
    @abstractmethod
    def can_load(self, file_path: str) -> bool:
        pass

    @abstractmethod
    def load(self, file_path: str, state: AppState) -> None:
        """Загружает изображение и заполняет state."""
        pass