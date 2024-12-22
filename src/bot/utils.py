import logging

from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)


def save_state(
    context: CallbackContext,
    state: str,
    message_text: str,
    reply_markup: InlineKeyboardMarkup,
    handler_name: str = None,
) -> None:
    """
    Сохраняет текущее состояние пользователя.

    :param context: Контекст вызова, содержащий данные пользователя.
    :param state: Строка, описывающая текущее состояние пользователя.
    :param message_text: Текст сообщения, связанного с текущим состоянием.
    :param reply_markup: Разметка клавиатуры, связанная с текущим состоянием.
    :param handler_name: Название обработчика, который вызвал состояние.
    :return: None
    """
    user_id = context.user_data.get("user_id", "неизвестен")

    # Проверка на дублирующее состояние
    if "history" in context.user_data and context.user_data["history"]:
        last_state = context.user_data["history"][-1]
        if (
            last_state["state"] == state
            and last_state["message_text"] == message_text
        ):
            logger.info(
                f"Пользователь {user_id} пытается сохранить "
                f"дублирующее состояние, пропускаем."
            )
            return

    logger.info(
        f"Пользователь {user_id} сохраняет состояние: {state}, "
        f"с сообщением: {message_text}"
    )

    # Сохранение состояния в историю пользователя
    if "history" not in context.user_data:
        context.user_data["history"] = []

    context.user_data["history"].append(
        {
            "state": state,
            "message_text": message_text,
            "reply_markup": reply_markup,
            "handler_name": handler_name,
        }
    )


def load_previous_state(context: CallbackContext) -> dict | None:
    """
    Загружает предыдущее сохраненное состояние пользователя.

    :param context: Контекст вызова, содержащий данные пользователя.
    :return: Последнее сохраненное состояние
    пользователя или None, если состояние не найдено.
    """
    user_id = context.user_data.get("user_id", "неизвестен")

    if (
        "history" in context.user_data
        and len(context.user_data["history"]) > 1
    ):
        # Извлекаем текущее состояние (удаляем его)
        current_state = context.user_data["history"].pop()
        logger.info(f"Текущее состояние {current_state}")
        # Загружаем предыдущее состояние
        previous_state = context.user_data["history"][-1]

        logger.info(
            f"Пользователь {user_id} загружает предыдущее "
            f"состояние: {previous_state}"
        )
        return previous_state

    logger.info(
        f"Пользователь {user_id} пытается загрузить"
        f" предыдущее состояние, "
        f"но история слишком мала."
    )
    return None


def clear_pagination_state(context: CallbackContext) -> None:
    """
    Очищает состояние пагинации пользователя.

    :param context: Контекст вызова, содержащий данные пользователя.
    :return: None
    """
    if "pagination" in context.user_data:
        del context.user_data["pagination"]
        logger.info("Состояние пагинации очищено.")
