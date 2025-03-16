from idlelib.rpc import response_queue

from aiogram import Bot
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram.filters import CommandStart, Command
import requests
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv
import os

from sqlalchemy.util import await_only

from config import API_KEY

import database.requests as rq

import keyboards.inline as inl

from state import Team, Player, Grid_main, Transfers

router = Router()

async def get_football_data(endpoint, params=None):
    url = f"https://v3.football.api-sports.io/{endpoint}"
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': API_KEY
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer("Привет! Я бот, который поможет найти тебе всю информацию о футболе.", reply_markup=inl.main)

@router.callback_query(F.data == 'again_main')
async def main(callback: CallbackQuery):
    await callback.message.edit_text("Привет! Я бот, который поможет найти тебе всю информацию о футболе.", reply_markup=inl.main)



@router.callback_query(F.data == 'get_team')
async def get_team(callback: CallbackQuery):
    await callback.answer('Вы выбрали поиск по команде.')
    await callback.message.edit_text('Выберите, что хотите найти в футбольной команде:', reply_markup=inl.team)

@router.callback_query(F.data == 'get_structure')
async def get_stcructure(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали поиск состава.')
    await callback.message.edit_text('Введите название команды:')
    await state.set_state(Team.strucrture)

@router.message(Team.strucrture)
async def structure(message: Message, state: FSMContext):
    team_name = message.text
    data = await get_football_data('teams', {'search': team_name})
    if not data.get('response'):
        await message.answer(
            "К сожалению, такую команду не удалось найти. Пожалуйста, введите название команду еще раз или выйдите в главное меню.", reply_markup=inl.main_again)
        return
    teams = data['response']
    team_id = teams[0]['team']['id']
    players = await get_football_data('players/squads', {'team': team_id})
    squad = players['response'][0]['players']
    response_text = f"Игроки команды {teams[0]['team']['name']}: \n"
    for player in squad:
        player_name = player['name']
        player_position = player['position']
        player_number = player['number']
        response_text += f"Имя: {player_name}, позиция: {player_position}, номер: {player_number}\n"
    await message.reply(response_text)
    await state.clear()

@router.callback_query(F.data == 'to_main')
async def main(callback: CallbackQuery):
    await callback.answer('Вы выбрали вернуться на главную.')
    await callback.message.edit_text("Привет! Я бот, который поможет найти тебе всю информацию о футболе.", reply_markup=inl.main)

@router.callback_query(F.data == 'get_info')
async def ask_team_info(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вы выбрали поиск трофеев команды")
    await callback.message.edit_text("Введите название комнады: ")
    await state.set_state(Team.info)

@router.message(Team.info)
async def info(message: Message, state: FSMContext):
    team_name = message.text
    data = await get_football_data('teams', {'search': team_name})

    if not data.get('response'):
        await message.answer(
            "К сожалению, такую команду не удалось найти. Пожалуйста, введите название команду еще раз или выйдите в главное меню.", reply_markup=inl.main_again)
        return
    teams = data['response']
    team_id = teams[0]['team']['id']
    info_data = await get_football_data('teams', {'id': team_id})
    info_name = info_data['response'][0]['team']['name']
    info_founded = info_data['response'][0]['team']['founded']
    info_country = info_data['response'][0]['team']['country']
    info_logo = info_data['response'][0]['team']['logo']
    info_venue_name = info_data['response'][0]['venue']['name']
    info_venue_city = info_data['response'][0]['venue']['city']
    info_venue_logo = info_data['response'][0]['venue']['image']
    response_text_team = f'Информация о команде "{info_data['response'][0]['team']['name']}": \n'
    response_text_team += (f'Команда "{info_data['response'][0]['team']['name']}" была создана в {info_founded}.\nМесто: {info_country}\n')
    response_text_venue = (f'Домашняя арена: {info_venue_name}\nГород домашней арены: {info_venue_city}')
    await message.answer(response_text_team)
    await message.answer_photo(info_logo, caption=f"Логотип команды {info_data['response'][0]['team']['name']}")
    await message.answer(response_text_venue)
    await message.answer_photo(info_venue_logo, caption=f"Фото домашней арены {info_data['response'][0]['team']['name']}")
    await state.clear()

@router.callback_query(F.data == 'get_player')
async def get_player(callback: CallbackQuery):
    await callback.answer("Вы выбрали поиск по игроку")
    await callback.message.edit_text("Выберите, что хотите найти по игроку.", reply_markup=inl.player)

@router.callback_query(F.data == 'get_player_info')
async def player_info(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вы выбрали поиск информаци по игроку")
    await callback.message.edit_text("Введите фамилию игрока: ")
    await state.set_state(Player.info)

@router.message(Player.info)
async def info_player(message: Message, state:FSMContext):
    player_text = message.text
    player_name = await get_football_data('players/profiles', {'search': player_text})
    players_dict = {}
    cnt = 0
    if not player_name.get('response'):
        await message.answer(
            "К сожалению, игрока с такой фамилией не удалось найти. Пожалуйста, введите фамилию еще раз или выйдите в главное меню.", reply_markup=inl.main_again)
        return

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



@router.callback_query(F.data == 'get_standings')
async def get_standings(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вы выбрали поиск по таблице команд.")
    await callback.message.edit_text('Выберите поиск, который хотите осуществить.', reply_markup=inl.main_standings)

@router.callback_query(F.data == 'grid')
async def grid(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вы выбрали поиск по общей сетке.")
    await callback.message.edit_text("Введите через запятую название лиги и сезон (пример: Premier League,2022)\n"
                                     "К сожалению, наш бот умеет искать информацию только с 2021 по 2023 год включительно.")
    await state.set_state(Grid_main.grid)

@router.message(Grid_main.grid)
async def grid_main(message: Message, state: FSMContext):
    mes = message.text.split(',')
    league = await get_football_data('leagues', {'name': mes[0]})
    if not league.get('response'):
        await message.answer("К сожалению, не удалось не удалось найти сетку. Попробуйте ввести ее еще раз или выйдите в меню.", reply_markup=inl.main_again)
    league_id = league['response'][0]['league']['id']
    season = mes[1]
    standings = await get_football_data('standings', {'league': league_id, 'season': season})

    if not standings.get('response'):
        await message.answer("К сожалению, не удалось не удалось найти сетку. Попробуйте ввести ее еще раз или выйдите в меню.", reply_markup=inl.main_again)
    response_text = f'Статистика табличной сетки {standings['response'][0]['league']['name']} {standings['response'][0]['league']['season']} года.\n'
    for team in standings['response'][0]['league']['standings'][0]:
        if team['all']['win'] and team['all']['lose'] and team['all']['draw']:
            response_text += (f"{team['rank']}-e место: {team['team']['name']}. Очков: {team['points']}. Всего матчей: {team['all']['played']} (Побед: {team['all']['win']},"
                              f" Поражений: {team['all']['lose']}, Ничья: {team['all']['draw']})\n")
        elif team['all']['win'] and team['all']['lose']:
            response_text += (
                f"{team['rank']}-e место: {team['team']['name']}. Очков: {team['points']}. Всего матчей: {team['all']['played']} (Побед: {team['all']['win']},"
                f" Поражений: {team['all']['lose']}\n)")
        elif team['all']['win'] and team['all']['draw']:
            response_text += (
                f"{team['rank']}-e место: {team['team']['name']}. Очков: {team['points']}. Всего матчей: {team['all']['played']} (Побед: {team['all']['win']},"
                f" Ничья: {team['all']['draw']})\n")
        elif team['all']['lose']:
            response_text += (
                f"{team['rank']}-e место: {team['team']['name']}. Очков: {team['points']}. Всего матчей: {team['all']['played']} ("
                f"Поражений: {team['all']['lose']})\n")
        elif team['all']['lose'] and team['all']['draw']:
            response_text += (
                f"{team['rank']}-e место: {team['team']['name']}. Очков: {team['points']}. Всего матчей: {team['all']['played']} ("
                f"Поражений: {team['all']['lose']}, Ничья: {team['all']['draw']})\n")
        elif team['all']['win']:
            response_text += (
                f"{team['rank']}-e место: {team['team']['name']}. Очков: {team['points']}. Всего матчей: {team['all']['played']} (Побед: {team['all']['win']}"
                f")\n")
        else:
            response_text += (
                f"{team['rank']}-e место: {team['team']['name']}. Очков: {team['points']}. Всего матчей: {team['all']['played']} ("
                f"Ничья: {team['all']['draw']})\n")
    await message.answer(response_text)
    await state.clear()

@router.callback_query(F.data == 'team_in_grid')
async def team_grid(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вы выбрали поиск по команде в сетке.")
    await callback.message.edit_text("Введите через запятую название лиги, сезон и название команды (пример: La Liga,2021,Barcelona)\n"
                                     "К сожалению, наш бот умеет искать информацию только с 2021 по 2023 год включительно.")
    await state.set_state(Grid_main.team_grid)

@router.message(Grid_main.team_grid)
async def find_grid(message: Message, state: FSMContext):
    text = message.text.split(',')
    league = await get_football_data('leagues', {'name': text[0]})
    if not league.get('response'):
        await message.answer(
            "К сожалению, не удалось не удалось найти сетку. Попробуйте ввести ее еще раз или выйдите в меню.",
            reply_markup=inl.main_again)
    league_id = league['response'][0]['league']['id']
    team = await get_football_data('teams', {'name': text[2]})
    team_id = team['response'][0]['team']['id']
    if not team.get('response'):
        await message.answer(
            "К сожалению, не удалось не удалось найти сетку. Попробуйте ввести ее еще раз или выйдите в меню.",
            reply_markup=inl.main_again)
    season = text[1]
    standings = await get_football_data('standings', {'league': league_id, 'season': season, 'team': team_id})
    if not standings.get('response'):
        await message.answer("К сожалению, не удалось не удалось найти сетку. Попробуйте ввести ее еще раз или выйдите в меню.", reply_markup=inl.main_again)
    response_text = (f'Статистика команды {team['response'][0]['team']['name']} в табличной сетки {standings['response'][0]['league']['name']}'
                     f' {standings['response'][0]['league']['season']} года:\n')
    response_text += f"🏆 Место: {standings['response'][0]['league']['standings'][0][0]['rank']}\n"
    response_text += f"📈 Всего очков: {standings['response'][0]['league']['standings'][0][0]['points']}\n"
    response_text += f"⚽ Проведено матчей: {standings['response'][0]['league']['standings'][0][0]['all']['played']}\n"
    if standings['response'][0]['league']['standings'][0][0]['all']['win']:
        response_text += f"🎉 Побед: {standings['response'][0]['league']['standings'][0][0]['all']['win']}\n"
    if standings['response'][0]['league']['standings'][0][0]['all']['lose']:
        response_text += f"🆘 Поражений: {standings['response'][0]['league']['standings'][0][0]['all']['lose']}\n"
    if standings['response'][0]['league']['standings'][0][0]['all']['draw']:
        response_text += f"🤛🏻 Ничья: {standings['response'][0]['league']['standings'][0][0]['all']['draw']}\n"
    response_text += f"⚽ Всего забито: {standings['response'][0]['league']['standings'][0][0]['all']['goals']['for']}\n"
    response_text += f"🔘 Пропущено голов: {standings['response'][0]['league']['standings'][0][0]['all']['goals']['against']}\n"
    await message.answer(response_text)
    await state.clear()

@router.callback_query(F.data == 'get_transfer')
async def get_transfer(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вы выбрали поиск по трансферу.")
    await callback.message.edit_text("Выберите какой трансфер вы хотите найти.", reply_markup=inl.transfer)

@router.callback_query(F.data == 'player_transfer')
async def get_player_transfer(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вы выбрали поиск по трансферу игрока.")
    await callback.message.edit_text("Введите фамилию игрока:")
    await state.set_state(Transfers.ask_transfer)

@router.message(Transfers.ask_transfer)
async def info_transfer(message: Message, state: FSMContext):
    player_text = message.text
    player_name = await get_football_data('players/profiles', {'search': player_text})
    players_dict = {}
    cnt = 0
    if not player_name.get('response'):
        await message.answer(
            "К сожалению, игрока с такой фамилией не удалось найти. Пожалуйста, введите фамилию еще раз или выйдите в главное меню.",
            reply_markup=inl.main_again)
        return

    await message.answer('Список игроков с похожей фамилией: ')
    for player in player_name['response']:
        cnt += 1
        response_text = f"{cnt}. {player['player']['name']} {player['player']['lastname']} \n"
        players_dict[str(cnt)] = player['player']['id']
        await message.answer(response_text)
    await message.answer("Введите номер игрока по списку, чтобы найти его траснфер.")
    await state.update_data(players_dict=players_dict)
    await state.set_state(Transfers.transfer)

@router.message(Transfers.transfer)
async def transfer2(message: Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    players_dict = data.get('players_dict', {})
    name_football = await get_football_data('players/profiles', {'player': players_dict[text]})
    name_player = name_football['response'][0]['player']['name']


    if not players_dict:
        await message.answer("Ошибка: список игроков не найден. Попробуйте снова.")
        return
    transfer_info = await get_football_data('transfers', {'player': players_dict[text]})
    sorted_transfers = sorted(transfer_info['response'][0]["transfers"], key=lambda x: x["date"])
    response_text = f"История трансферов игрока {name_player}: \n"
    for transfer in sorted_transfers:
        response_text += f'{transfer['teams']['out']['name']} → {transfer['teams']['in']['name']}. Дата: {transfer['date']} Сумма трансфера: {transfer['type']} \n'
    await message.answer(response_text)
    await state.clear()

@router.callback_query(F.data == "team_transfer")
async def transfer_team(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вы выбрали поиск трансерфов команды.")
    await callback.message.edit_text("Введите название команды, чтобы найти историю ее трансферов.")
    await state.set_state(Transfers.team_transfer)

@router.message(Transfers.team_transfer)
async def info_team_transfer(message: Message, state: FSMContext):
    cnt = 0
    text = message.text
    team = await get_football_data('teams', {'name': text})
    if not team:
        await message.answer("Ошибка: список игроков не найден. Попробуйте снова.")
    team_id = team['response'][0]['team']['id']
    transfer_team = await get_football_data('transfers', {'team': team_id})
    response_text = f'История трансферов команды {text} \n:'
    for player in transfer_team['response']:
        cnt += 1
        response_text += f"Игрок {player['player']['name']} в {player['transfers'][0]['teams']['in']['name']} за {player['transfers'][0]['type']} Дата: {player['transfers'][0]['date']}\n"
        if cnt == 10:
            break
    await message.answer(response_text)
    await message.answer('К сожалению, мы можем вывести только первые 10 трансферов, так как список слишком длинный.')
    await state.clear()






























