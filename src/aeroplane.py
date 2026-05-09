class Aeroplane:
    """Класс, описывающий самолёт с валидацией и сравнением."""

    def __init__(
        self, icao24: str, callsign: str, origin_country: str, altitude: float | None, velocity: float | None
    ):
        self._icao24 = icao24
        self._callsign = callsign
        self._origin_country = origin_country
        self.altitude = altitude  # используем setter для валидации
        self.velocity = velocity  # используем setter для валидации

    # region Геттеры и сеттеры с валидацией
    @property
    def icao24(self) -> str:
        return self._icao24

    @property
    def callsign(self) -> str:
        return self._callsign or "N/A"

    @property
    def origin_country(self) -> str:
        return self._origin_country

    @property
    def altitude(self) -> float | None:
        return self._altitude

    @altitude.setter
    def altitude(self, value: float | None):
        if value is not None and value < 0:
            raise ValueError("Высота не может быть отрицательной")
        self._altitude = value

    @property
    def velocity(self) -> float | None:
        return self._velocity

    @velocity.setter
    def velocity(self, value: float | None):
        if value is not None and value < 0:
            raise ValueError("Скорость не может быть отрицательной")
        self._velocity = value

    # endregion

    # region Методы сравнения (по скорости и высоте)
    def __eq__(self, other: "Aeroplane") -> bool:
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.velocity == other.velocity and self.altitude == other.altitude

    def __lt__(self, other: "Aeroplane") -> bool:
        if not isinstance(other, Aeroplane):
            return NotImplemented
        # Сравниваем по высоте, если одинаковая – по скорости
        if self.altitude != other.altitude:
            return (self.altitude or 0) < (other.altitude or 0)
        return (self.velocity or 0) < (other.velocity or 0)

    def __le__(self, other: "Aeroplane") -> bool:
        return self < other or self == other

    def __gt__(self, other: "Aeroplane") -> bool:
        return not (self <= other)

    def __ge__(self, other: "Aeroplane") -> bool:
        return not (self < other)

    # endregion

    def __repr__(self) -> str:
        return (
            f"Aeroplane(icao24={self._icao24!r}, callsign={self.callsign!r}, "
            f"country={self._origin_country!r}, alt={self.altitude} м, vel={self.velocity} м/с)"
        )

    def __str__(self) -> str:
        vel_kmh = (self.velocity * 3.6) if self.velocity is not None else "N/A"
        alt_m = f"{self.altitude:.0f}" if self.altitude is not None else "N/A"
        return f"✈ {self.callsign} ({self._origin_country}) | " f"Высота: {alt_m} м | Скорость: {vel_kmh} км/ч"

    @classmethod
    def from_api_dict(cls, data: dict) -> "Aeroplane":
        """Фабричный метод для создания объекта из словаря OpenSky."""
        altitude = data.get("altitude")
        velocity = data.get("velocity")
        # Конвертируем None в None, а числа оставляем как есть
        if altitude is not None and altitude != "":
            altitude = float(altitude)
        else:
            altitude = None
        if velocity is not None and velocity != "":
            velocity = float(velocity)
        else:
            velocity = None

        return cls(
            icao24=data.get("icao24", ""),
            callsign=data.get("callsign", ""),
            origin_country=data.get("origin_country", "Unknown"),
            altitude=altitude,
            velocity=velocity,
        )

    @staticmethod
    def cast_to_object_list(data_list: list[dict]) -> list["Aeroplane"]:
        """Преобразует список словарей в список объектов Aeroplane."""
        objects = []
        for item in data_list:
            try:
                objects.append(Aeroplane.from_api_dict(item))
            except (ValueError, TypeError, KeyError) as e:
                print(f"Пропущен некорректный объект: {e} | Данные: {item}")
        return objects

    def to_dict(self) -> dict:
        """Преобразует объект в словарь для сохранения в JSON."""
        return {
            "icao24": self._icao24,
            "callsign": self._callsign,
            "origin_country": self._origin_country,
            "altitude": self._altitude,
            "velocity": self._velocity,
        }
