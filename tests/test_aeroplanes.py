import pytest

from src.aeroplane import Aeroplane


class TestAeroplane:
    """Тестирование класса Aeroplane."""

    def test_create_valid_aeroplane(self):
        plane = Aeroplane("abc123", "FL123", "USA", 10000.5, 250.0)
        assert plane.icao24 == "abc123"
        assert plane.callsign == "FL123"
        assert plane.origin_country == "USA"
        assert plane.altitude == 10000.5
        assert plane.velocity == 250.0

    def test_create_with_empty_callsign(self):
        plane = Aeroplane("abc123", "", "Russia", 5000, 200)
        assert plane.callsign == "N/A"

    def test_invalid_altitude_negative(self):
        with pytest.raises(ValueError, match="Высота не может быть отрицательной"):
            Aeroplane("abc", "FL", "USA", -100, 200)

    def test_invalid_velocity_negative(self):
        with pytest.raises(ValueError, match="Скорость не может быть отрицательной"):
            Aeroplane("abc", "FL", "USA", 1000, -50)

    def test_compare_by_altitude(self):
        plane1 = Aeroplane("1", "A", "RU", 10000, 200)
        plane2 = Aeroplane("2", "B", "US", 15000, 180)
        plane3 = Aeroplane("3", "C", "DE", 10000, 220)

        assert plane2.compare_by_altitude(plane1) == 1
        assert plane1.compare_by_altitude(plane2) == -1
        assert plane1.compare_by_altitude(plane3) == 0

    def test_compare_by_velocity(self):
        plane1 = Aeroplane("1", "A", "RU", 10000, 200)
        plane2 = Aeroplane("2", "B", "US", 10000, 250)

        assert plane2.compare_by_velocity(plane1) == 1
        assert plane1.compare_by_velocity(plane2) == -1

    def test_compare_with_none_values(self):
        plane1 = Aeroplane("1", "A", "RU", 10000, None)
        plane2 = Aeroplane("2", "B", "US", 10000, 200)

        assert plane1.compare_by_velocity(plane2) == -1

        plane3 = Aeroplane("3", "C", "DE", None, 200)
        plane4 = Aeroplane("4", "D", "FR", 10000, 200)

        assert plane3.compare_by_altitude(plane4) == -1

    def test_lt_operator(self):
        plane1 = Aeroplane("1", "A", "RU", 10000, 200)
        plane2 = Aeroplane("2", "B", "US", 15000, 180)

        assert plane1 < plane2

    def test_lt_operator_with_none(self):
        plane1 = Aeroplane("1", "A", "RU", None, 200)
        plane2 = Aeroplane("2", "B", "US", 10000, 180)

        assert plane1 < plane2

    def test_eq_operator(self):
        plane1 = Aeroplane("1", "A", "RU", 10000, 200)
        plane2 = Aeroplane("2", "B", "US", 10000, 200)

        assert plane1 == plane2

    def test_to_dict(self):
        plane = Aeroplane("test123", "TEST", "UK", 8000, 180)
        dict_repr = plane.to_dict()

        assert dict_repr["icao24"] == "test123"
        assert dict_repr["callsign"] == "TEST"
        assert dict_repr["origin_country"] == "UK"
        assert dict_repr["altitude"] == 8000
        assert dict_repr["velocity"] == 180

    def test_from_dict(self):
        data = {"icao24": "test123", "callsign": "TEST", "origin_country": "UK", "altitude": 8000, "velocity": 180}
        plane = Aeroplane.from_dict(data)
        assert plane.icao24 == "test123"
        assert plane.callsign == "TEST"
        assert plane.origin_country == "UK"
        assert plane.altitude == 8000
        assert plane.velocity == 180

    def test_from_api_dict(self):
        data = {
            "icao24": "abc123",
            "callsign": "FL123",
            "origin_country": "USA",
            "altitude": "10000",
            "velocity": "250",
        }
        plane = Aeroplane.from_api_dict(data)
        assert plane.icao24 == "abc123"
        assert plane.altitude == 10000
        assert plane.velocity == 250

    def test_cast_to_object_list(self):
        data_list = [
            {"icao24": "1", "callsign": "FL1", "origin_country": "USA", "altitude": 10000, "velocity": 200},
            {"icao24": "2", "callsign": "FL2", "origin_country": "Russia", "altitude": 8000, "velocity": 180},
        ]
        objects = Aeroplane.cast_to_object_list(data_list)
        assert len(objects) == 2
        assert isinstance(objects[0], Aeroplane)
        assert objects[0].icao24 == "1"

    def test_str_method(self):
        plane = Aeroplane("abc", "FL123", "USA", 10000, 250)
        str_repr = str(plane)
        assert "FL123" in str_repr
        assert "USA" in str_repr


