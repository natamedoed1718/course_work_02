import json
import os
from typing import List, Dict, Any
from src.abstract_storage import AbstractStorage
from src.aeroplane import Aeroplane


class JSONStorage(AbstractStorage):
    """Класс для сохранения информации о самолётах в JSON-файл."""

    def __init__(self, filename: str = "data/aeroplanes.json") -> None:
        self.filename: str = filename

        # Создаём папку data, если её нет
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"[OK] Создана папка: {directory}")

        # Создаём файл, если его нет
        if not os.path.exists(filename):
            self._save_data([])
            print(f"[OK] Создан файл: {filename}")

    def _load_data(self) -> List[Dict[str, Any]]:
        """Загружает данные из JSON файла."""
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                data: List[Dict[str, Any]] = json.load(file)
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        """Сохраняет данные в JSON файл."""
        directory = os.path.dirname(self.filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    # Реализация абстрактных методов
    def add_aeroplane(self, aeroplane: Aeroplane) -> bool:
        """Добавляет самолёт в файл."""
        data: List[Dict[str, Any]] = self._load_data()
        plane_dict: Dict[str, Any] = aeroplane.to_dict()

        # Проверяем, нет ли уже такого самолёта (по icao24)
        for item in data:
            if item.get("icao24") == plane_dict["icao24"]:
                return False

        data.append(plane_dict)
        self._save_data(data)
        print(f"[OK] Самолёт {plane_dict['callsign']} добавлен в файл")
        return True

    def get_aeroplanes(self) -> List[Aeroplane]:
        """Возвращает список всех самолётов из файла."""
        data: List[Dict[str, Any]] = self._load_data()
        return [Aeroplane.from_dict(item) for item in data]

    def delete_aeroplane(self, icao24: str) -> bool:
        """Удаляет самолёт по ICAO24 коду."""
        data: List[Dict[str, Any]] = self._load_data()
        original_length: int = len(data)
        data = [item for item in data if item.get("icao24") != icao24]

        if len(data) < original_length:
            self._save_data(data)
            return True
        return False

    def clear_all(self) -> None:
        """Очищает всё хранилище."""
        self._save_data([])
        print("[OK] Хранилище очищено")

    # Дополнительные методы
    def get_by_country(self, country: str) -> List[Aeroplane]:
        """Получает самолёты по стране регистрации."""
        all_planes: List[Aeroplane] = self.get_aeroplanes()
        return [plane for plane in all_planes if plane.origin_country.lower() == country.lower()]

    def get_file_path(self) -> str:
        """Возвращает полный путь к файлу."""
        return os.path.abspath(self.filename)

    # Алиасы для совместимости с абстрактным классом (если нужно)
    def add(self, aeroplane: Aeroplane) -> bool:
        """Алиас для add_aeroplane."""
        return self.add_aeroplane(aeroplane)

    def get_all(self) -> List[Aeroplane]:
        """Алиас для get_aeroplanes."""
        return self.get_aeroplanes()

    def delete(self, icao24: str) -> bool:
        """Алиас для delete_aeroplane."""
        return self.delete_aeroplane(icao24)

