'''@router.message(Player.info)
async def info_player(message: Message, state:FSMContext):
    player_text = message.text
    player_name = await get_football_data('players/profiles', {'search': player_text})
    players_dict = {}
    cnt = 0
    await message.answer('Список игроков с похожей фамилией: ')
    for player in player_name['response']:
        cnt += 1
        response_text = f"{cnt}. Информация об игроке {player['player']['name']}: \n"
        response_text += f"👤 Имя: {player['player']['name']} Фамилия: {player['player']['lastname']}\n"
        response_text += f"🎂 Возраст: {player['player']['age']}\n"
        response_text += f"📅 Дата рождения: {player['player']['birth']['date']}\n"
        response_text += f"🌍 Место рождения: {player['player']['birth']['country']} {player['player']['birth']['place']}\n"
        players_dict[cnt] = player['player']['id']


        await message.answer(response_text)
    await state.clear()
    await state.update_data(players_dict=players_dict)
    await message.answer('Если хотите найти подробную информацию об игроке, нажмите кнопку снизу.' , reply_markup= inl.player_info)


@router.callback_query(F.data == 'more_info')
async def more_info_player(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вы выбрали поиск больше информации по игроку ")
    await callback.message.edit_text("Введите номер игрока из списка сверху: ")
    await state.set_state(Player.more_info)

@router.message(Player.more_info)
async def more_info(message: Message, state: FSMContext):
    data = await state.get_data()
    players_dict = data.get('players_dict', {})
    print(players_dict)
    try:
        player_number = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный номер игрока.")
        return
    player_id = players_dict[player_number]
    new_info = await get_football_data('players', {'id': player_id})
    await message.answer(new_info['response'][0]['player']['age'])




response_text += f"⚽ Команда: {player_name['response'][0]['statistics']['team']['name']}\n"
        response_text += f"🏆 Лига команды: {player_name['response'][0]['statistics']['league']['name']}\n"
        response_text += f"🛡️ Позиция: {player_name['response'][0]['statistics']['games']['position']}\n"
        response_text += f"🥅 Голы: {player_name['response'][0]['statistics']['goals']['total']}\n"
        response_text += f"🎯 Голевые передачи: {player_name['response'][0]['statistics']['goals']['assists']}\n"'''