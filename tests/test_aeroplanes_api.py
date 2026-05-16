from unittest.mock import Mock, patch

import pytest
import requests

from src.aeroplanes_api import AeroplanesAPI


class TestAeroplanesAPI:
    """Тестирование класса AeroplanesAPI."""

    def setup_method(self):
        self.api = AeroplanesAPI(timeout=5)

    # Тесты для get_country_bounding_box
    @patch("src.aeroplanes_api.requests.Session.get")
    def test_get_country_bounding_box_success(self, mock_get):
        """Тест успешного получения bounding box."""
        mock_response = Mock()
        mock_response.json.return_value = [{"boundingbox": ["41.0", "82.0", "19.0", "169.0"]}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.api.get_country_bounding_box("Russia")
        assert result == (41.0, 82.0, 19.0, 169.0)

    @patch("src.aeroplanes_api.requests.Session.get")
    def test_get_country_bounding_box_not_found(self, mock_get):
        """Тест: страна не найдена."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Страна 'Xyz' не найдена"):
            self.api.get_country_bounding_box("Xyz")

    @patch("src.aeroplanes_api.requests.Session.get")
    def test_get_country_bounding_box_request_error(self, mock_get):
        """Тест: ошибка запроса к API."""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        with pytest.raises(ConnectionError, match="Ошибка запроса к Nominatim"):
            self.api.get_country_bounding_box("Russia")

    @patch("src.aeroplanes_api.requests.Session.get")
    def test_get_country_bounding_box_timeout(self, mock_get):
        """Тест: таймаут запроса."""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        # При таймауте выбрасывается ConnectionError с общим сообщением
        with pytest.raises(ConnectionError):
            self.api.get_country_bounding_box("Russia")

    @patch("src.aeroplanes_api.requests.Session.get")
    def test_get_country_bounding_box_invalid_response(self, mock_get):
        """Тест: некорректный ответ от API."""
        mock_response = Mock()
        mock_response.json.return_value = [{}]  # Нет поля boundingbox
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Ошибка обработки данных Nominatim"):
            self.api.get_country_bounding_box("Russia")

    # Тесты для get_aeroplanes_in_bbox
    @patch("src.aeroplanes_api.requests.Session.get")
    def test_get_aeroplanes_in_bbox_success(self, mock_get):
        """Тест успешного получения самолётов."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "states": [
                ["abc123", "FL123", "USA", 123456, 123457, 50.0, 30.0, 10000, False, 250.0, 90, 0, None, 10050],
                ["def456", "FL456", "Canada", 123458, 123459, 60.0, 40.0, 8000, False, 200.0, 95, 5, None, 8050],
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        bbox = (41.0, 82.0, 19.0, 169.0)
        result = self.api.get_aeroplanes_in_bbox(bbox)

        assert len(result) == 2
        assert result[0]["icao24"] == "abc123"
        assert result[0]["callsign"] == "FL123"
        assert result[0]["origin_country"] == "USA"
        assert result[0]["altitude"] == 10000
        assert result[1]["icao24"] == "def456"

    @patch("src.aeroplanes_api.requests.Session.get")
    def test_get_aeroplanes_in_bbox_empty(self, mock_get):
        """Тест: пустой ответ от API."""
        mock_response = Mock()
        mock_response.json.return_value = {"states": None}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        bbox = (41.0, 82.0, 19.0, 169.0)
        result = self.api.get_aeroplanes_in_bbox(bbox)

        assert result == []

    @patch("src.aeroplanes_api.requests.Session.get")
    def test_get_aeroplanes_in_bbox_with_none_states(self, mock_get):
        """Тест: states содержит None элементы."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "states": [
                None,
                ["abc123", "FL123", "USA", 123456, 123457, 50.0, 30.0, 10000, False, 250.0, 90, 0, None, 10050],
                None,
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        bbox = (41.0, 82.0, 19.0, 169.0)
        result = self.api.get_aeroplanes_in_bbox(bbox)

        assert len(result) == 1
        assert result[0]["icao24"] == "abc123"

    @patch("src.aeroplanes_api.requests.Session.get")
    def test_get_aeroplanes_in_bbox_request_error(self, mock_get):
        """Тест: ошибка запроса к OpenSky."""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        bbox = (41.0, 82.0, 19.0, 169.0)
        with pytest.raises(ConnectionError, match="Ошибка запроса к OpenSky"):
            self.api.get_aeroplanes_in_bbox(bbox)

    @patch("src.aeroplanes_api.requests.Session.get")
    def test_get_aeroplanes_in_bbox_timeout(self, mock_get):
        """Тест: таймаут при запросе к OpenSky."""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        bbox = (41.0, 82.0, 19.0, 169.0)
        # При таймауте выбрасывается ConnectionError с общим сообщением
        with pytest.raises(ConnectionError):
            self.api.get_aeroplanes_in_bbox(bbox)

    @patch("src.aeroplanes_api.requests.Session.get")
    def test_get_aeroplanes_in_bbox_short_state(self, mock_get):
        """Тест: state с недостаточным количеством элементов."""
        mock_response = Mock()
        mock_response.json.return_value = {"states": [["short"]]}  # Слишком короткий список
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        bbox = (41.0, 82.0, 19.0, 169.0)
        result = self.api.get_aeroplanes_in_bbox(bbox)

        assert result == []  # Пропускаем некорректные данные

    @patch("src.aeroplanes_api.requests.Session.get")
    def test_get_aeroplanes_in_bbox_not_list(self, mock_get):
        """Тест: states не является списком."""
        mock_response = Mock()
        mock_response.json.return_value = {"states": "not a list"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        bbox = (41.0, 82.0, 19.0, 169.0)
        result = self.api.get_aeroplanes_in_bbox(bbox)

        assert result == []

    # Тесты для get_aeroplanes_by_country
    @patch("src.aeroplanes_api.AeroplanesAPI.get_country_bounding_box")
    @patch("src.aeroplanes_api.AeroplanesAPI.get_aeroplanes_in_bbox")
    def test_get_aeroplanes_by_country_success(self, mock_get_aeroplanes, mock_get_bbox):
        """Тест успешного получения самолётов по стране."""
        mock_get_bbox.return_value = (41.0, 82.0, 19.0, 169.0)
        mock_get_aeroplanes.return_value = [{"icao24": "test", "callsign": "TEST"}]

        result = self.api.get_aeroplanes_by_country("Russia")

        assert len(result) == 1
        mock_get_bbox.assert_called_once_with("Russia")
        mock_get_aeroplanes.assert_called_once_with((41.0, 82.0, 19.0, 169.0))

    @patch("src.aeroplanes_api.AeroplanesAPI.get_country_bounding_box")
    def test_get_aeroplanes_by_country_bbox_error(self, mock_get_bbox):
        """Тест: ошибка при получении bbox."""
        mock_get_bbox.side_effect = ValueError("Country not found")

        with pytest.raises(Exception, match="Не удалось получить данные для страны 'InvalidCountry'"):
            self.api.get_aeroplanes_by_country("InvalidCountry")

    @patch("src.aeroplanes_api.AeroplanesAPI.get_country_bounding_box")
    @patch("src.aeroplanes_api.AeroplanesAPI.get_aeroplanes_in_bbox")
    def test_get_aeroplanes_by_country_aeroplanes_error(self, mock_get_aeroplanes, mock_get_bbox):
        """Тест: ошибка при получении самолётов."""
        mock_get_bbox.return_value = (41.0, 82.0, 19.0, 169.0)
        mock_get_aeroplanes.side_effect = ConnectionError("OpenSky error")

        with pytest.raises(Exception, match="Не удалось получить данные для страны 'Russia'"):
            self.api.get_aeroplanes_by_country("Russia")

    # Тест для инициализации
    def test_init_creates_session(self):
        """Тест: инициализация создаёт сессию с правильным User-Agent."""
        api = AeroplanesAPI(timeout=30)
        assert api.timeout == 30
        assert api.session.headers["User-Agent"] == "AeroplaneCoursework/1.0"

    # Дополнительные тесты для покрытия
    @patch("src.aeroplanes_api.requests.Session.get")
    def test_get_aeroplanes_in_bbox_with_empty_callsign(self, mock_get):
        """Тест: самолёт с пустым позывным."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "states": [["abc123", "", "USA", 123456, 123457, 50.0, 30.0, 10000, False, 250.0, 90, 0, None, 10050]]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        bbox = (41.0, 82.0, 19.0, 169.0)
        result = self.api.get_aeroplanes_in_bbox(bbox)

        assert len(result) == 1
        assert result[0]["callsign"] == "N/A"  # Пустой позывной заменяется на N/A

    @patch("src.aeroplanes_api.requests.Session.get")
    def test_get_aeroplanes_in_bbox_with_none_callsign(self, mock_get):
        """Тест: самолёт с None в позывном."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "states": [["abc123", None, "USA", 123456, 123457, 50.0, 30.0, 10000, False, 250.0, 90, 0, None, 10050]]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        bbox = (41.0, 82.0, 19.0, 169.0)
        result = self.api.get_aeroplanes_in_bbox(bbox)

        assert len(result) == 1
        assert result[0]["callsign"] == "N/A"  # None заменяется на N/A

    @patch("src.aeroplanes_api.requests.Session.get")
    def test_get_aeroplanes_in_bbox_missing_fields(self, mock_get):
        """Тест: отсутствие некоторых полей в ответе."""
        mock_response = Mock()
        mock_response.json.return_value = {"states": [["abc123"]]}  # Только ICAO24, остальных полей нет
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        bbox = (41.0, 82.0, 19.0, 169.0)
        result = self.api.get_aeroplanes_in_bbox(bbox)

        # Проверяем, что короткие записи пропускаются
        assert result == []
