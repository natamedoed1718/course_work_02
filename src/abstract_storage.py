from abc import ABC, abstractmethod
from typing import Any


class AbstractStorage(ABC):
    """Абстрактный класс для работы с хранилищем (файл, БД и т.д.)."""

    @abstractmethod
    def add(self, data: dict[str, Any]) -> None:
        """Добавляет запись (словарь) в хранилище."""
        pass

    @abstractmethod
    def get_all(self) -> list[dict[str, Any]]:
        """Возвращает все записи."""
        pass

    @abstractmethod
    def delete(self, predicate) -> int:
        """Удаляет записи, удовлетворяющие условию predicate(record). Возвращает кол-во удалённых."""
        pass
