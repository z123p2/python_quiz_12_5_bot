import asyncio
import logging
from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.exceptions import TelegramNetworkError
from quiz_data import quiz_data
from database import get_quiz_index, get_quiz_score, update_quiz_index, save_quiz_result, get_user_statistics
from keyboards import generate_options_keyboard, generate_start_keyboard

# Создаем роутер для группировки хендлеров
router = Router()


async def safe_answer(message, text, **kwargs):
    """Отправляет сообщение без повторных попыток."""
    try:
        return await message.answer(text, **kwargs)
    except TelegramNetworkError:
        pass


async def safe_edit_reply_markup(bot, chat_id, message_id):
    """Пробует убрать кнопки, игнорирует любые ошибки."""
    try:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None
        )
    except:
        pass


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await safe_answer(message, "Добро пожаловать в квиз!", reply_markup=generate_start_keyboard())


# Хэндлер на команду /quiz
@router.message(F.text == "Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    # Убираем кнопку "Начать игру"
    await safe_answer(message, "Давайте начнем квиз!", reply_markup=types.ReplyKeyboardRemove())

    user_id = message.from_user.id
    current_question_index = await get_quiz_index(user_id)

    # Проверяем, есть ли незавершенный квиз
    if 0 < current_question_index < len(quiz_data):
        # Продолжаем с того же места
        await get_question(message, user_id)
    else:
        # Начинаем новый квиз
        await new_quiz(message)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index, 0)
    await get_question(message, user_id)


async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index], current_question_index)
    await safe_answer(message, f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


@router.callback_query(F.data.startswith("right_"))
async def right_answer(callback: types.CallbackQuery):
    # Извлекаем индекс вопроса и индекс выбранного ответа
    parts = callback.data.replace("right_", "").split("_")
    if len(parts) != 2:
        return
    q_idx = int(parts[0])
    selected_index = int(parts[1])

    user_id = callback.from_user.id

    # Проверяем, что вопрос ещё актуален
    current_question_index = await get_quiz_index(user_id)
    if current_question_index != q_idx:
        return

    # Пробуем убрать кнопки, игнорируем ошибки
    await safe_edit_reply_markup(callback.bot, callback.from_user.id, callback.message.message_id)

    score = await get_quiz_score(user_id)

    # Увеличиваем счетчик правильных ответов
    score += 1

    # Получаем текст ответа по индексу
    selected_answer = quiz_data[current_question_index]['options'][selected_index]

    # Выводим ответ пользователя и результат
    await safe_answer(callback.message, f"Ваш ответ: {selected_answer}\nВерно!")

    # Обновление номера текущего вопроса и счета в базе данных
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index, score)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        # Сохраняем результат
        total = len(quiz_data)
        await save_quiz_result(user_id, score, total)
        await safe_answer(callback.message, f"Это был последний вопрос. Квиз завершен!\n"
                                            f"Правильных ответов: {score} из {total} "
                                            f"({round((score/total)*100, 1)}%)")


@router.callback_query(F.data.startswith("wrong_"))
async def wrong_answer(callback: types.CallbackQuery):
    # Извлекаем индекс вопроса и индекс выбранного ответа
    parts = callback.data.replace("wrong_", "").split("_")
    if len(parts) != 2:
        return
    q_idx = int(parts[0])
    selected_index = int(parts[1])

    user_id = callback.from_user.id

    # Проверяем, что вопрос ещё актуален
    current_question_index = await get_quiz_index(user_id)
    if current_question_index != q_idx:
        return

    # Пробуем убрать кнопки, игнорируем ошибки
    await safe_edit_reply_markup(callback.bot, callback.from_user.id, callback.message.message_id)

    score = await get_quiz_score(user_id)
    correct_option = quiz_data[current_question_index]['correct_option']
    correct_answer = quiz_data[current_question_index]['options'][correct_option]

    # Получаем текст ответа по индексу
    selected_answer = quiz_data[current_question_index]['options'][selected_index]

    await safe_answer(callback.message, f"Ваш ответ: {selected_answer}\n"
                                        f"Неправильно. Правильный ответ: {correct_answer}")

    # Обновление номера текущего вопроса в базе данных (счет не меняем)
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index, score)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        # Сохраняем результат
        total = len(quiz_data)
        await save_quiz_result(user_id, score, total)
        await safe_answer(callback.message, f"Это был последний вопрос. Квиз завершен!\n"
                                            f"Правильных ответов: {score} из {total} "
                                            f"({round((score/total)*100, 1)}%)")


# Хэндлер на команду /stats
@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    stats = await get_user_statistics(user_id)
    if stats:
        await safe_answer(message, f"Ваша статистика:\n"
                                   f"Правильных ответов: {stats['score']} из {stats['total']}\n"
                                   f"Процент правильных: {stats['percentage']}%")
    else:
        await safe_answer(message, "Вы еще не проходили квиз. Начните с команды /quiz")