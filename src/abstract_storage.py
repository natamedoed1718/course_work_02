from abc import ABC, abstractmethod
from typing import Any


class AbstractStorage(ABC):
    """Абстрактный класс для работы с хранилищем (файл, БД и т.д.)."""

    @abstractmethod
    def add_aeroplane(self, data: Any) -> bool:
        """Добавляет самолёт в хранилище."""
        pass

    @abstractmethod
    def get_aeroplanes(self) -> list[Any]:
        """Возвращает все самолёты."""
        pass

    @abstractmethod
    def delete_aeroplane(self, icao24: str) -> bool:
        """Удаляет самолёт по ICAO24 коду."""
        pass

    @abstractmethod
    def clear_all(self) -> None:
        """Очищает всё хранилище."""
        pass
