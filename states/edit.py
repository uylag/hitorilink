from aiogram import fsm

# Several parameters edit
class EditStates(fsm.state.StatesGroup):
    name =            fsm.state.State() # Name / nickname ( :p )
    age_required =    fsm.state.State() # Actual age of user
    age_range =       fsm.state.State() # Range between other users age and current user actual age
    gender_actual =   fsm.state.State() # Male, Female
    gender_search =   fsm.state.State() # Male, Female, No Matter
    desc =            fsm.state.State() # Brief description of the profile
    interests =       fsm.state.State() # Create list of all possible interests in general, range from animation to games, sports, programming, anime, etc.
    media =           fsm.state.State() # Build media group with MediaGroupBuilder