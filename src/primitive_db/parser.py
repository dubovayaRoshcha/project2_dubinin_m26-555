import shlex


def parse_value(value):
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Некорректное значение: {value}. Попробуйте снова.")


def parse_list(text):
    text = text.strip()

    if not text.startswith("(") or not text.endswith(")"):
        raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")

    text = text[1:-1]

    lexer = shlex.shlex(text, posix=False, punctuation_chars=",")
    lexer.whitespace_split = True

    items = list(lexer)

    result = []
    part = []

    for item in items:
        if item == ",":
            if len(part) != 1:
                raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")

            result.append(parse_value(part[0]))
            part = []
        else:
            part.append(item)

    if len(part) != 1:
        raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")

    result.append(parse_value(part[0]))

    return result


def parse_condition(text):
    parts = text.split("=", 1)

    if len(parts) != 2:
        raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")

    name = parts[0].strip()
    value = parts[1].strip()

    if not name or not value:
        raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")

    return {name: parse_value(value)}
