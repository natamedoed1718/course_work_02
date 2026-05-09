import json
import os
import tempfile

from src.aeroplane import Aeroplane
from src.json_storage import JSONStorage


class TestJSONStorage:
    """Тестирование класса JSONStorage."""

    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        self.temp_file.close()
        self.storage = JSONStorage(self.temp_file.name)

    def teardown_method(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_add_aeroplane(self):
        plane = Aeroplane("test1", "TEST1", "RU", 5000, 200)
        result = self.storage.add_aeroplane(plane)
        assert result is True

        planes = self.storage.get_aeroplanes()
        assert len(planes) == 1
        assert planes[0].icao24 == "test1"

    def test_add_duplicate_aeroplane(self):
        plane = Aeroplane("test1", "TEST1", "RU", 5000, 200)
        self.storage.add_aeroplane(plane)
        result = self.storage.add_aeroplane(plane)
        assert result is False

        planes = self.storage.get_aeroplanes()
        assert len(planes) == 1

    def test_add_multiple_aeroplanes(self):
        plane1 = Aeroplane("test1", "TEST1", "RU", 5000, 200)
        plane2 = Aeroplane("test2", "TEST2", "US", 6000, 250)
        plane3 = Aeroplane("test3", "TEST3", "FR", 7000, 300)

        self.storage.add_aeroplane(plane1)
        self.storage.add_aeroplane(plane2)
        self.storage.add_aeroplane(plane3)

        planes = self.storage.get_aeroplanes()
        assert len(planes) == 3

    def test_delete_aeroplane(self):
        plane1 = Aeroplane("test1", "TEST1", "RU", 5000, 200)
        plane2 = Aeroplane("test2", "TEST2", "US", 6000, 250)

        self.storage.add_aeroplane(plane1)
        self.storage.add_aeroplane(plane2)

        result = self.storage.delete_aeroplane("test1")
        assert result is True

        planes = self.storage.get_aeroplanes()
        assert len(planes) == 1
        assert planes[0].icao24 == "test2"

    def test_delete_nonexistent_aeroplane(self):
        plane = Aeroplane("test1", "TEST1", "RU", 5000, 200)
        self.storage.add_aeroplane(plane)

        result = self.storage.delete_aeroplane("nonexistent")
        assert result is False

        planes = self.storage.get_aeroplanes()
        assert len(planes) == 1

    def test_clear_all(self):
        plane1 = Aeroplane("test1", "TEST1", "RU", 5000, 200)
        plane2 = Aeroplane("test2", "TEST2", "US", 6000, 250)

        self.storage.add_aeroplane(plane1)
        self.storage.add_aeroplane(plane2)

        self.storage.clear_all()
        planes = self.storage.get_aeroplanes()
        assert len(planes) == 0

    def test_get_empty_storage(self):
        planes = self.storage.get_aeroplanes()
        assert planes == []

    def test_file_persistence(self):
        plane = Aeroplane("test1", "TEST1", "RU", 5000, 200)
        self.storage.add_aeroplane(plane)

        new_storage = JSONStorage(self.temp_file.name)
        planes = new_storage.get_aeroplanes()

        assert len(planes) == 1
        assert planes[0].icao24 == "test1"
