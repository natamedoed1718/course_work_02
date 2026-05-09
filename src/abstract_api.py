from abc import ABC, abstractmethod


class AbstractAeroplaneAPI(ABC):
    """Абстрактный класс для работы с API самолётов и геоданных."""

    @abstractmethod
    def get_country_bounding_box(self, country_name: str) -> tuple[float, float, float, float]:
        """Получает bounding box страны через Nominatim."""
        pass

    @abstractmethod
    def get_aeroplanes_in_bbox(self, bbox: tuple[float, float, float, float]) -> list[dict]:
        """Получает список самолётов в заданной области через OpenSky."""
        pass

    @abstractmethod
    def get_aeroplanes_by_country(self, country_name: str) -> list[dict]:
        """Получает самолёты по названию страны."""
        pass
