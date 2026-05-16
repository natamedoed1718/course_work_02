from src.aeroplane import Aeroplane
from src.aeroplanes_api import AeroplanesAPI
from src.json_storage import JSONStorage


def filter_aeroplanes_by_text(aeroplanes: list, search_text: str) -> list:
    """
    Фильтрует самолёты по тексту (ищет в стране регистрации или позывном).
    Поддерживает частичное совпадение и поиск по нескольким словам.
    """
    if not search_text:
        return aeroplanes

    search_words = search_text.lower().split()
    filtered = []

    for plane in aeroplanes:
        searchable_text = f"{plane.origin_country} {plane.callsign}".lower()
        if all(word in searchable_text for word in search_words):
            filtered.append(plane)

    return filtered


def get_top_by_altitude(aeroplanes: list, n: int) -> list:
    """
    Возвращает топ N самолётов по высоте полёта (от большей к меньшей).
    Самолёты с None высотой не включаются в топ.
    """
    if not aeroplanes:
        return []

    # Фильтруем самолёты, у которых есть высота
    planes_with_altitude = [p for p in aeroplanes if p.altitude is not None]

    # Сортируем по высоте (от большей к меньшей)
    sorted_planes = sorted(planes_with_altitude, key=lambda p: p.altitude, reverse=True)

    return sorted_planes[:n]


def user_interaction():
    """Основной цикл общения с пользователем через консоль."""
    print("Добро пожаловать в систему мониторинга самолётов")
    api = AeroplanesAPI()
    storage = JSONStorage()
    current_aeroplanes = []

    while True:
        print("\nВыберите действие:")
        print("1. Поискать самолёты над страной")
        print("2. Показать топ N самолётов по высоте")
        print("3. Найти самолёты по названию страны или позывному")
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
                    current_aeroplanes = Aeroplane.cast_to_object_list(raw_data)
                    print(f"Найдено самолётов: {len(current_aeroplanes)}")
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

                top_n = get_top_by_altitude(current_aeroplanes, n)
                print(f"\nТоп {n} самолётов по высоте (от большей к меньшей):")
                if not top_n:
                    print("Нет самолётов с данными о высоте.")
                for i, plane in enumerate(top_n, start=1):
                    alt_display = f"{plane.altitude:.0f} м"
                    print(f"{i:2d}. {plane.callsign} ({plane.origin_country}) – {alt_display}")
            except ValueError:
                print("Ошибка: введите целое число.")

        elif choice == "3":
            if not current_aeroplanes:
                print("Сначала выполните поиск (пункт 1).")
                continue

            search_text = input("Введите текст для поиска (страна или позывной): ").strip()
            if not search_text:
                print("Текст для поиска не введён.")
                continue

            filtered = filter_aeroplanes_by_text(current_aeroplanes, search_text)
            print(f"\nНайдено самолётов по запросу '{search_text}': {len(filtered)}")
            for plane in filtered[:20]:
                print(f"  - {plane}")
            if len(filtered) > 20:
                print("  ... (показаны первые 20)")

        elif choice == "4":
            if not current_aeroplanes:
                print("Нет данных для сохранения. Сначала выполните поиск (пункт 1).")
                continue
            count = 0
            for plane in current_aeroplanes:
                if storage.add_aeroplane(plane):
                    count += 1
            print(f"Сохранено {count} самолётов в {storage.file_path}")

        elif choice == "5":
            stored_planes = storage.get_aeroplanes()
            if not stored_planes:
                print("Хранилище пусто.")
            else:
                print(f"Всего записей в хранилище: {len(stored_planes)}")
                for plane in stored_planes[-10:]:
                    print(f"  - {plane}")

        elif choice == "6":
            confirm = input("Удалить все данные из JSON-файла? (y/n): ")
            if confirm.lower() == "y":
                storage.clear_all()
                print("Хранилище очищено")
            else:
                print("Операция отменена.")

        else:
            print("Неверный выбор. Пожалуйста, введите цифру от 0 до 6.")
