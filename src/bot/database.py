import logging

from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.variables import FILTER_STEPS_DATA

logger = logging.getLogger(__name__)


def get_valid_min_max_from_range(value: str) -> tuple[float, float]:
    """Проверяет, является ли строка корректным диапазоном."""
    if " - " in value:
        try:
            value_min, value_max = value.split(" - ")
            return float(value_min), float(value_max)
        except ValueError as e:
            logger.error(
                (
                    f"Ошибка при разбиении значения диапазона: "
                    f"{value}. Ошибка: {e}"
                )
            )
    else:
        logger.error(f"Некорректный формат значения диапазона: {value}")
        raise ValueError(f"Некорректный формат значения диапазона: {value}")


async def fetch_data_from_db(
    session: AsyncSession,
    selected_values: dict[int:list],
    current_step_number: int,
) -> dict:
    """
    Возвращает результат запроса к базе по настройкам отбора.

    :param session: Асинхронная сессия SQLAlchemy
    :param selected_values: Словарь с ключами по номерам этапов
    и значениями в виде списков выбранных значений на каждом этапе.
    :param current_step_number: Номер текущего этапа.
    """
    current_step: int = FILTER_STEPS_DATA[current_step_number]
    button_fields: list = current_step["button_fields"]
    # Генерация SQL-запроса
    stmt = await get_sql_statment(
        FILTER_STEPS_DATA, selected_values, current_step_number
    )
    try:
        result = await session.execute(stmt)
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса: {e}")
        raise

    buttons: list = []
    rows: list = result.fetchall()

    if not rows:
        logger.warning(
            (
                f"Данные не найдены на шаге {current_step_number} "
                f"с выбранными значениями: {selected_values}"
            )
        )
        return {
            "message_text": (
                "К сожалению, данные не найдены. "
                "Попробуйте изменить критерии отбора."
            ),
            "buttons": [],
        }
    for row in rows:
        button: dict = {}
        if not current_step["by_range"]:
            for digit in range(len(button_fields)):
                button[button_fields[digit]] = row[digit]
        else:
            values_range: float = current_step["range"]
            values_range_step: float = current_step["range_step"]
            digits_after_dot: int = current_step["digits_after_dot"]
            full_range: float = values_range + values_range_step

            if row[0] is not None:
                value_range_position: int = row[0] // full_range
            else:
                value_range_position = 0

            range_result = " ".join(
                (
                    str(
                        round(
                            value_range_position * full_range, digits_after_dot
                        )
                    ),
                    "-",
                    str(value_range_position * full_range + values_range),
                )
            )

            if range_result not in buttons:
                for digit in range(len(button_fields)):
                    button[button_fields[digit]] = range_result

        buttons.append(button)

    result_dict: dict = {
        "message_text": current_step["message_text"],
        "buttons": buttons,
    }

    logger.info(
        f"Данные успешно получены на шаге {current_step_number}: {result_dict}"
    )
    return result_dict


async def get_sql_statment(
    filter_data: dict, selected_values: list, current_step_number: int
) -> Select:
    """Возвращает запрос к базе по настройкам отбора."""
    current_step: int = filter_data[current_step_number]
    query_fields: list = current_step["query_fields"]
    group_fields: list = current_step["group_fields"]
    order_fields: list = current_step["order_fields"]
    join_fields: list = current_step["join_fields"]

    stmt: Select = select(*query_fields)

    if group_fields:
        stmt = stmt.group_by(*group_fields)
    if order_fields:
        stmt = stmt.order_by(*order_fields)
    if join_fields:
        stmt = stmt.join(*join_fields)

    for step_number, filter_step in filter_data.items():
        if step_number >= current_step_number:
            break
        values: list = selected_values.get(step_number)

        if not values:
            continue

        if filter_step["join_fields"]:
            stmt = stmt.join(*filter_step["join_fields"])

        stmt = await get_sql_statment_with_conditions(
            stmt, filter_step, values
        )
    return stmt


async def get_sql_statment_with_conditions(
    stmt: Select, filter_step: dict, values: list
) -> Select:
    """Добавляет условия по настройкам этапа отбора."""
    if not filter_step["by_range"]:
        # Для полей, где не нужно учитывать диапазон значений
        return stmt.where(filter_step["where_field"].in_(values))
        # Если используется диапазон
    else:
        conditions: list = []
        for value in values:
            value_min, value_max = get_valid_min_max_from_range(value)
            conditions.append(
                filter_step["where_field"].between(
                    float(value_min), float(value_max)
                )
            )
        if conditions:
            return stmt.where(or_(*conditions))
    return stmt
