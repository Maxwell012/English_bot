import random
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import aiohttp
import os
from pathlib import Path

from aiogram import Dispatcher, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, Voice
from aiogram.filters import Command
from aiogram.utils.formatting import Spoiler
from typing import Optional

from database.schemas.flashcard import FlashcardSchemaUpdate
from src.database.exceptions import NotFoundError
from src.database.handlers import Handlers
from src.database.handlers.word import WordHandler
from src.database.models import Models
from src.database.utils.UnitOfWork import UnitOfWork
from src.database.schemas import (
    UserSchemaToDB, Languages, UserSchemaFromDB, FlashcardSchemaToDB,
    WordSchemaFromDB, UserSchemaUpdate, EnglishLevel
)
from src.handlers.classes import user_profile_fsm
from src.keyboards.inline import (
    get_settings_inline, get_word_inline, get_main_menu_inline, get_level_inline,
    get_notification_frequency_inline, get_word_review_inline
)
from src.messages.user import (
    choose_language, choose_level, choose_notification_frequency, get_settings_text, get_start_message, 
    get_word_review_message
)
from src.states.user import UserProfileState
from src.utils.utils import get_next_level, is_profile_complete
from src.services.spaced_repetition import SpacedRepetition
from src.dependencies import logger


# Создаем директорию для аудио файлов, если её нет
AUDIO_DIR = Path("media/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

async def get_word_audio(word: str) -> Optional[str]:
    """
    Получает аудио файл для слова используя Google Text-to-Speech API
    """
    try:
        # Здесь можно использовать различные API для получения аудио
        # Например, Google Text-to-Speech, Amazon Polly, или другие
        # Для примера используем простой URL с Google TTS
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={word}&tl=en&client=tw-ob"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    audio_path = AUDIO_DIR / f"{word}.mp3"
                    with open(audio_path, "wb") as f:
                        f.write(await response.read())
                    return str(audio_path)
    except Exception as e:
        print(f"Error getting audio for word {word}: {e}")
        return None

async def start(message: Message, state: FSMContext, uow: UnitOfWork):
    telegram_id = message.from_user.id
    user: Optional[UserSchemaFromDB] = await Handlers.handle_not_found_error(Handlers.user.get_one(uow, id=telegram_id))
    if user:
        language = user.language if user.language else Languages.ENGLISH
        await message.answer(get_start_message(language))
        # video = FSInputFile("media/video/instruction.mp4")
        # await message.answer_video(video=video, caption="📖 Відео інструкція для користування ботом.")
        if not is_profile_complete(user):
            await user_profile_fsm.fill_profile(message, state, user)
    else:
        data = UserSchemaToDB(
            id=telegram_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            full_name=message.from_user.full_name
        )
        await Handlers.user.add_one(uow, data)

        user = await Handlers.user.get_one(uow, id=telegram_id)
        await user_profile_fsm.add_last_message(state, last_message=get_start_message(user.language))
        await user_profile_fsm.fill_profile(message, state, user)


async def profile(message: Message, uow: UnitOfWork, user: UserSchemaFromDB):
    """Показывает профиль пользователя с основной информацией и статистикой"""
    # Получаем статистику по карточкам
    _error_handler = Handlers.handle_not_found_error
    all_flashcards = await _error_handler(Handlers.flashcard.get_all(uow, user_id=user.id), return_if_err=[])
    learning_words = [fc for fc in all_flashcards if not fc.learned]
    learned_words = [fc for fc in all_flashcards if fc.learned]
    
    # Формируем сообщение в зависимости от языка
    if user.language == Languages.RUSSIAN:
        profile_text = (
            f"👤 <b>Профиль пользователя</b>\n\n"
            f"🆔 ID: {user.id}\n"
            f"👤 Имя: {user.full_name}\n"
            f"🌍 Язык: {'Русский' if user.language == Languages.RUSSIAN else 'English'}\n"
            f"📚 Уровень: {user.english_level.value}\n"
            f"🔔 Уведомления: {user.notifications_per_day} раз в день\n\n"
            f"📊 <b>Статистика</b>\n"
            f"📖 Всего слов: {len(all_flashcards)}\n"
            f"📚 В процессе изучения: {len(learning_words)}\n"
            f"✅ Выучено слов: {len(learned_words)}\n"
        )
    else:
        profile_text = (
            f"👤 <b>User Profile</b>\n\n"
            f"🆔 ID: {user.id}\n"
            f"👤 Name: {user.full_name}\n"
            f"🌍 Language: {'Russian' if user.language == Languages.RUSSIAN else 'English'}\n"
            f"📚 Level: {user.english_level.value}\n"
            f"🔔 Notifications: {user.notifications_per_day} times per day\n\n"
            f"📊 <b>Statistics</b>\n"
            f"📖 Total words: {len(all_flashcards)}\n"
            f"📚 Learning: {len(learning_words)}\n"
            f"✅ Learned: {len(learned_words)}\n"
        )
    
    await message.answer(profile_text, reply_markup=get_main_menu_inline(user.language))


async def show_learned_words(message: Message, uow: UnitOfWork, user: UserSchemaFromDB):
    """Показывает список выученных слов"""
    learned_flashcards = await Handlers.flashcard.get_all(uow, user_id=user.id, learned=True)
    
    if not learned_flashcards:
        if user.language == Languages.RUSSIAN:
            await message.answer("У вас пока нет выученных слов. Продолжайте учиться! 📚")
        else:
            await message.answer("You don't have any learned words yet. Keep learning! 📚")
        return
    
    # Получаем информацию о словах
    learned_words = []
    for fc in learned_flashcards:
        word = await Handlers.word.get_one(uow, id=fc.word_id)
        learned_words.append(word)
    
    # Формируем сообщение
    if user.language == Languages.RUSSIAN:
        header = "📚 <b>Выученные слова:</b>\n\n"
    else:
        header = "📚 <b>Learned words:</b>\n\n"
    
    words_text = ""
    for i, word in enumerate(learned_words, 1):
        words_text += f"{i}. <b>{word.text}</b> - {word.translation}\n"
    
    # Разбиваем сообщение на части, если оно слишком длинное
    max_length = 4000
    messages = []
    current_message = header
    
    for line in words_text.split('\n'):
        if len(current_message) + len(line) + 1 > max_length:
            messages.append(current_message)
            current_message = line + '\n'
        else:
            current_message += line + '\n'
    
    if current_message:
        messages.append(current_message)
    
    # Отправляем сообщения
    for msg in messages:
        await message.answer(msg)


async def support(message: Message, bot: Bot):
    await message.answer(
        f"✍ Пишите @neponyatnuy с какими-либо вопросами:\n"
        f"🔨 неполадки в работе сервиса;\n"
        f"💡 предложения и замечания;\n"
        f"💰 возврат денег;\n"
        f"😉 что-либо ещё...\n\n"
        f"Твой идентификатор: <code>{message.from_user.id}</code>"
    )
    await bot.send_contact(
        chat_id=message.chat.id,
        phone_number="+48786467177",
        first_name="Admin"
    )


async def listen(callback: CallbackQuery):
    word = callback.data.split("_")[1]
    # TODO: add a function to get word sound
    # send voice message to an user
    await callback.answer(f"Прослушивание слова: {word}")


async def know(callback: CallbackQuery, uow: UnitOfWork, user: UserSchemaFromDB):
    word_id = callback.data.split("_")[1]
    # TODO: mark the word as known in the database
    word = await Handlers.word.get_one(uow, id=word_id)
    await Handlers.flashcard.add_one(uow, FlashcardSchemaToDB(user_id=user.id, word_id=word_id, known=True))
    await callback.answer(f"Слово {word_id} пропущено.")


async def learn_callback(callback: CallbackQuery):
    word = callback.data.split("_")[1]
    # TODO: add a word into a postgres table
    await callback.answer(f"Слово {word} добавлено в изучаемые.")


async def learned_callback(callback: CallbackQuery):
    word = callback.data.split("_")[1]
    # TODO: mark the word as learned in the database
    await callback.answer(f"Поздравляем! Слово {word} выучено.")


async def settings_callback(callback: CallbackQuery, state: FSMContext, uow: UnitOfWork, user: UserSchemaFromDB):
    """Обработчик кнопки настроек"""
    text = get_settings_text(user.language, user.english_level, user.notifications_per_day)
    keyboard = get_settings_inline(user.language)
    await callback.message.edit_text(text, reply_markup=keyboard)


async def settings_edit_callback(callback: CallbackQuery, state: FSMContext, uow: UnitOfWork, user: UserSchemaFromDB):
    await callback.answer()
    await state.clear()
    await user_profile_fsm.fill_profile(callback.message, state, user)

async def settings_back_callback(callback: CallbackQuery, state: FSMContext, uow: UnitOfWork, user: UserSchemaFromDB):
    """Обработчик возврата в профиль"""
    await profile(callback.message, uow, user)
    await callback.answer()


async def next_word(message: Message, state: FSMContext, uow: UnitOfWork, user: UserSchemaFromDB):
    """Получает следующее слово для изучения"""
    # Получаем все карточки пользователя
    all_flashcards = await Handlers.flashcard.get_all(uow, user_id=user.id)
    all_used_word_ids = [flashcard.word_id for flashcard in all_flashcards]
    
    # Получаем слова, которые пользователь еще не изучал
    _filter = Models.word.c.id.notin_(all_used_word_ids)
    all_words = await Handlers.word.get_all(uow, _filter=_filter, level=user.english_level)
    
    # Проверяем, есть ли слова для изучения на текущем уровне
    if not all_words:
        next_user_level = get_next_level(user.english_level)
        if not next_user_level:
            if user.language == Languages.RUSSIAN:
                await message.answer(
                    "Поздравляем! 🎉 Вы достигли последнего уровня английского языка.\n\n"
                    "К сожалению или к счастью, нам больше нечему вас учить 🙃.\n"
                    "P.S: Наша команда очень рада за вас и предлагает отпраздновать это событие ❗"
                )
            else:
                await message.answer(
                    "Congratulations! 🎉 You have reached the last level of English.\n\n"
                    "Unfortunately or fortunately, we have nothing more to teach you 🙃.\n"
                    "P.S: Our team is really happy for you and suggests celebrating this event ❗"
                )
            return
        
        # Сообщение о переходе на следующий уровень
        if user.language == Languages.RUSSIAN:
            await message.answer(
                f"Поздравляем! 🎉 Вы выучили все слова уровня {user.english_level.value}.\n"
                f"Теперь ваш уровень - {next_user_level.value}.\n\n"
                f"P.S: Продолжайте в том же духе, и вы обязательно достигнете своей цели 🙂❗"
            )
        else:
            await message.answer(
                f"Congratulations! 🎉 You have learned all words from level {user.english_level.value}.\n"
                f"Now your level is {next_user_level.value}.\n\n"
                f"P.S: Keep going and you will definitely achieve your goal 🙂❗"
            )
        
        await Handlers.user.update_one(uow, UserSchemaUpdate(english_level=next_user_level))
        user.english_level = next_user_level
        await next_word(message, state, uow, user)
        return

    # Выбираем случайное слово
    random_word: WordSchemaFromDB = random.choice(all_words)
    
    # Создаем карточку для пользователя
    initial_interval, initial_ease, initial_reps, next_review = SpacedRepetition.get_initial_values()
    new_flashcard = FlashcardSchemaToDB(
        user_id=user.id,
        word_id=random_word.id,
        next_review=next_review
    )
    await Handlers.flashcard.add_one(uow, new_flashcard)
    
    # Отправляем сообщение со словом
    await message.answer(
        get_word_review_message(user.language, random_word),
        reply_markup=get_word_review_inline(user.language, random_word.id)
    )

async def review_word(callback: CallbackQuery, uow: UnitOfWork, user: UserSchemaFromDB):
    """Показывает перевод слова для повторения"""
    word_id = int(callback.data.split("_")[1])
    word = await Handlers.word.get_one(uow, id=word_id)
    
    if user.language == Languages.RUSSIAN:
        text = (
            f"<b>Слово:</b> {word.text}\n"
            f"<b>Перевод:</b> {word.translation}\n"
            f"<b>Пример:</b> {word.example}\n\n"
            f"Оцените, насколько хорошо вы знаете это слово:"
        )
    else:
        text = (
            f"<b>Word:</b> {word.text}\n"
            f"<b>Translation:</b> {word.translation}\n"
            f"<b>Example:</b> {word.example}\n\n"
            f"Rate how well you know this word:"
        )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="5️⃣", callback_data=f"rate_5_{word_id}"),
            InlineKeyboardButton(text="4️⃣", callback_data=f"rate_4_{word_id}"),
            InlineKeyboardButton(text="3️⃣", callback_data=f"rate_3_{word_id}"),
        ],
        [
            InlineKeyboardButton(text="2️⃣", callback_data=f"rate_2_{word_id}"),
            InlineKeyboardButton(text="1️⃣", callback_data=f"rate_1_{word_id}"),
            InlineKeyboardButton(text="0️⃣", callback_data=f"rate_0_{word_id}"),
        ]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

