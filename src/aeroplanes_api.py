import requests

from src.abstract_api import AbstractAeroplaneAPI


class AeroplanesAPI(AbstractAeroplaneAPI):
    """Реализация для Nominatim и OpenSky."""

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OPENSKY_URL = "https://opensky-network.org/api/states/all"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AeroplaneCoursework/1.0"})

    def get_country_bounding_box(self, country_name: str) -> tuple:
        """
        Получает bounding box страны через Nominatim API.
        Возвращает кортеж (south, north, west, east)
        """
        params = {"q": country_name, "format": "json", "limit": 1}

        try:
            response = self.session.get(self.NOMINATIM_URL, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            if not data:
                raise ValueError(f"Страна '{country_name}' не найдена")

            # Получаем boundingbox из ответа
            boundingbox = data[0]["boundingbox"]
            south = float(boundingbox[0])
            north = float(boundingbox[1])
            west = float(boundingbox[2])
            east = float(boundingbox[3])

            return (south, north, west, east)

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Ошибка запроса к Nominatim: {e}")
        except (KeyError, IndexError, ValueError) as e:
            raise ValueError(f"Ошибка обработки данных Nominatim: {e}")

    def get_aeroplanes_in_bbox(self, bbox: tuple) -> list:
        """
        Получает список самолётов в заданной области через OpenSky API.
        bbox: (south, north, west, east)
        """
        south, north, west, east = bbox

        params = {
            "lamin": south,  # южная широта
            "lamax": north,  # северная широта
            "lomin": west,  # западная долгота
            "lomax": east,  # восточная долгота
        }

        try:
            response = self.session.get(self.OPENSKY_URL, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            states = data.get("states", [])

            # Преобразуем сырые данные в список словарей
            aeroplanes_list = []
            for state in states:
                if state is None:
                    continue

                aeroplane_dict = {
                    "icao24": state[0],  # уникальный код самолёта
                    "callsign": state[1].strip() if state[1] else "N/A",  # позывной
                    "origin_country": state[2],  # страна регистрации
                    "time_position": state[3],  # время позиции
                    "last_contact": state[4],  # последний контакт
                    "longitude": state[5],  # долгота
                    "latitude": state[6],  # широта
                    "altitude": state[7],  # высота (метры)
                    "on_ground": state[8],  # на земле
                    "velocity": state[9],  # скорость (м/с)
                    "heading": state[10],  # курс
                    "vertical_rate": state[11],  # вертикальная скорость
                    "geo_altitude": state[13],  # геометрическая высота
                }
                aeroplanes_list.append(aeroplane_dict)

            return aeroplanes_list

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Ошибка запроса к OpenSky: {e}")

    def get_aeroplanes_by_country(self, country_name: str) -> list:
        """
        Получает самолёты по названию страны.
        Сначала получает bbox страны, затем самолёты в этой области.
        """
        try:
            bbox = self.get_country_bounding_box(country_name)
            aeroplanes = self.get_aeroplanes_in_bbox(bbox)
            return aeroplanes
        except Exception as e:
            raise Exception(f"Не удалось получить данные для страны '{country_name}': {e}")
