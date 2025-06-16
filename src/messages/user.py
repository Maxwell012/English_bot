from src.database.schemas import Languages, EnglishLevel, WordSchemaFromDB
from aiogram.utils.formatting import Spoiler


def get_start_message(lan: Languages):
    match lan:
        case Languages.ENGLISH:
            text = (
                "✋ Hi there! I'm here to help you learn English words:\n\n"
                "🔔 I will send you words in notifications until you learn them;\n"
                "💾 I will save the words you are learning/have learned;\n"
                "🧑‍🏫 I will translate any words you send me.\n\n"
                "🏁 Let's get started! Just press \"⏩ Next word\" or type a word you want to learn.\n\n"
                "👁️ In the settings, you can also hide word translations."
            )
        case Languages.RUSSIAN:
            text = (
                "✋ Привет! Я помогу тебе учить английские слова:\n\n"
                "🔔 Буду отправлять тебе слова в уведомлениях, пока ты их не выучишь;\n"
                "💾 Буду сохранять слова, которые ты учишь/выучил;\n"
                "🧑‍🏫 Буду переводить слова, которые ты мне напишешь.\n\n"
                "🏁 Ну что, поехали! Просто нажимай \"⏩ Следующее слово\" или напиши слово, которое хочешь выучить.\n\n"
                "👁️ В настройках ты также можешь скрыть перевод слов."
            )
        # case Languages.UKRAINE:
        #     text = (
        #         "✋ Привіт! Я допоможу тобі вчити англійські слова:\n\n"
        #         "🔔 Надсилатиму тобі слова у сповіщеннях поки ти їх не вивчиш;\n"
        #         "💾 Зберігатиму слова які ти вчиш/вивчив;\n"
        #         "🧑‍🏫 Перекладатиму слова, які ти мені напишеш.\n\n"
        #         "🏁 Отож, поїхали! Просто натискай \"⏩ Наступне слово\" або напиши слово яке ти хочеш вивчити.\n\n"
        #         "👁️ В налаштуваннях ти також можеш сховати переклад слів."
        #     )
        case _:
            text = (
                "✋ Hi there! I'm here to help you learn English words:\n\n"
                "🔔 I will send you words in notifications until you learn them;\n"
                "💾 I will save the words you are learning/have learned;\n"
                "🧑‍🏫 I will translate any words you send me.\n\n"
                "🏁 Let's get started! Just press \"⏩ Next word\" or type a word you want to learn.\n\n"
                "👁️ In the settings, you can also hide word translations."
            )
    return text


def choose_language(lan: Languages):
    match lan:
        case Languages.ENGLISH:
            text = "👅 Select a language for the interface and translations:"
        case Languages.RUSSIAN:
            text = "👅 Выберите язык для интерфейса и перевода:"
        # case Languages.UKRAINE:
        #     text = "👅 Виберіть мову для інтерфейсу та перекладу:"
        case _:
            text = "👅 Select a language for the interface and translations:"
    return text


def language_setting(lan: Languages):
    match lan:
        case Languages.ENGLISH:
            text = "My language (interface): 🇬🇧 English"
        case Languages.RUSSIAN:
            text = "Мой язык (интерфейса): 🇷🇺 Русский"
        # case Languages.UKRAINE:
        #     text = "Моя мова (інтерфейсу): 🇺🇦 Українська"
        case _:
            text = "My language (interface): 🇬🇧 English"
    return text


def choose_level(lan: Languages):
    match lan:
        case Languages.ENGLISH:
            text = "📈 Choose the level of English words you want to learn:"
        case Languages.RUSSIAN:
            text = "📈 Укажи, какого уровня английские слова ты хочешь учить:"
        # case Languages.UKRAINE:
        #     text = "📈 Вкажи якого рівня англійські слова ти хочеш вчити:"
        case _:
            text = "📈 Choose the level of English words you want to learn:"
    return text


level_text = {
    EnglishLevel.A1: {
        Languages.ENGLISH: "👼 A1 - Elementary",
        Languages.RUSSIAN: "👼 A1 - Начальный",
        # Languages.UKRAINIAN: "👼 A1 - Початковий"
    },
    EnglishLevel.A2: {
        Languages.ENGLISH: "👶 A2 - Pre-Intermediate",
        Languages.RUSSIAN: "👶 A2 - Ниже среднего",
        # Languages.UKRAINIAN: "👶 A2 - Нижче середнього"
    },
    EnglishLevel.B1: {
        Languages.ENGLISH: "💪 B1 - Intermediate",
        Languages.RUSSIAN: "💪 B1 - Средний",
        # Languages.UKRAINIAN: "💪 B1 - Середній"
    },
    EnglishLevel.B2: {
        Languages.ENGLISH: "🦍 B2 - Upper Intermediate",
        Languages.RUSSIAN: "🦍 B2 - Выше среднего",
        # Languages.UKRAINIAN: "🦍 B2 - Вище середнього"
    },
    EnglishLevel.C1: {
        Languages.ENGLISH: "✨ C1 - Advanced",
        Languages.RUSSIAN: "✨ C1 - Продвинутый",
        # Languages.UKRAINIAN: "✨ C1 - Просунутий"
    }
}