# Тесты для функций фильтрации


class TestFilterFunctions:
    """Тестирование функций фильтрации и сортировки."""

    def setup_method(self):
        from src.user_interface import filter_aeroplanes_by_text, get_top_by_altitude

        self.filter_aeroplanes_by_text = filter_aeroplanes_by_text
        self.get_top_by_altitude = get_top_by_altitude

        # Создаём тестовые данные
        # Самолёты с высотой: индексы 0,1,2,3,5 (всего 5)
        # Самолёты без высоты: индекс 4 (1 штука)
        self.planes = [
            Aeroplane("1", "A1", "Russia", 10000, 200),  # есть высота
            Aeroplane("2", "B2", "United States", 8000, 250),  # есть высота
            Aeroplane("3", "C3", "France", 12000, 220),  # есть высота
            Aeroplane("4", "D4", "Russia", 9000, 180),  # есть высота
            Aeroplane("5", "E5", "Germany", None, 190),  # нет высоты
            Aeroplane("6", "F6", "USA", 7000, None),  # есть высота (7000)
        ]

    def test_filter_by_text_exact_country(self):
        filtered = self.filter_aeroplanes_by_text(self.planes, "Russia")
        assert len(filtered) == 2
        for plane in filtered:
            assert "Russia" in plane.origin_country

    def test_filter_by_text_partial_country(self):
        filtered = self.filter_aeroplanes_by_text(self.planes, "United")
        assert len(filtered) == 1
        assert filtered[0].origin_country == "United States"

    def test_filter_by_callsign(self):
        filtered = self.filter_aeroplanes_by_text(self.planes, "A1")
        assert len(filtered) == 1
        assert filtered[0].callsign == "A1"

    def test_filter_by_multiple_words(self):
        filtered = self.filter_aeroplanes_by_text(self.planes, "United States")
        assert len(filtered) == 1
        assert filtered[0].origin_country == "United States"

    def test_filter_empty_text(self):
        filtered = self.filter_aeroplanes_by_text(self.planes, "")
        assert len(filtered) == len(self.planes)

    def test_filter_no_match(self):
        filtered = self.filter_aeroplanes_by_text(self.planes, "Mars")
        assert len(filtered) == 0

    def test_get_top_by_altitude(self):
        top_3 = self.get_top_by_altitude(self.planes, 3)
        assert len(top_3) == 3
        # Проверяем, что высоты отсортированы по убыванию
        altitudes = [p.altitude for p in top_3]
        assert altitudes == [12000, 10000, 9000]

    def test_get_top_by_altitude_excludes_none(self):
        """Тест: самолёты с None высотой не попадают в топ."""
        top_5 = self.get_top_by_altitude(self.planes, 5)
        # Все самолёты в топе должны иметь высоту
        for plane in top_5:
            assert plane.altitude is not None
        # В топе должно быть 5 самолётов (все с высотой)
        assert len(top_5) == 5

    def test_get_top_more_than_available(self):
        top_10 = self.get_top_by_altitude(self.planes, 10)
        # Должны вернуться все самолёты с высотой (их 5)
        assert len(top_10) == 5

    def test_get_top_empty_list(self):
        top = self.get_top_by_altitude([], 5)
        assert top == []

    def test_get_top_with_only_none_altitudes(self):
        """Тест: только самолёты без высоты."""
        planes_no_altitude = [Aeroplane("1", "A", "RU", None, 200), Aeroplane("2", "B", "US", None, 250)]
        top = self.get_top_by_altitude(planes_no_altitude, 3)
        assert top == []
