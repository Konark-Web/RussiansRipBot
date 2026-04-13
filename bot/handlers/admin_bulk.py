import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.config_loader import Config
from bot.keyboards import admin_bulk_review_keyboard
from bot.services.bulk_messaging_service import BulkMessagingService, OutgoingBroadcastPayload

log = logging.getLogger(__name__)


class AdminBulkStates(StatesGroup):
    waiting_content = State()
    confirming = State()


class AdminBulkHandler:
    def __init__(self, bulk_service: BulkMessagingService, config: Config):
        self._bulk_service = bulk_service
        self._config = config

    def _is_admin(self, message: types.Message) -> bool:
        return message.from_user and message.from_user.id == self._config.admin_telegram_user_id

    def _is_admin_callback(self, call: types.CallbackQuery) -> bool:
        return call.from_user and call.from_user.id == self._config.admin_telegram_user_id

    async def send_message_cmd(self, message: types.Message, state: FSMContext):
        if not self._is_admin(message):
            return
        await state.finish()
        await message.answer(
            "Надішліть <b>текст</b> або <b>фото з підписом</b> (підтримується HTML). "
            "Після цього ви зможете отримати тестову копію в особисті й лише потім розіслати всім.",
            parse_mode="HTML",
        )
        await AdminBulkStates.waiting_content.set()

    async def admin_bulk_receive_content(self, message: types.Message, state: FSMContext):
        if not self._is_admin(message):
            return

        photo_file_id = None
        text = ""
        if message.photo:
            photo_file_id = message.photo[-1].file_id
            text = message.caption or ""
        elif message.text:
            text = message.text
        else:
            await message.answer("Надішліть текст або фото (можна лише фото, але краще з підписом).")
            return

        if not photo_file_id and not (text and text.strip()):
            await message.answer("Потрібен непорожній текст або фото.")
            return

        await state.update_data(text_html=text, photo_file_id=photo_file_id)
        await AdminBulkStates.confirming.set()
        await message.answer(
            "Контент прийнято. Перевірте попереднє повідомлення. Далі оберіть дію:",
            reply_markup=admin_bulk_review_keyboard(),
        )

    async def admin_bulk_test(self, call: types.CallbackQuery, state: FSMContext):
        if not self._is_admin_callback(call):
            await call.answer("Немає доступу", show_alert=True)
            return

        current = await state.get_state()
        if current != AdminBulkStates.confirming.state:
            await call.answer("Спочатку надішліть повідомлення через /send_message", show_alert=True)
            return

        data = await state.get_data()
        payload = OutgoingBroadcastPayload(
            text_html=data.get("text_html") or "",
            photo_file_id=data.get("photo_file_id"),
        )
        try:
            await self._bulk_service.send_to_recipient(call.bot, self._config.admin_telegram_user_id, payload)
        except Exception:
            log.exception("admin test send failed")
            await call.answer("Помилка відправки тесту", show_alert=True)
            return

        await call.answer("Тест надіслано вам в особисті")

    async def _run_bulk_broadcast(
        self,
        bot: Bot,
        admin_id: int,
        payload: OutgoingBroadcastPayload,
    ):
        try:
            await self._bulk_service.broadcast_to_all_active(bot, payload)
        except Exception:
            log.exception("bulk broadcast failed")
            try:
                await bot.send_message(
                    admin_id,
                    "Під час масової розсилки сталася помилка (деталі в логах).",
                )
            except Exception:
                log.exception("failed to notify admin about bulk error")
            return
        try:
            await bot.send_message(admin_id, "Масове повідомлення надіслано.")
        except Exception:
            log.exception("failed to notify admin about bulk success")

    async def admin_bulk_send(self, call: types.CallbackQuery, state: FSMContext):
        if not self._is_admin_callback(call):
            await call.answer("Немає доступу", show_alert=True)
            return

        current = await state.get_state()
        if current != AdminBulkStates.confirming.state:
            await call.answer("Немає активного повідомлення для розсилки", show_alert=True)
            return

        data = await state.get_data()
        payload = OutgoingBroadcastPayload(
            text_html=data.get("text_html") or "",
            photo_file_id=data.get("photo_file_id"),
        )
        await call.answer("Розсилка запущена")
        await call.message.edit_reply_markup(reply_markup=None)
        await state.finish()
        asyncio.create_task(
            self._run_bulk_broadcast(
                call.bot, self._config.admin_telegram_user_id, payload
            )
        )

    async def admin_bulk_cancel(self, call: types.CallbackQuery, state: FSMContext):
        if not self._is_admin_callback(call):
            await call.answer("Немає доступу", show_alert=True)
            return

        await state.finish()
        await call.answer("Скасовано")
        await call.message.edit_reply_markup(reply_markup=None)


def register_admin_bulk(dp: Dispatcher, bulk_service: BulkMessagingService, config: Config):
    handler = AdminBulkHandler(bulk_service, config)

    dp.register_message_handler(
        handler.send_message_cmd,
        chat_type=types.ChatType.PRIVATE,
        commands="send_message",
    )
    dp.register_message_handler(
        handler.admin_bulk_receive_content,
        chat_type=types.ChatType.PRIVATE,
        state=AdminBulkStates.waiting_content,
        content_types=types.ContentTypes.ANY,
    )
    dp.register_callback_query_handler(
        handler.admin_bulk_test,
        lambda c: c.data == "adm_bulk:test",
        chat_type=types.ChatType.PRIVATE,
    )
    dp.register_callback_query_handler(
        handler.admin_bulk_send,
        lambda c: c.data == "adm_bulk:send",
        chat_type=types.ChatType.PRIVATE,
    )
    dp.register_callback_query_handler(
        handler.admin_bulk_cancel,
        lambda c: c.data == "adm_bulk:cancel",
        chat_type=types.ChatType.PRIVATE,
    )