def level_setting(lan: Languages, level: EnglishLevel):
    return level_text[level][lan]


def choose_notification_frequency(lan: Languages):
    match lan:
        case Languages.ENGLISH:
            text = "🔔 How many times a day would you like me to send you words in notifications? (Optimal: 8)"
        case Languages.RUSSIAN:
            text = "🔔 Сколько раз в день ты хочешь, чтобы я отправлял тебе слова в уведомлениях? (Оптимально: 8)"
        # case Languages.UKRAINE:
        #     text = "🔔 Скільки разів в день ти хочеш щоб я надсилав тобі слова у сповіщеннях? (оптимально 8)"
        case _:
            text = "🔔 How many times a day would you like me to send you words in notifications? (Optimal: 8)"
    return text


def notification_setting(lan: Languages, number_notifications: int):
    if not isinstance(number_notifications, int) or number_notifications <= 0:
        raise ValueError("number_notifications должно быть целым числом больше нуля")

    def get_times_text(num, lang):
        if lang == "en":
            return f"{num} time per day" if num == 1 else f"{num} times per day"
        elif lang == "ru":
            if 11 <= num % 100 <= 19:
                return f"{num} раз в день"
            last_digit = num % 10
            if last_digit == 1:
                return f"{num} раз в день"
            elif 2 <= last_digit <= 4:
                return f"{num} раза в день"
            else:
                return f"{num} раз в день"
        # elif lang == "ua":
        #     if 11 <= num % 100 <= 19:
        #         return f"{num} раз на день"
        #     last_digit = num % 10
        #     if last_digit == 1:
        #         return f"{num} раз на день"
        #     elif 2 <= last_digit <= 4:
        #         return f"{num} рази на день"
        #     else:
        #         return f"{num} раз на день"

    match lan:
        case Languages.ENGLISH:
            text = f"Notifications: 🔔 {get_times_text(number_notifications, 'en')}"
        case Languages.RUSSIAN:
            text = f"Уведомления: 🔔 {get_times_text(number_notifications, 'ru')}"
        # case Languages.UKRAINE:
        #     text = f"Сповіщення: 🔔 {get_times_text(number_notifications, 'ua')}"
        case _:
            text = f"Notifications: 🔔 {get_times_text(number_notifications, 'en')}"

    return text


# def send_word_text(lan: Languages, word: str, example: str):
#     match lan:
#         case Languages.ENGLISH:
#             text = f"{word}\n\nExample: {example}"
#         case Languages.RUSSIAN:
#             text = f"{word}\n\nПример: {example}"
#         # case Languages.UKRAINE:
#         #     text = f"{word}\n\nПриклад: {example}"
#         case _:
#             text = f"{word}\n\nExample: {example}"
#     return text


def get_word_review_message(language: Languages, word: WordSchemaFromDB) -> str:
    """Формирует сообщение для повторения слова"""
    if language == Languages.RUSSIAN:
        return (
            f"<b>Слово:</b> {word.text}\n"
            f"<b>Пример:</b> {Spoiler(word.example)}\n\n"
            f"Нажмите на кнопку, чтобы увидеть перевод и оценить знание слова."
        )
    else:
        return (
            f"<b>Word:</b> {word.text}\n"
            f"<b>Example:</b> {Spoiler(word.example)}\n\n"
            f"Click the button to see the translation and rate your knowledge of the word."
        )
    
def get_settings_text(lan: Languages, level: EnglishLevel, notification: int) -> str:
    if lan == Languages.RUSSIAN:
        text = (
            "⚙️ <b>Настройки</b>\n\n"
            f"🌍 <b>Язык</b>   ---   {lan.value}\n"
            f"📚 <b>Уровень:</b>   ---   {level.value}\n"
            f"🔔 <b>Уведомления</b>   ---   {notification} за день"
        )
    else:
        text = (
            "⚙️ <b>Settings</b>\n\n"
            f"🌍 <b>Language</b>   ---   {lan.value}\n"
            f"📚 <b>Level</b>   ---   {level.value}\n"
            f"🔔 <b>Notifications</b>   ---   {notification} per day"
        )
    return text