def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    table_columns = {"ID": "int"}

    for column in columns:
        parts = column.split(":")

        if len(parts) != 2:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        name, data_type = parts

        if data_type not in ("int", "str", "bool"):
            print(f"Некорректное значение: {data_type}. Попробуйте снова.")
            return metadata

        if not name or name in table_columns:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        table_columns[name] = data_type

    metadata[table_name] = table_columns

    print(f'Таблица "{table_name}" успешно создана со столбцами: '
        + ", ".join(f"{name}:{data_type}" for name, data_type in table_columns.items()))

    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    metadata.pop(table_name)

    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata