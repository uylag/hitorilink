from aiogram import fsm

class SearchStates(fsm.state.StatesGroup):
    in_search = fsm.state.State()
    out_search = fsm.state.State()