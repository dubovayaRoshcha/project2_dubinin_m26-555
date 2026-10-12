import json
import os


def load_metadata(filepath):
    """Загружает метаданные таблиц из JSON-файла"""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет метаданные таблиц в JSON-файл"""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_table_data(table_name):
    """Загружает записи таблицы из JSON-файла"""
    filepath = f"data/{table_name}.json"

    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет записи таблицы в JSON-файл"""
    os.makedirs("data", exist_ok=True)

    filepath = f"data/{table_name}.json"

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def delete_table_data(table_name):
    """Удаляет JSON-файл с данными таблицы"""
    filepath = f"data/{table_name}.json"

    if os.path.exists(filepath):
        os.remove(filepath)


def create_cacher():
    """Создаёт замыкание для кэширования результатов по ключу"""
    cache = {}

    def cache_result(key, value_func):
        """Возвращает результат из кэша или вычисляет и сохраняет его"""
        if key is None:
            cache.clear()
            return None

        if key in cache:
            return cache[key]

        result = value_func()
        cache[key] = result
        return result

    return cache_result
