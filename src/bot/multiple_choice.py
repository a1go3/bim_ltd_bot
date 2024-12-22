from telegram import InlineKeyboardButton


def clear_multiple_dict(
    multiple_dict: dict[int, dict[str, bool]], state: int
) -> dict[int, dict[str, bool]]:
    """Удаление состояний мн.выбора, которые позже текущего состояния."""
    for key, value in multiple_dict.items():
        if key >= state:
            multiple_dict.pop(key)
    return multiple_dict


def get_selected_values(dict: dict[str, bool]) -> list[str]:
    """Получает список выбранных элементов из словаря."""
    selected_values = []
    for key, value in dict.items():
        if value:
            selected_values.append(key)
    return selected_values


def get_selected_dict(
    multiple_dict: dict[int, dict[str, bool]], state: int
) -> dict[int, list[str]]:
    """Создает словарь выбранных значений для мн. выбора."""
    selected_dict = {}
    for key, value in multiple_dict.items():
        if key < state:
            selected_dict[key] = get_selected_values(value)
    return selected_dict


def update_multiple_dict(
    multiple_dict: dict[int, dict[str, bool]], state: int, param: str = None
) -> dict[int, dict[str, bool]]:
    """Обновляет словарь множественного выбора."""
    multiple_dict[state] = multiple_dict.get(state, {})
    if param:
        multiple_dict[state][param] = not multiple_dict[state].get(
            param, False
        )
    else:
        multiple_dict[state] = {}
    return multiple_dict


def check_multi_dict(
    multiple_dict: dict[int, dict[str, bool]], param: str
) -> bool:
    """Проверяет наличие ключа в словаре."""
    return param in multiple_dict


def check_elem_not_dict(elem) -> str:
    """Возвращает значение по ключу если словарь."""
    return str(elem["label"] if isinstance(elem, dict) else elem)


def check_marked_button(
    elem: str, m_dict: dict[int, dict[str, bool]], state: int
) -> str:
    """Формирует отметку на кнопке мн.выбора."""
    if state in m_dict:
        params = m_dict[state]
        return (
            f"{'✅ ' if (elem in params and params[elem]) else ''}" f"{elem}"
        )
    else:
        return f"{elem}"


def get_multiple_elem_buttons(
    multiple_dict: dict[int, dict[str, bool]],
    session_key: str,
    current_elements: list,
    state: int,
) -> list[InlineKeyboardButton]:
    """Формирует кнопки мн.выбора."""
    return [
        [
            InlineKeyboardButton(
                check_marked_button(
                    check_elem_not_dict(elem), multiple_dict, state
                ),
                callback_data=(
                    f"multiple_{session_key}_" f"{check_elem_not_dict(elem)}"
                ),
            )
        ]
        for elem in current_elements
    ]


def get_next_step_button() -> list[InlineKeyboardButton]:
    """Формирует кнопку перехода к следующему шагу."""
    return [
        InlineKeyboardButton(
            "Применить выбор и перейти далее", callback_data=("step-forward")
        ),
    ]
