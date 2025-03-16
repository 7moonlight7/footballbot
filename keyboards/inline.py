from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🤝 Команда", callback_data='get_team'), InlineKeyboardButton(text="🏃‍♂️ Игрок", callback_data='get_player')],
    [InlineKeyboardButton(text='📊 Таблица команд', callback_data='get_standings'), InlineKeyboardButton(text="🔀 Трансферы", callback_data='get_transfer')]

])

team = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📝 Состав', callback_data='get_structure'), InlineKeyboardButton(text="ℹ️ Информация", callback_data="get_info")],
    [InlineKeyboardButton(text='🏠 На главную', callback_data='to_main')]
])
player = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="ℹ️ Информация", callback_data='get_player_info')],
    [InlineKeyboardButton(text='🏠 На главную', callback_data='to_main')]
])

player_info = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="ℹ️ Информация", callback_data='more_info'), InlineKeyboardButton(text='🏠 На главную', callback_data='to_main')]
])

main_standings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🏆 Общая сетка', callback_data='grid'), InlineKeyboardButton(text="🤝 Команда в сетке", callback_data='team_in_grid')]
])

main_again = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏠 На главную", callback_data='again_main')]])

transfer = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👤 По игроку", callback_data='player_transfer'), InlineKeyboardButton(text='🤝 По команде', callback_data="team_transfer")]
])