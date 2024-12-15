from aiogram import F
from aiogram.filters.callback_data import CallbackQueryFilter
from aiogram.types import InlineKeyboardButton
from my_app.bot.types.callbacks import ActionCallback, BaseCallback, MenuCallback


class BaseButtonInfo:
    def __init__(self, text: str, callback_data: BaseCallback):
        self.text = text
        self.callback_data = callback_data

    def __call__(self) -> CallbackQueryFilter:
        return CallbackQueryFilter(
            callback_data=self.callback_data.__class__,
            rule=F.action == self.callback_data.action,
        )

    def export(self) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=self.text, callback_data=self.callback_data.pack()
        )


class MenuButtonInfo(BaseButtonInfo):
    text: str
    callback_data: MenuCallback

    def __init__(self, text: str, callback_data: str):
        super().__init__(text, MenuCallback(action=callback_data))


class ActionButtonInfo(BaseButtonInfo):
    text: str
    callback_data: ActionCallback

    def __init__(self, text: str, callback_data: str):
        super().__init__(text, ActionCallback(action=callback_data))
