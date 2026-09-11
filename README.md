English | [Русский](README.ru.md)

# Quiz Bot - Telegram Quiz Bot

![Python](https://img.shields.io/badge/python-3.x-blue)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://t.me/python_quiz_12_5_bot)
![aiogram](https://img.shields.io/badge/aiogram-3.x-green)
![License](https://img.shields.io/badge/license-MIT-green)

A Telegram bot for running quizzes on Python.

## Bot name

[@python_quiz_12_5_bot](https://t.me/python_quiz_12_5_bot)

## Commands

| Command | Description |
|---------|----------|
| `/start` | Start the bot: welcome message and a "Start game" button |
| `/quiz` | Start a new quiz (10 Python questions) |
| `/stats` | Show the stats of the last quiz run |

## Description

The bot asks 10 questions about Python. For each question you pick one of four
answer options. After the quiz the bot shows the number of correct answers and
the percentage. The result is saved and can be viewed with `/stats`.

## Project structure

| File | Purpose |
|------|-----------|
| `.env.example` | Template of environment variables (copy to `.env`) |
| `config.py` | Bot settings (token and API base URL from env, DB name) |
| `database.py` | SQLite work (tables, CRUD) |
| `handlers.py` | Command and callback handlers |
| `keyboards.py` | Keyboard builders (Reply and Inline) |
| `main.py` | Entry point, starts the bot |
| `quiz_data.py` | 10 quiz questions |
| `README.md` | Documentation |

## Installation and running

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Get a bot token from @BotFather in Telegram

3. Copy `.env.example` to `.env` and put your token there:
   ```
   BOT_TOKEN=your_telegram_bot_token_here
   ```

4. Run the bot:
   ```
   python main.py
   ```

## API base URL (optional)

If Telegram API is not reachable directly, set a mirror address in `.env`:

   `PROXY_URL=https://api.telegram.org`

If a mirror is not needed - leave the line commented out.

## Database

On first start a `quiz_bot.db` file is created automatically with two tables:

- quiz_state - stores the current question index and the user's correct answer count
- quiz_results - stores the results of the last quiz run (correct/total/percentage)

Data persists between sessions, so the user can continue the quiz from where
they stopped.

## Demo

### 1. Starting the bot
With the /start command a welcome message and a "Start game" button appear

![Bot start](https://github.com/iceflux/python_quiz_12_5_bot/blob/main/screenshots/quiz_start.jpg?raw=true)

### 2. Quiz process
The bot shows a question with four answer options. After picking an option
the bot shows your answer and the result (correct/wrong)

![Quiz question](https://github.com/iceflux/python_quiz_12_5_bot/blob/main/screenshots/quiz_question.jpg?raw=true)
![Correct / Wrong answer](https://github.com/iceflux/python_quiz_12_5_bot/blob/main/screenshots/quiz_correct_wrong.jpg?raw=true)

### 3. Quiz finish and stats
After 10 questions the bot shows the final result: the number of correct
answers and the percentage
The /stats command shows the result of the last quiz run

![Quiz result](https://github.com/iceflux/python_quiz_12_5_bot/blob/main/screenshots/quiz_finish_stats.jpg?raw=true)

## Implementation notes

- Async work based on aiogram 3
- User state stored in SQLite (aiosqlite)
- Inline buttons with answer options
- Error handling and automatic reconnection on network failures
- Stats saved in the database
- Custom Telegram API base URL support for restricted regions

## Requirements

- Python 3.13+
- aiogram 3.29+
- aiosqlite 0.22+
