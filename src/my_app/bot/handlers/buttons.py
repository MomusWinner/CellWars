from my_app.bot.types.button_info import ActionButtonInfo, MenuButtonInfo

MATCHMAKING_INLINE = MenuButtonInfo(
    text="Начать поиск матча",
    callback_data="matchmake",
)

STATS_INLINE = MenuButtonInfo(
    text="Посмотреть статистику",
    callback_data="stats",
)

CANCEL_MATCHMAKING_INLINE = ActionButtonInfo(
    text="Отмена",
    callback_data="cancel_matchmaking",
)

BACK_TO_MENU_INLINE = ActionButtonInfo(
    text="Вернуться в меню",
    callback_data="back_to_menu",
)

PLACE_WARRIORS_INLINE = ActionButtonInfo(
    text="Поставить войнов",
    callback_data="place_warriors",
)

PLACE_BANK_INLINE = ActionButtonInfo(
    text="Поставить банк",
    callback_data="place_bank",
)

CANCEL_FIELD_INLINE = ActionButtonInfo(
    text="Отмена",
    callback_data="cancel_field",
)
