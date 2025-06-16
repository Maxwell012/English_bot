from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.database.schemas import Languages, EnglishLevel
from src.messages.user import level_text


def get_back_button(lan: Languages = Languages.ENGLISH, prefix_for_data: str = None) -> InlineKeyboardButton:
    match lan:
        case Languages.ENGLISH:
            text = "Back"
        case Languages.RUSSIAN:
            text = "Назад"
        case _:
            text = "Back"
    return InlineKeyboardButton(text=f"🔙 {text}", callback_data=f"{prefix_for_data}_back")


def get_skip_button(lan: Languages = Languages.ENGLISH, prefix_for_data: str = None) -> InlineKeyboardButton:
    match lan:
        case Languages.ENGLISH:
            text = "Skip"
        case Languages.RUSSIAN:
            text = "Пропустить"
        case _:
            text = "Skip"
    return InlineKeyboardButton(text=f"⏩ {text}", callback_data=f"{prefix_for_data}_skip")


def get_language_inline(skip_button: bool = False) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🇺🇦 Русский", callback_data=f"language_ru")],
        [InlineKeyboardButton(text=f"🇬🇧 English", callback_data=f"language_en")],
    ])
    if skip_button:
        keyboard.inline_keyboard.append([get_skip_button(prefix_for_data="language")])
    return keyboard


def get_level_inline(lan: Languages = Languages.ENGLISH, skip_button: bool = False) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=level_text[EnglishLevel.A1][lan], callback_data=f"level_{EnglishLevel.A1.value}")],
        [InlineKeyboardButton(text=level_text[EnglishLevel.A2][lan], callback_data=f"level_{EnglishLevel.A2.value}")],
        [InlineKeyboardButton(text=level_text[EnglishLevel.B1][lan], callback_data=f"level_{EnglishLevel.B1.value}")],
        [InlineKeyboardButton(text=level_text[EnglishLevel.B2][lan], callback_data=f"level_{EnglishLevel.B2.value}")],
        [InlineKeyboardButton(text=level_text[EnglishLevel.C1][lan], callback_data=f"level_{EnglishLevel.C1.value}")],
        [get_back_button(lan, "level")]
    ])

    if skip_button:
        keyboard.inline_keyboard[-1].append(get_skip_button(lan, "level"))

    return keyboard


def get_notification_frequency_inline(lan: Languages = Languages.ENGLISH, skip_button: bool = False) -> InlineKeyboardMarkup:
    match lan:
        case Languages.ENGLISH:
            once = "1 time per day"
            four_times = "4 times per day"
            eight_times = "8 times per day"
            twelve_times = "12 times per day"
        case Languages.RUSSIAN:
            once = "1 раз в день"
            four_times = "4 раза в день"
            eight_times = "8 раз в день"
            twelve_times = "12 раз в день"
        # case Languages.UKRAINE:
        #     once = "1 раз на день"
        #     four_times = "4 рази на день"
        #     eight_times = "8 разів на день"
        case _:
            once = "1 time per day"
            four_times = "4 times per day"
            eight_times = "8 times per day"
            twelve_times = "12 times per day"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{once}", callback_data=f"notification_1")],
        [InlineKeyboardButton(text=f"{four_times}", callback_data=f"notification_4")],
        [InlineKeyboardButton(text=f"{eight_times}", callback_data=f"notification_8")],
        [InlineKeyboardButton(text=f"{twelve_times}", callback_data=f"notification_12")],
        [get_back_button(lan, "notification")]
    ])
    
    if skip_button:
        keyboard.inline_keyboard[-1].append(get_skip_button(lan, "notification"))
    
    return keyboard


def get_word_inline(lan: Languages, word_id: id) -> InlineKeyboardMarkup:
    match lan:
        case Languages.ENGLISH:
            listen = "🔊 Listen"
            know = "✅ I know"
            learn = "📚 Learn"
            skip = "⏩ Skip"
        case Languages.RUSSIAN:
            listen = "🔊 Послушать"
            know = "✅ Знаю"
            learn = "📚 Учим"
            skip = "⏩ Пропустить"
        case _:
            listen = "🔊 Listen"
            know = "✅ I know"
            learn = "📚 Learn"
            skip = "⏩ Skip"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=listen, callback_data=f"listen_{word_id}")],
        [InlineKeyboardButton(text=know, callback_data=f"know_{word_id}")],
        [InlineKeyboardButton(text=learn, callback_data=f"learn_{word_id}")],
        [InlineKeyboardButton(text=skip, callback_data=f"skip_{word_id}")],
    ])


def get_learned_inline(lan: Languages, word: str) -> InlineKeyboardMarkup:
    match lan:
        case Languages.ENGLISH:
            learned = "🎉 Learned"
        case Languages.RUSSIAN:
            learned = "🎉 Выучил"
        case _:
            learned = "🎉 Learned"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=learned, callback_data=f"learned_{word}")]
    ])


def get_main_menu_inline(lan: Languages) -> InlineKeyboardMarkup:
    match lan:
        case Languages.ENGLISH:
            settings = "⚙️ Settings"
            my_words = "📖 My words"
            help_text = "❓ Help"
        case Languages.RUSSIAN:
            settings = "⚙️ Настройки"
            my_words = "📖 Мои слова"
            help_text = "❓ Помощь"
        case _:
            settings = "⚙️ Settings"
            my_words = "📖 My words"
            help_text = "❓ Help"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=settings, callback_data="settings")],
        [InlineKeyboardButton(text=my_words, callback_data="my_words")],
        [InlineKeyboardButton(text=help_text, callback_data="help")]
    ])


def get_word_review_inline(lan: Languages, word_id: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру для повторения слова"""
    match lan:
        case Languages.RUSSIAN:
            review = "📝 Проверить знание"
            listen = "🔊 Послушать"
            skip = "⏩ Пропустить"
        case Languages.ENGLISH:
            review = "📝 Check knowledge"
            listen = "🔊 Listen"
            skip = "⏩ Skip"
        case _:
            review = "📝 Check knowledge"
            listen = "🔊 Listen"
            skip = "⏩ Skip"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=review, callback_data=f"review_{word_id}")],
        [InlineKeyboardButton(text=listen, callback_data=f"listen_{word_id}")],
        [InlineKeyboardButton(text=skip, callback_data=f"skip_{word_id}")],
    ])


def get_settings_inline(lan: Languages) -> InlineKeyboardMarkup:
    edit_button = "✏️ Изменить" if lan == Languages.RUSSIAN else "✏️ Edit"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=edit_button, callback_data="settings_edit")],
        [get_back_button(lan, "settings")]
    ])