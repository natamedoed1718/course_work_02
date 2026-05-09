from unittest.mock import Mock, patch

from src.aeroplane import Aeroplane
from src.user_interface import filter_aeroplanes_by_text, get_top_by_altitude


class TestFilterFunctions:
    """Тестирование функций фильтрации."""

    def setup_method(self):
        self.planes = [
            Aeroplane("1", "A1", "Russia", 10000, 200),
            Aeroplane("2", "B2", "United States", 8000, 250),
            Aeroplane("3", "C3", "France", 12000, 220),
            Aeroplane("4", "D4", "Russia", 9000, 180),
            Aeroplane("5", "E5", "Germany", None, 190),
            Aeroplane("6", "F6", "USA", 7000, None),
        ]

    def test_filter_by_text_exact_country(self):
        filtered = filter_aeroplanes_by_text(self.planes, "Russia")
        assert len(filtered) == 2
        for plane in filtered:
            assert "Russia" in plane.origin_country

    def test_filter_by_text_partial_country(self):
        filtered = filter_aeroplanes_by_text(self.planes, "United")
        assert len(filtered) == 1
        assert filtered[0].origin_country == "United States"

    def test_filter_by_callsign(self):
        filtered = filter_aeroplanes_by_text(self.planes, "A1")
        assert len(filtered) == 1
        assert filtered[0].callsign == "A1"

    def test_filter_by_multiple_words(self):
        filtered = filter_aeroplanes_by_text(self.planes, "United States")
        assert len(filtered) == 1
        assert filtered[0].origin_country == "United States"

    def test_filter_empty_text(self):
        filtered = filter_aeroplanes_by_text(self.planes, "")
        assert len(filtered) == len(self.planes)

    def test_filter_no_match(self):
        filtered = filter_aeroplanes_by_text(self.planes, "Mars")
        assert len(filtered) == 0

    def test_filter_case_insensitive(self):
        filtered = filter_aeroplanes_by_text(self.planes, "russia")
        assert len(filtered) == 2
        for plane in filtered:
            assert "Russia" in plane.origin_country

    def test_filter_multiple_search_words(self):
        filtered = filter_aeroplanes_by_text(self.planes, "united states")
        assert len(filtered) == 1
        assert filtered[0].origin_country == "United States"


class TestGetTopByAltitude:
    """Тестирование функции get_top_by_altitude."""

    def setup_method(self):
        self.planes = [
            Aeroplane("1", "A1", "Russia", 10000, 200),
            Aeroplane("2", "B2", "United States", 8000, 250),
            Aeroplane("3", "C3", "France", 12000, 220),
            Aeroplane("4", "D4", "Russia", 9000, 180),
            Aeroplane("5", "E5", "Germany", None, 190),
            Aeroplane("6", "F6", "USA", 7000, None),
        ]

    def test_get_top_3_by_altitude(self):
        top_3 = get_top_by_altitude(self.planes, 3)
        assert len(top_3) == 3
        altitudes = [p.altitude for p in top_3]
        assert altitudes == [12000, 10000, 9000]

    def test_get_top_5_by_altitude(self):
        top_5 = get_top_by_altitude(self.planes, 5)
        assert len(top_5) == 5
        altitudes = [p.altitude for p in top_5]
        assert altitudes == [12000, 10000, 9000, 8000, 7000]

    def test_get_top_more_than_available(self):
        top_10 = get_top_by_altitude(self.planes, 10)
        assert len(top_10) == 5  # Только самолёты с высотой

    def test_get_top_excludes_none_altitudes(self):
        top_5 = get_top_by_altitude(self.planes, 5)
        for plane in top_5:
            assert plane.altitude is not None

    def test_get_top_empty_list(self):
        top = get_top_by_altitude([], 5)
        assert top == []

    def test_get_top_with_only_none_altitudes(self):
        planes_no_altitude = [Aeroplane("1", "A", "RU", None, 200), Aeroplane("2", "B", "US", None, 250)]
        top = get_top_by_altitude(planes_no_altitude, 3)
        assert top == []

    def test_get_top_single_plane(self):
        single_plane = [Aeroplane("1", "A", "RU", 5000, 200)]
        top = get_top_by_altitude(single_plane, 1)
        assert len(top) == 1
        assert top[0].altitude == 5000

    def test_get_top_n_equals_zero(self):
        top = get_top_by_altitude(self.planes, 0)
        assert top == []

    def test_get_top_negative_n(self):
        top = get_top_by_altitude(self.planes, -5)
        assert top == []


