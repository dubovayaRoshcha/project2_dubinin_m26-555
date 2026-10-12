import time


def handle_db_errors(func):
    """Перехватывает исключения и выводит сообщения об ошибках"""

    def wrapper(*args, **kwargs):
        """Вызывает функцию с обработкой исключений"""
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

    return wrapper


def confirm_action(action_name):
    """Создаёт декоратор для подтверждения опасных операций"""

    def decorator(func):
        """Оборачивает функцию проверкой подтверждения"""

        def wrapper(*args, **kwargs):
            """Запрашивает подтверждение перед выполнением функции"""
            answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')

            if answer != "y":
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Создаёт обёртку для измерения времени выполнения функции"""

    def wrapper(*args, **kwargs):
        """Замеряет время выполнения и возвращает результат функции"""
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()

        print(f"Функция {func.__name__} выполнилась за {end - start:.3f} секунд")
        return result

    return wrapper
