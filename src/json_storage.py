import json
import os
from typing import Any, Dict, List

from src.abstract_storage import AbstractStorage
from src.aeroplane import Aeroplane


class JSONStorage(AbstractStorage):
    """Класс для сохранения информации о самолётах в JSON-файл."""

    def __init__(self, filename: str = "data/aeroplanes.json") -> None:
        self.filename: str = filename
        self.file_path = os.path.abspath(filename)  # Добавляем атрибут file_path

        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(self.file_path):
            self._save_data([])

    def _load_data(self) -> List[Dict[str, Any]]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def add_aeroplane(self, aeroplane: Aeroplane) -> bool:
        data = self._load_data()
        plane_dict = aeroplane.to_dict()

        for item in data:
            if item.get("icao24") == plane_dict["icao24"]:
                return False

        data.append(plane_dict)
        self._save_data(data)
        return True

    def get_aeroplanes(self) -> List[Aeroplane]:
        data = self._load_data()
        return [Aeroplane.from_dict(item) for item in data]

    def delete_aeroplane(self, icao24: str) -> bool:
        data = self._load_data()
        original_length = len(data)
        data = [item for item in data if item.get("icao24") != icao24]

        if len(data) < original_length:
            self._save_data(data)
            return True
        return False

    def clear_all(self) -> None:
        self._save_data([])