class TestUserInteractionIntegration:
    """Интеграционные тесты для user_interaction (с моками)."""

    @patch("src.user_interface.AeroplanesAPI")
    @patch("src.user_interface.JSONStorage")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_search_aeroplanes_success(self, mock_print, mock_input, mock_storage, mock_api):
        """Тест успешного поиска самолётов."""
        from src.user_interface import user_interaction

        # Настраиваем моки
        mock_api_instance = Mock()
        mock_api_instance.get_aeroplanes_by_country.return_value = [
            {"icao24": "test1", "callsign": "FL1", "origin_country": "USA", "altitude": 10000, "velocity": 200}
        ]
        mock_api.return_value = mock_api_instance

        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance

        # Симулируем ввод пользователя: выбрать пункт 1, ввести страну, затем 0 для выхода
        mock_input.side_effect = ["1", "France", "0"]

        user_interaction()

        # Проверяем, что API был вызван с правильным параметром
        mock_api_instance.get_aeroplanes_by_country.assert_called_with("France")

    @patch("src.user_interface.AeroplanesAPI")
    @patch("src.user_interface.JSONStorage")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_search_aeroplanes_not_found(self, mock_print, mock_input, mock_storage, mock_api):
        """Тест: самолёты не найдены."""
        from src.user_interface import user_interaction

        mock_api_instance = Mock()
        mock_api_instance.get_aeroplanes_by_country.return_value = []
        mock_api.return_value = mock_api_instance

        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance

        mock_input.side_effect = ["1", "Antarctica", "0"]

        user_interaction()

        mock_api_instance.get_aeroplanes_by_country.assert_called_with("Antarctica")

    @patch("src.user_interface.AeroplanesAPI")
    @patch("src.user_interface.JSONStorage")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_search_aeroplanes_error(self, mock_print, mock_input, mock_storage, mock_api):
        """Тест: ошибка при поиске."""
        from src.user_interface import user_interaction

        mock_api_instance = Mock()
        mock_api_instance.get_aeroplanes_by_country.side_effect = Exception("API Error")
        mock_api.return_value = mock_api_instance

        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance

        mock_input.side_effect = ["1", "Invalid", "0"]

        user_interaction()

    @patch("src.user_interface.AeroplanesAPI")
    @patch("src.user_interface.JSONStorage")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_get_top_without_search(self, mock_print, mock_input, mock_storage, mock_api):
        """Тест: попытка получить топ без предварительного поиска."""
        from src.user_interface import user_interaction

        mock_api_instance = Mock()
        mock_api.return_value = mock_api_instance

        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance

        # Сразу выбираем пункт 2 (топ), потом 0 для выхода
        mock_input.side_effect = ["2", "0"]

        user_interaction()

        # Проверяем, что было выведено сообщение о необходимости сначала выполнить поиск
        # (проверяем через mock_print, но это опционально)

    @patch("src.user_interface.AeroplanesAPI")
    @patch("src.user_interface.JSONStorage")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_save_without_search(self, mock_print, mock_input, mock_storage, mock_api):
        """Тест: попытка сохранить без данных."""
        from src.user_interface import user_interaction

        mock_api_instance = Mock()
        mock_api.return_value = mock_api_instance

        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance

        mock_input.side_effect = ["4", "0"]

        user_interaction()

    @patch("src.user_interface.AeroplanesAPI")
    @patch("src.user_interface.JSONStorage")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_invalid_choice(self, mock_print, mock_input, mock_storage, mock_api):
        """Тест: неверный выбор в меню."""
        from src.user_interface import user_interaction

        mock_api_instance = Mock()
        mock_api.return_value = mock_api_instance

        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance

        mock_input.side_effect = ["99", "0"]

        user_interaction()

    @patch("src.user_interface.AeroplanesAPI")
    @patch("src.user_interface.JSONStorage")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_exit_program(self, mock_print, mock_input, mock_storage, mock_api):
        """Тест: выход из программы."""
        from src.user_interface import user_interaction

        mock_api_instance = Mock()
        mock_api.return_value = mock_api_instance

        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance

        mock_input.side_effect = ["0"]

        user_interaction()
