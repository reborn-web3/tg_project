from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """Состояния для процесса регистрации пользователя"""

    waiting_for_name = State()
    waiting_for_city = State()
    waiting_for_interests = State()
    waiting_for_events = State()
    waiting_for_about = State()

    # Редактирование профиля
    editing_menu = State()
    editing_name = State()
    editing_city = State()
    editing_interests = State()
    editing_events = State()
    editing_about = State()