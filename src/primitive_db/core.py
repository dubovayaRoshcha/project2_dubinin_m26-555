from primitive_db.utils import load_table_data


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

    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        + ", ".join(f"{name}:{data_type}" for name, data_type in table_columns.items())
    )

    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    metadata.pop(table_name)

    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def insert(metadata, table_name, values):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    columns = list(metadata[table_name].items())[1:]

    if len(values) != len(columns):
        print(f"Некорректное значение: {values}. Попробуйте снова.")
        return None

    table_data = load_table_data(table_name)

    for column, value in zip(columns, values):
        data_type = column[1]

        if data_type == "int" and type(value) is not int:
            print(f"Некорректное значение: {value}. Попробуйте снова.")
            return None

        if data_type == "str" and type(value) is not str:
            print(f"Некорректное значение: {value}. Попробуйте снова.")
            return None

        if data_type == "bool" and type(value) is not bool:
            print(f"Некорректное значение: {value}. Попробуйте снова.")
            return None

    new_id = max((row["ID"] for row in table_data), default=0) + 1

    record = {"ID": new_id}

    for column, value in zip(columns, values):
        record[column[0]] = value

    table_data.append(record)

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')

    return table_data


def select(table_data, where_clause=None):
    if where_clause is None:
        return table_data

    result = []

    for row in table_data:
        for name, value in where_clause.items():
            if row.get(name) == value:
                result.append(row)

    return result


def update(table_data, set_clause, where_clause):
    result = []

    for row in table_data:
        new_row = row.copy()

        for name, value in where_clause.items():
            if row.get(name) == value:
                new_row.update(set_clause)

        result.append(new_row)

    return result


def delete(table_data, where_clause):
    result = []

    for row in table_data:
        should_delete = False

        for name, value in where_clause.items():
            if row.get(name) == value:
                should_delete = True

        if not should_delete:
            result.append(row)

    return result
