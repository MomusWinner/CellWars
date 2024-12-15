from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class GameMessage:
    info: str
    actions: list[list[InlineKeyboardButton]]
    field: list[list[InlineKeyboardButton]]

    def __init__(
        self,
        info: str | None,
        actions: list[list[InlineKeyboardButton]] | None,
        field: list[list[InlineKeyboardButton]] | None,
    ):
        self.info = info if info else ""
        self.actions = actions if actions else []
        self.field = field if field else []

    @classmethod
    def from_markup(
        cls: type["GameMessage"], info: str, markup: InlineKeyboardMarkup
    ) -> "GameMessage":
        return cls.from_buttons(info=info, buttons=markup.inline_keyboard)

    @classmethod
    def from_buttons(
        cls: type["GameMessage"], info: str, buttons: list[list[InlineKeyboardButton]]
    ) -> "GameMessage":
        actions: list[list[InlineKeyboardButton]] = []
        field: list[list[InlineKeyboardButton]] = []
        for i, row in enumerate(buttons):
            if row[0].callback_data is not None and not row[0].callback_data.startswith(
                "action"
            ):
                actions = buttons[: i + 1]
                field = buttons[i:]
                break

        return cls(info, actions, field)

    @classmethod
    def from_field(
        cls: type["GameMessage"], field: list[list[InlineKeyboardButton]]
    ) -> "GameMessage":
        return cls(info=None, actions=None, field=field)

    def export_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=self.actions + self.field)
