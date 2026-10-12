import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.core import create_table, delete, drop_table, insert, select, update
from primitive_db.parser import parse_condition, parse_list
from primitive_db.utils import (
    create_cacher,
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> ... - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, ...) - создать запись"
    )
    print(
        "<command> select from <имя_таблицы> "
        "where <столбец> = <значение> - найти записи"
    )
    print("<command> select from <имя_таблицы> - показать все записи")
    print(
        "<command> update <имя_таблицы> set <столбец> = <значение> "
        "where <столбец> = <значение> - обновить запись"
    )
    print(
        "<command> delete from <имя_таблицы> "
        "where <столбец> = <значение> - удалить запись"
    )
    print("<command> info <имя_таблицы> - информация о таблице")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    print_help()
    cache_result = create_cacher()

    while True:
        metadata = load_metadata("db_meta.json")
        user_input = prompt.string("Введите команду: ")

        if user_input is None:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0]

        if command == "exit":
            if len(args) != 1:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue
            break

        elif command == "help":
            if len(args) != 1:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue
            print_help()

        elif command == "list_tables":
            if len(args) != 1:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue
            for table_name in metadata:
                print(f"- {table_name}")

        elif command == "create_table":
            if len(args) < 3:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = args[1]
            if (
                not table_name
                or not table_name.isascii()
                or not all(char.isalnum() or char == "_" for char in table_name)
            ):
                print(f"Некорректное значение: {table_name}. Попробуйте снова.")
                continue

            columns = args[2:]

            result = create_table(metadata, table_name, columns)

            if result is not None:
                save_metadata("db_meta.json", result)
                cache_result(None, None)

        elif command == "drop_table":
            if len(args) != 2:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = args[1]

            result = drop_table(metadata, table_name)

            if result is not None:
                save_metadata("db_meta.json", result)
                delete_table_data(table_name)
                cache_result(None, None)

        elif command == "insert":
            parts = user_input.split(maxsplit=4)

            if len(parts) != 5 or parts[1] != "into" or parts[3] != "values":
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = parts[2]

            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            try:
                values = parse_list(parts[4])
            except ValueError as error:
                print(error)
                continue

            table_data = insert(metadata, table_name, values)

            if table_data is not None:
                save_table_data(table_name, table_data)
                cache_result(None, None)

        elif command == "select":
            parts = user_input.split(maxsplit=4)

            if len(parts) < 3 or parts[1] != "from":
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = parts[2]

            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            where_clause = None

            if len(parts) > 3:
                if len(parts) != 5 or parts[3] != "where":
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue

                try:
                    where_clause = parse_condition(parts[4])
                except ValueError as error:
                    print(error)
                    continue

                name = next(iter(where_clause))

                if name not in metadata[table_name]:
                    print(f"Некорректное значение: {name}. Попробуйте снова.")
                    continue

                value = where_clause[name]

                types = {
                    "int": int,
                    "str": str,
                    "bool": bool,
                }

                if type(value) is not types[metadata[table_name][name]]:
                    print(f"Некорректное значение: {value}. Попробуйте снова.")
                    continue

            key = (
                table_name,
                tuple(sorted(where_clause.items())) if where_clause else None,
            )

            result = cache_result(
                key,
                lambda: select(load_table_data(table_name), where_clause),
            )

            if result is None:
                continue

            table = PrettyTable()
            table.field_names = list(metadata[table_name].keys())

            for row in result:
                table.add_row([row[name] for name in table.field_names])

            print(table)

        elif command == "update":
            parts = user_input.split(maxsplit=3)

            if len(parts) != 4 or parts[2] != "set" or " where " not in parts[3]:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = parts[1]

            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            set_text, where_text = parts[3].split(" where ", 1)

            try:
                set_clause = parse_condition(set_text)
                where_clause = parse_condition(where_text)
            except ValueError as error:
                print(error)
                continue

            set_name = next(iter(set_clause))
            where_name = next(iter(where_clause))

            if (
                set_name not in metadata[table_name]
                or where_name not in metadata[table_name]
                or set_name == "ID"
            ):
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            set_value = set_clause[set_name]
            where_value = where_clause[where_name]

            types = {
                "int": int,
                "str": str,
                "bool": bool,
            }

            if (
                type(set_value) is not types[metadata[table_name][set_name]]
                or type(where_value) is not types[metadata[table_name][where_name]]
            ):
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_data = load_table_data(table_name)
            result = update(table_data, set_clause, where_clause)

            if result is None:
                continue

            save_table_data(table_name, result)
            cache_result(None, None)

            for old_row, new_row in zip(table_data, result):
                if old_row != new_row:
                    print(
                        f"Запись с ID={new_row['ID']} в таблице "
                        f'"{table_name}" успешно обновлена.'
                    )

        elif command == "delete":
            parts = user_input.split(maxsplit=4)

            if len(parts) != 5 or parts[1] != "from" or parts[3] != "where":
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = parts[2]

            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            try:
                where_clause = parse_condition(parts[4])
            except ValueError as error:
                print(error)
                continue

            name = next(iter(where_clause))
            value = where_clause[name]

            if name not in metadata[table_name]:
                print(f"Некорректное значение: {name}. Попробуйте снова.")
                continue

            types = {"int": int, "str": str, "bool": bool}

            if type(value) is not types[metadata[table_name][name]]:
                print(f"Некорректное значение: {value}. Попробуйте снова.")
                continue

            table_data = load_table_data(table_name)
            result = delete(table_data, where_clause)

            if result is None:
                continue

            save_table_data(table_name, result)
            cache_result(None, None)

            for row in table_data:
                if row not in result:
                    print(
                        f"Запись с ID={row['ID']} успешно удалена "
                        f'из таблицы "{table_name}".'
                    )

        elif command == "info":
            if len(args) != 2:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = args[1]

            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            columns = metadata[table_name]
            table_data = load_table_data(table_name)

            print(f"Таблица: {table_name}")
            print(
                "Столбцы: "
                + ", ".join(
                    f"{name}:{data_type}" for name, data_type in columns.items()
                )
            )
            print(f"Количество записей: {len(table_data)}")

        else:
            print(f"Функции {command} нет. Попробуйте снова.")
