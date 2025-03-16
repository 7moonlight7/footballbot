from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage


class Team(StatesGroup):
    strucrture = State()
    info = State()

class Player(StatesGroup):
    info = State()
    more_info = State()

class Grid_main(StatesGroup):
    grid = State()
    team_grid = State()

class Transfers(StatesGroup):
    ask_transfer = State()
    transfer = State()
    team_transfer = State()