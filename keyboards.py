from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def generate_options_keyboard(answer_options, right_answer, question_index):
    builder = InlineKeyboardBuilder()

    for i, option in enumerate(answer_options):
        if option == right_answer:
            callback_data = f"right_{question_index}_{i}"
        else:
            callback_data = f"wrong_{question_index}_{i}"
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=callback_data)
        )

    builder.adjust(1)
    return builder.as_markup()


def generate_start_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    return builder.as_markup(resize_keyboard=True)