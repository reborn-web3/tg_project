from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_interests_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора интересов"""
    interests = [
        ("💰 Инвестиции", "interest_investments"),
        ("📈 Карьерное развитие", "interest_career"),
        ("💼 Предпринимательство и бизнес", "interest_business"),
        ("📊 Экономика", "interest_economy"),
        ("📢 Маркетинг", "interest_marketing"),
        ("🎨 Искусство", "interest_art"),
        ("⚽ Спорт", "interest_sport"),
    ]

    keyboard = []
    for text, callback_data in interests:
        keyboard.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    # Кнопка подтверждения выбора
    keyboard.append(
        [
            InlineKeyboardButton(
                text="✅ Подтвердить выбор", callback_data="interests_confirm"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_events_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора типов мероприятий"""
    events = [
        ("💼 Деловые", "event_business"),
        ("📚 Обучающие", "event_educational"),
        ("🏃 Спортивные", "event_sport"),
        ("🎭 Культурные", "event_cultural"),
        ("🍽️ Гастрономические", "event_gastronomic"),
    ]

    keyboard = []
    for text, callback_data in events:
        keyboard.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    # Кнопка подтверждения выбора
    keyboard.append(
        [
            InlineKeyboardButton(
                text="✅ Подтвердить выбор", callback_data="events_confirm"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_skip_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой 'Пропустить'"""
    keyboard = [[InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip_about")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_edit_profile_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора поля для редактирования профиля"""
    keyboard = [
        [
            InlineKeyboardButton(text="👤 Имя и фамилия", callback_data="edit_name"),
            InlineKeyboardButton(text="🏙️ Город", callback_data="edit_city"),
        ],
        [
            InlineKeyboardButton(text="💡 Интересы", callback_data="edit_interests"),
            InlineKeyboardButton(text="🎪 Мероприятия", callback_data="edit_events"),
        ],
        [InlineKeyboardButton(text="📝 О себе", callback_data="edit_about")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="edit_cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def update_interests_keyboard(selected: list[str]) -> InlineKeyboardMarkup:
    """Обновленная клавиатура интересов с отметками выбранных"""
    interests_map = {
        "interest_investments": "💰 Инвестиции",
        "interest_career": "📈 Карьерное развитие",
        "interest_business": "💼 Предпринимательство и бизнес",
        "interest_economy": "📊 Экономика",
        "interest_marketing": "📢 Маркетинг",
        "interest_art": "🎨 Искусство",
        "interest_sport": "⚽ Спорт",
    }

    keyboard = []
    for callback_data, text in interests_map.items():
        if callback_data in selected:
            text = f"✅ {text}"
        keyboard.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    keyboard.append(
        [
            InlineKeyboardButton(
                text="✅ Подтвердить выбор", callback_data="interests_confirm"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def update_events_keyboard(selected: list[str]) -> InlineKeyboardMarkup:
    """Обновленная клавиатура мероприятий с отметками выбранных"""
    events_map = {
        "event_business": "💼 Деловые",
        "event_educational": "📚 Обучающие",
        "event_sport": "🏃 Спортивные",
        "event_cultural": "🎭 Культурные",
        "event_gastronomic": "🍽️ Гастрономические",
    }

    keyboard = []
    for callback_data, text in events_map.items():
        if callback_data in selected:
            text = f"✅ {text}"
        keyboard.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    keyboard.append(
        [
            InlineKeyboardButton(
                text="✅ Подтвердить выбор", callback_data="events_confirm"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_event_registration_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой регистрации на мероприятие"""
    keyboard = [
        [InlineKeyboardButton(text="Зарегистрироваться", callback_data="event_register")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
