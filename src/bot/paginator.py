import re

from telegram import InlineKeyboardButton

from bot.variables import HANDLE_PAGINATOR_PATTERN, ITEMS_PER_PAGE, STATE_NAMES


# Функция для получения названия по номеру
def get_state_name(state_number: int) -> str:
    """Возвращает название состояния по его номеру."""
    if 0 <= state_number < len(STATE_NAMES):
        return STATE_NAMES[state_number]
    return "Неизвестное состояние"


def get_total_pages(list_total_elements: list) -> int:
    """Возвращает общее число страниц пагинации."""
    return (len(list_total_elements) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE


def get_list_values_from_list_dicts(list: list) -> list:
    """Возвращает список значений из списка словарей."""
    list_values = []
    for dict in list:
        if dict["label"]:
            list_values.append(dict["label"])
    return list_values


def get_current_elements(page: int, list_total_elements: list) -> list:
    """Возвращает список элементов для текущей страницы пагинации."""
    start_index = page * ITEMS_PER_PAGE
    end_index = min(start_index + ITEMS_PER_PAGE, len(list_total_elements))
    return list_total_elements[start_index:end_index]


def get_paginator_buttons(page: int, total_pages: int) -> list:
    """Возвращает кнопки пагинации для запрошенного параметра."""
    paginator_buttons = []

    if page > 0:
        paginator_buttons.append(
            InlineKeyboardButton(
                "Предыдущая", callback_data=f"prev_{page - 1}"
            )
        )

    paginator_buttons.append(
        InlineKeyboardButton(
            f"{page + 1} из {total_pages} стр.", callback_data="no_answer"
        )
    )

    if page < total_pages - 1:
        paginator_buttons.append(
            InlineKeyboardButton("Следующая", callback_data=f"next_{page + 1}")
        )

    if total_pages == 1:
        paginator_buttons.clear()

    return paginator_buttons


def check_string(input_string: str, selected_param_name: str = None) -> str:
    """Проверяет, находится ли пользователь внутри пагинатора/мн.выбора."""
    if (
        not re.match(HANDLE_PAGINATOR_PATTERN, input_string)
        and (not re.match(r"^multiple", input_string))
        and (not re.match(r"^step-forward", input_string))
    ):
        return input_string.split("_")[-1]

    return selected_param_name


def create_paginator_dict() -> dict:
    """Создает словарь для пагинации."""
    return {
        "current_page": 0,
        "name_parameter": None,
    }


def get_current_page_check(
    context_name_parametr: str,
    current_name_parametr: str,
    context_current_page: int,
) -> int:
    """Проверяет, был ли переход к другому параметру."""
    if context_name_parametr != current_name_parametr:
        return 0

    return context_current_page


def update_paginator_dict(state: int) -> dict:
    """Обновляет словарь пагинации при возврате к предыдущему состоянию."""
    return {
        "current_page": 0,
        "name_parameter": get_state_name(state),
    }


def get_paginator_elements(
    pagination_dict, state, list_elements
) -> tuple[list, list, dict]:
    """Формирует данные для пагинации: элементы, кнопки и словарь контекста."""
    list_total_elements = get_list_values_from_list_dicts(list_elements)
    func_name = get_state_name(state)
    current_page = get_current_page_check(
        pagination_dict["name_parameter"],
        func_name,
        pagination_dict["current_page"],
    )
    current_elements = get_current_elements(current_page, list_total_elements)

    pagination_dict["name_parameter"] = func_name
    pagination_dict["current_page"] = current_page

    paginator_buttons = get_paginator_buttons(
        current_page,
        get_total_pages(list_total_elements),
    )

    return current_elements, paginator_buttons, pagination_dict


def check_paginator(input_string: str) -> bool:
    """Сверяет строку с шаблоном пагинатора."""
    return re.match(HANDLE_PAGINATOR_PATTERN, input_string)