async def process_word_rating(callback: CallbackQuery, uow: UnitOfWork, user: UserSchemaFromDB):
    """Обрабатывает оценку знания слова"""
    _, rating, word_id = callback.data.split("_")
    rating = int(rating)
    word_id = int(word_id)
    
    # Получаем карточку
    flashcard = await Handlers.flashcard.get_one(uow, word_id=word_id, user_id=user.id)
    
    # Обновляем параметры карточки
    updated_card = await Handlers.flashcard.process_answer(uow, flashcard.id, rating)
    
    # Формируем сообщение об успехе
    if user.language == Languages.RUSSIAN:
        if updated_card.learned:
            text = "🎉 Поздравляем! Вы выучили это слово!"
        else:
            text = "✅ Слово обновлено! Следующее повторение через {} дней."
    else:
        if updated_card.learned:
            text = "🎉 Congratulations! You've learned this word!"
        else:
            text = "✅ Word updated! Next review in {} days."
    
    await callback.message.edit_text(text.format(updated_card.interval))
    
    # Предлагаем следующее слово
    await next_word(callback.message, None, uow, user)

async def listen_word(callback: CallbackQuery, uow: UnitOfWork, user: UserSchemaFromDB):
    """Отправляет аудио произношения слова"""
    word_id = int(callback.data.split("_")[1])
    word = await Handlers.word.get_one(uow, id=word_id)
    
    # Получаем аудио файл
    audio_path = await get_word_audio(word.text)
    if audio_path:
        await callback.message.answer_voice(
            voice=FSInputFile(audio_path),
            caption=f"🔊 {word.text}"
        )
        # Удаляем временный файл
        os.remove(audio_path)
    else:
        if user.language == Languages.RUSSIAN:
            await callback.answer("❌ Не удалось получить аудио для этого слова")
        else:
            await callback.answer("❌ Could not get audio for this word")

