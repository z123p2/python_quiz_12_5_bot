import aiosqlite
from config import DB_NAME


async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу для хранения состояния квиза
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        # Пробуем добавить колонку score (если уже есть - игнорируем ошибку)
        try:
            await db.execute('''ALTER TABLE quiz_state ADD COLUMN score INTEGER DEFAULT 0''')
        except:
            pass
        # Создаем таблицу для хранения результатов
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_results (user_id INTEGER PRIMARY KEY, score INTEGER, total INTEGER, percentage REAL)''')
        # Сохраняем изменения
        await db.commit()


async def get_quiz_index(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def get_quiz_score(user_id):
    # Получаем количество правильных ответов пользователя
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT score FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def update_quiz_index(user_id, index, score=0):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, score) VALUES (?, ?, ?)', (user_id, index, score))
        # Сохраняем изменения
        await db.commit()


async def save_quiz_result(user_id, score, total):
    # Сохраняем результат прохождения квиза
    percentage = round((score / total) * 100, 1) if total > 0 else 0
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_results (user_id, score, total, percentage) VALUES (?, ?, ?, ?)',
                         (user_id, score, total, percentage))
        await db.commit()


async def get_user_statistics(user_id):
    # Получаем статистику пользователя
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT score, total, percentage FROM quiz_results WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return {'score': results[0], 'total': results[1], 'percentage': results[2]}
            else:
                return None