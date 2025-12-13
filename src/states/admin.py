from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """Состояния для админ-панели"""

    main_menu = State()
    editing_text = State()  # Редактирование текста по ключу
    waiting_for_text_key = State()  # Ожидание выбора ключа для редактирования
    waiting_for_new_content = State()  # Ожидание нового содержимого

