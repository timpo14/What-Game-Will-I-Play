import telebot
from telebot import types

import json
from datetime import datetime
from random import choice

TOKEN = "7033545407:AAE7zre10DYV6I3x_nGmTB2gqePmiCp8BPQ"
bot = telebot.TeleBot(TOKEN)
data_base = 'games.json'
GENRES = [
    'puzzle', 'boomer shooter',
    'horror', 'sandbox', 'platformer',
    'clicker', 'visual novel', 'party',
    'action', 'RPG', 'survival'
]

bot_version = "0.2.0"

def get_data():
    with open(data_base, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


@bot.message_handler(commands=['random_game'])
def random_game(message):
    chat_id = message.chat.id
    games = get_data()['games']
    random_game = choice(games)
    result_message = f"Игра: {random_game['title']}\n" \
                     f"Жанр: {random_game['genre']}\n" \
                     f"Год выпуска: {random_game['release_year']}\n" \
                     f"Описание: {random_game['description']}"
    bot.send_message(chat_id, result_message)
    try:
        bot.send_photo(chat_id, random_game['image'])
    except:
        bot.send_message(chat_id, 'Извините, картинка недоступна')


@bot.callback_query_handler(func=lambda call: call.data in GENRES)
def random_genre(call):
    try:
        genre = call.data
        games = [game['title'] for game in get_data()['games'] if game['genre'] == genre]
        bot.send_message(call.message.chat.id, f'Игра в жанре {genre}\n' + choice(games))
    except:
        bot.send_message(call.message.chat.id, 'Извините игры в этом жанре пока недоступны ):')


@bot.message_handler(commands=['genre'])
def random_genre_step(message):
    markup = types.InlineKeyboardMarkup()
    for genre in GENRES:
        markup.add(types.InlineKeyboardButton(genre, callback_data=genre))
    bot.send_message(message.chat.id, 'Выберите жанр:', reply_markup=markup)


@bot.message_handler(commands=['new'])
def random_genre_step(message):
    current_year = datetime.now().year
    games = [game['title'] for game in get_data()['games'] if game['release_year'] == current_year]
    result = '\n'.join(games)
    bot.send_message(message.chat.id, 'Релизы этого года:\n' + result)


@bot.message_handler(commands=['help'])
def random_game(message):
    games = get_data()['games']
    text = '/random_game - Получить случайную игру из всех игр нашей базы!\n' \
           '/genre - Получите игру определенного жанра!\n' \
           '/new - Новинки и игры этого года'
    info_about_bot = '*WHAT GAME WILL I PLAY?* - информация\n' \
                     '*ЧТО ЭТО ТАКОЕ?*\n' \
                     '*What Game Will I Play?* - это проект от тех, кто не знает во что поиграть для тех, кто не знает, во что поиграть!\n' \
                     '*ОБ АВТОРАХ*\n', \
                     f'*9Sasha* - идея бота, 88% кода, {int(len(games) / 7 * 100)}% датабазы\n' \
                     f'*timpo14* - идея функций, 12% кода, {int(len(games) - 7 / len(games) * 100)}% датабазы, обслуживание бота(подключение сервера и т.д)'   
    info_about_version = f'*Текущая версия = {bot_version}*\n' \
                         f'*ЧТО НОВОГО В {bot_version}?*\n' \
                         '- Обновлена датабаза*(+ 5 новых игр, +1 новый жанр)*\n - Обновлена команда */help*'
    bot.send_message(message.chat.id, text)
    bot.send_message(message.chat.id, info_about_bot, parse_mode="Markdown")
    bot.send_message(message.chat.id, info_about_version, parse_mode="Markdown")


@bot.message_handler(commands=['info'])
def info_step(message):
    text = 'Введите название игры, о которой хотите получить информацию'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler_by_chat_id(
        chat_id=message.chat.id,
        callback=give_info
    )


def give_info(message):
    text = game_info(message.text)
    if text:
        bot.send_message(message.chat.id, text[0])
        try:
            bot.send_photo(message.chat.id, text[1])
        except:
            bot.send_message(message.chat.id, 'Извините фото недоступно!')
    bot.send_message(message.chat.id, 'Такой игры нет в базе!')


def game_info(title):
    data = get_data()['games']
    for game in data:
        if title.lower() == game['title'].lower():
            result = f'Название: {game["title"]}\n' \
                     f'Жанр: {game["genre"]}\n' \
                     f'Год выпуска: {game["release_year"]}\n' \
                     f'Описание: {game["description"]}\n'
            return result, game['image']
    return 0


def generate_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    random_game = types.KeyboardButton('/random_game')
    games_in_genre = types.KeyboardButton('/genre')
    new_games = types.KeyboardButton('/new')
    info = types.KeyboardButton('/info')
    help_me = types.KeyboardButton('/help')
    markup.add(random_game, games_in_genre, new_games, info, help_me)
    return markup


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    text = 'Привет!\nЕсли не знаешь во что поиграть, наш бот именно для тебя!'
    bot.send_message(message.chat.id, text, reply_markup=generate_keyboard())


if __name__ == "__main__":
    bot.polling(none_stop=True)
