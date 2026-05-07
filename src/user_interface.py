from src.aeroplane import Aeroplane
from src.aeroplanes_api import AeroplanesAPI
from src.json_storage import JSONStorage


def user_interaction():
    """Основной цикл общения с пользователем через консоль."""
    print("✈ Добро пожаловать в систему мониторинга самолётов ✈")
    api = AeroplanesAPI()
    storage = JSONStorage()

    while True:
        print("\nВыберите действие:")
        print("1. Поискать самолёты над страной")
        print("2. Показать топ N самолётов по высоте (из последнего запроса)")
        print("3. Найти самолёты по стране регистрации (из последнего запроса)")
        print("4. Сохранить последние данные в JSON")
        print("5. Показать сохранённые самолёты из JSON")
        print("6. Очистить JSON-хранилище")
        print("0. Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            print("До свидания!")
            break

        elif choice == "1":
            country = input("Введите название страны (например, Russia, France, Canada): ").strip()
            try:
                print(f"Получаем данные для {country}...")
                raw_data = api.get_aeroplanes_by_country(country)
                if not raw_data:
                    print("Самолётов не найдено или страна не имеет воздушного пространства.")
                else:
                    # Сохраняем в глобальную переменную (в реальном проекте лучше через объект состояния)
                    global current_aeroplanes
                    current_aeroplanes = Aeroplane.cast_to_object_list(raw_data)
                    print(f"Найдено самолётов: {len(current_aeroplanes)}")
                    # Показываем первые 5 для примера
                    for plane in current_aeroplanes[:5]:
                        print(f"  - {plane}")
                    if len(current_aeroplanes) > 5:
                        print("  ... (остальные можно посмотреть через топ N или фильтрацию)")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "2":
            if not current_aeroplanes:
                print("Сначала выполните поиск (пункт 1).")
                continue
            try:
                n = int(input("Введите количество N для топ-самолётов по высоте: "))
                if n <= 0:
                    print("N должно быть положительным.")
                    continue
                # Сортировка по убыванию высоты (None – в конец)
                sorted_planes = sorted(
                    current_aeroplanes, key=lambda p: (p.altitude is None, p.altitude or 0), reverse=False
                )  # сначала None
                # Выше всех те, у кого altitude не None и большое
                sorted_by_alt_desc = sorted(
                    current_aeroplanes, key=lambda p: (p.altitude is None, p.altitude or 0), reverse=True
                )
                top_n = sorted_by_alt_desc[:n]
                print(f"\nТоп {n} самолётов по высоте:")
                for i, plane in enumerate(top_n, start=1):
                    alt_display = f"{plane.altitude:.0f} м" if plane.altitude is not None else "нет данных"
                    print(f"{i:2d}. {plane.callsign} ({plane.origin_country}) – {alt_display}")
            except ValueError:
                print("Ошибка: введите целое число.")

        elif choice == "3":
            if not current_aeroplanes:
                print("Сначала выполните поиск (пункт 1).")
                continue
            countries_input = input("Введите страну регистрации (или несколько через пробел): ").strip()
            if not countries_input:
                print("Название страны не введено.")
                continue
            countries = [c.strip().lower() for c in countries_input.split()]
            filtered = [p for p in current_aeroplanes if p.origin_country.lower() in countries]
            print(f"\nНайдено самолётов из {countries_input}: {len(filtered)}")
            for plane in filtered[:20]:  # ограничим вывод
                print(f"  - {plane}")
            if len(filtered) > 20:
                print("  ... (показаны первые 20)")

        elif choice == "4":
            if not current_aeroplanes:
                print("Нет данных для сохранения. Сначала выполните поиск (пункт 1).")
                continue
            count = 0
            for plane in current_aeroplanes:
                # Преобразуем объект в словарь
                plane_dict = {
                    "icao24": plane.icao24,
                    "callsign": plane.callsign,
                    "origin_country": plane.origin_country,
                    "altitude": plane.altitude,
                    "velocity": plane.velocity,
                }
                storage.add(plane_dict)
                count += 1
            print(f"Сохранено {count} самолётов в {storage.file_path}")

        elif choice == "5":
            stored = storage.get_all()
            if not stored:
                print("Хранилище пусто.")
            else:
                print(f"Всего записей в хранилище: {len(stored)}")
                # Покажем последние 10
                for rec in stored[-10:]:
                    callsign = rec.get("callsign", "N/A")
                    country = rec.get("origin_country", "?")
                    alt = rec.get("altitude")
                    alt_str = f"{alt:.0f}" if alt is not None else "—"
                    print(f"  - {callsign} ({country}) – высота {alt_str} м")

        elif choice == "6":
            confirm = input("Удалить все данные из JSON-файла? (y/n): ")
            if confirm.lower() == "y":
                deleted = storage.delete(lambda _: True)
                print(f"Удалено записей: {deleted}")
            else:
                print("Операция отменена.")

        else:
            print("Неверный выбор. Пожалуйста, введите цифру от 0 до 6.")


current_aeroplanes = []  # Глобальная переменная для хранения последних полученных самолётов
