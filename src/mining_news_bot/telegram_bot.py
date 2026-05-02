from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from mining_news_bot.database import Database
from mining_news_bot.settings import Settings


def build_moderation_keyboard(draft_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Опубликовать", callback_data=f"publish:{draft_id}"),
                InlineKeyboardButton("Отклонить", callback_data=f"reject:{draft_id}"),
            ]
        ]
    )


async def send_draft_to_moderator(
    application: Application,
    moderator_chat_id: int,
    draft_id: int,
    draft_text: str,
) -> None:
    await application.bot.send_message(
        chat_id=moderator_chat_id,
        text=draft_text,
        reply_markup=build_moderation_keyboard(draft_id),
        disable_web_page_preview=False,
    )


def build_callback_handler(settings: Settings, database: Database) -> CallbackQueryHandler:
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if query is None or query.data is None:
            return
        await query.answer()
        action, raw_draft_id = query.data.split(":", 1)
        draft_id = int(raw_draft_id)
        draft = database.get_draft(draft_id)
        if draft is None:
            await query.edit_message_text("Черновик не найден.")
            return
        if action == "publish":
            message = await context.bot.send_message(
                chat_id=settings.telegram_channel_id,
                text=draft["draft_text"],
                disable_web_page_preview=False,
            )
            database.mark_published(draft_id, message.message_id)
            await query.edit_message_text(f"Опубликовано:\n\n{draft['draft_text']}")
        elif action == "reject":
            database.mark_rejected(draft_id)
            await query.edit_message_text(f"Отклонено:\n\n{draft['draft_text']}")

    return CallbackQueryHandler(handle_callback)
