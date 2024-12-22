import logging

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
)

from bot.handlers import (
    handle_back,
    handle_no_answer,
    handle_pagination,
    handle_start,
    handle_step_forward,
    select_brand,
    select_category,
    select_model,
    select_power,
    select_type,
    show_about,
    show_model_info,
    start,
)
from bot.variables import (
    SELECT_BRAND,
    SELECT_CATEGORY,
    SELECT_MODEL,
    SELECT_POWER,
    SELECT_TYPE,
    SHOW_RESULT,
)
from db.config import LOG_FORMAT, settings

logging.basicConfig(
    format=LOG_FORMAT,
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


application = Application.builder().token(settings.BOT_TOKEN).build()


async def setup_handlers():
    """
    Настраивает обработчики команд и событий для Telegram бота.

    Использует ConversationHandler для управления состояниями диалогов.
    """
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_CATEGORY: [
                CallbackQueryHandler(show_about, pattern="^about$"),
                CallbackQueryHandler(
                    select_category, pattern="^select-category$"
                ),
                CallbackQueryHandler(handle_back, pattern="^back$"),
                CallbackQueryHandler(handle_start, pattern="^start$"),
                CallbackQueryHandler(
                    handle_pagination, pattern="^(prev|next)_[0-9]+$"
                ),
                CallbackQueryHandler(handle_no_answer, pattern="^no_answer$"),
                CallbackQueryHandler(select_category, pattern="^multiple"),
                CallbackQueryHandler(
                    handle_step_forward, pattern="^step-forward"
                ),
            ],
            SELECT_TYPE: [
                CallbackQueryHandler(select_type, pattern="^category_"),
                CallbackQueryHandler(handle_back, pattern="^back$"),
                CallbackQueryHandler(handle_start, pattern="^start$"),
                CallbackQueryHandler(
                    handle_pagination, pattern="^(prev|next)_[0-9]+$"
                ),
                CallbackQueryHandler(handle_no_answer, pattern="^no_answer$"),
                CallbackQueryHandler(select_type, pattern="^multiple"),
                CallbackQueryHandler(
                    handle_step_forward, pattern="^step-forward"
                ),
            ],
            SELECT_POWER: [
                CallbackQueryHandler(select_power, pattern="^type_"),
                CallbackQueryHandler(handle_back, pattern="^back$"),
                CallbackQueryHandler(handle_start, pattern="^start$"),
                CallbackQueryHandler(
                    handle_pagination, pattern="^(prev|next)_[0-9]+$"
                ),
                CallbackQueryHandler(handle_no_answer, pattern="^no_answer$"),
                CallbackQueryHandler(select_power, pattern="^multiple"),
                CallbackQueryHandler(
                    handle_step_forward, pattern="^step-forward"
                ),
            ],
            SELECT_BRAND: [
                CallbackQueryHandler(select_brand, pattern="^power_"),
                CallbackQueryHandler(handle_back, pattern="^back$"),
                CallbackQueryHandler(handle_start, pattern="^start$"),
                CallbackQueryHandler(
                    handle_pagination, pattern="^(prev|next)_[0-9]+$"
                ),
                CallbackQueryHandler(handle_no_answer, pattern="^no_answer$"),
                CallbackQueryHandler(select_brand, pattern="^multiple"),
                CallbackQueryHandler(
                    handle_step_forward, pattern="^step-forward"
                ),
            ],
            SELECT_MODEL: [
                CallbackQueryHandler(select_model, pattern="^brand_"),
                CallbackQueryHandler(handle_back, pattern="^back$"),
                CallbackQueryHandler(handle_start, pattern="^start$"),
                CallbackQueryHandler(
                    handle_pagination, pattern="^(prev|next)_[0-9]+$"
                ),
                CallbackQueryHandler(handle_no_answer, pattern="^no_answer$"),
                CallbackQueryHandler(select_model, pattern="^multiple"),
                CallbackQueryHandler(
                    handle_step_forward, pattern="^step-forward"
                ),
            ],
            SHOW_RESULT: [
                CallbackQueryHandler(show_model_info, pattern="^model_"),
                CallbackQueryHandler(
                    select_category, pattern="^select-category$"
                ),
                CallbackQueryHandler(
                    handle_pagination, pattern="^(prev|next)_[0-9]+$"
                ),
                CallbackQueryHandler(handle_no_answer, pattern="^no_answer$"),
                CallbackQueryHandler(handle_start, pattern="^start$"),
                CallbackQueryHandler(handle_back, pattern="^back$"),
                CallbackQueryHandler(show_about, pattern="^about$"),
            ],
        },
        fallbacks=[CommandHandler("start", handle_start)],
    )
    application.add_handler(conv_handler)
