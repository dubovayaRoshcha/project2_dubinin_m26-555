from primitive_db.constants import VALID_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.utils import load_table_data


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу и добавляет её в метаданные"""
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    table_columns = {"ID": "int"}

    for column in columns:
        parts = column.split(":")

        if len(parts) != 2:
            raise ValueError(f"Некорректное значение: {column}")

        name, data_type = parts

        if data_type not in VALID_TYPES:
            raise ValueError(f"Некорректное значение: {data_type}")

        if not name or name in table_columns:
            raise ValueError(f"Некорректное значение: {column}")

        table_columns[name] = data_type

    metadata[table_name] = table_columns

    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        + ", ".join(f"{name}:{data_type}" for name, data_type in table_columns.items())
    )

    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных после подтверждения"""
    if table_name not in metadata:
        raise KeyError(table_name)

    metadata.pop(table_name)

    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Проверяет значения и добавляет запись с автоматически созданным ID"""
    if table_name not in metadata:
        raise KeyError(table_name)

    columns = list(metadata[table_name].items())[1:]

    if len(values) != len(columns):
        raise ValueError(f"Некорректное количество значений: {len(values)}")

    table_data = load_table_data(table_name)

    for column, value in zip(columns, values):
        data_type = column[1]

        if data_type == "int" and type(value) is not int:
            raise ValueError(f"Некорректное значение: {value}")

        if data_type == "str" and type(value) is not str:
            raise ValueError(f"Некорректное значение: {value}")

        if data_type == "bool" and type(value) is not bool:
            raise ValueError(f"Некорректное значение: {value}")

    new_id = max((row["ID"] for row in table_data), default=0) + 1

    record = {"ID": new_id}

    for column, value in zip(columns, values):
        record[column[0]] = value

    table_data.append(record)

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')

    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает все записи или записи, соответствующие условию"""
    if where_clause is None:
        return table_data

    result = []

    for row in table_data:
        for name, value in where_clause.items():
            if row.get(name) == value:
                result.append(row)

    return result


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет поля записей, удовлетворяющих условию"""
    result = []

    for row in table_data:
        new_row = row.copy()

        for name, value in where_clause.items():
            if row.get(name) == value:
                new_row.update(set_clause)

        result.append(new_row)

    return result


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    """Удаляет подходящие записи после подтверждения"""
    result = []

    for row in table_data:
        should_delete = False

        for name, value in where_clause.items():
            if row.get(name) == value:
                should_delete = True

        if not should_delete:
            result.append(row)

    return result