async def skip_word(callback: CallbackQuery, uow: UnitOfWork, user: UserSchemaFromDB):
    """Пропускает текущее слово"""
    word_id = int(callback.data.split("_")[1])
    
    # Получаем карточку
    flashcard = await Handlers.flashcard.get_one(uow, word_id=word_id, user_id=user.id)
    
    # Обновляем параметры карточки
    await Handlers.flashcard.process_answer(uow, flashcard.id, 0)  # 0 - не знаю
    
    if user.language == Languages.RUSSIAN:
        await callback.answer("⏩ Слово пропущено")
    else:
        await callback.answer("⏩ Word skipped")
    
    # Предлагаем следующее слово
    await next_word(callback.message, None, uow, user)

def register_handlers(dp: Dispatcher):
    # COMMANDS
    dp.message.register(start, Command(commands=["start", "run"]))
    dp.message.register(profile, Command(commands="profile"))
    dp.message.register(support, Command(commands=["support"]))
    dp.message.register(show_learned_words, Command(commands=["learned"]))

    # User Profile
    dp.callback_query.register(user_profile_fsm.get_language, UserProfileState.LANGUAGE, F.data.startswith("language_"))
    dp.callback_query.register(user_profile_fsm.get_level, UserProfileState.ENGLISH_LEVEL, F.data.startswith("level_"))
    dp.callback_query.register(user_profile_fsm.get_notification_frequency, UserProfileState.NOTIFICATION, F.data.startswith("notification_"))

    # Settings
    dp.callback_query.register(settings_callback, F.data == "settings")
    dp.callback_query.register(settings_edit_callback, F.data == "settings_edit")
    dp.callback_query.register(settings_back_callback, F.data == "settings_back")

    # Word handling
    dp.message.register(next_word, Command(commands=["next_word"]))
    dp.callback_query.register(review_word, F.data.startswith("review_"))
    dp.callback_query.register(process_word_rating, F.data.startswith("rate_"))
    dp.callback_query.register(listen_word, F.data.startswith("listen_"))
    dp.callback_query.register(skip_word, F.data.startswith("skip_"))