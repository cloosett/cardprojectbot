import telebot
from telebot import types
import sqlite3


TOKEN = "TOKEN"
bot = telebot.TeleBot(TOKEN)


selected_cards = []
cards_to_insert = [
        "6♥️", "7♥️", "8♥️", "9♥️", "10♥️", "💂‍♂️♥️", "👸♥️", "🤴♥️", "🧛♥️",
        "6♦️", "7♦️", "8♦️", "9♦️", "10♦️", "💂‍♂️♦️", "👸♦️", "🤴♦️", "🧛♦️",
        "6♣️", "7♣️", "8♣️", "9♣️", "10♣️", "💂‍♣️", "👸♣️", "🤴♣️", "🧛♣️",
        "6♠️", "7♠️", "8♠️", "9♠️", "10♠️", "💂♠️", "👸♠️", "🤴♠️", "🧛♠️"
    ]


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    suits = ['♥️', '♦️', '♣️', '♠️']
    ranks = ['6', '7', '8', '9', '10', '💂‍♂️', '👸', '🤴', '🧛']

    for suit in suits:
        row_buttons = [types.KeyboardButton(f"{rank}{suit}") for rank in ranks]
        markup.row(*row_buttons)

    into = types.KeyboardButton('Добавити✅')
    select = types.KeyboardButton('Показати залишок🤫')
    clear_list = types.KeyboardButton('Очистити список🧹')
    markup.row(into, select, clear_list)

    conn = sqlite3.connect('card.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS my_table (
            id INTEGER PRIMARY KEY,
            in_game STRING,
            bat BOOLEAN
        )
    ''')
    for card in cards_to_insert:
        cursor.execute('INSERT INTO my_table (in_game, bat) VALUES (?, ?)', (card, False))
    conn.commit()
    conn.close()

    bot.send_message(message.chat.id, "Виберіть карти:", reply_markup=markup)

def next_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    suits = ['♥️', '♦️', '♣️', '♠️']
    ranks = ['6', '7', '8', '9', '10', '💂‍♂️', '👸', '🤴', '🧛']

    for suit in suits:
        row_buttons = [types.KeyboardButton(f"{rank}{suit}") for rank in ranks]
        markup.row(*row_buttons)

        into = types.KeyboardButton('Добавити✅')
        select = types.KeyboardButton('Показати залишок🤫')
        clear_list = types.KeyboardButton('Очистити список🧹')
        markup.row(into, select, clear_list)

        bot.send_message(message.chat.id, "Виберіть карти:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Добавити✅")
def add_cards_to_list(message):
    global selected_cards
    conn = sqlite3.connect('card.db')
    cursor = conn.cursor()
    for card_add in selected_cards:
        cursor.execute('UPDATE my_table SET bat = ? WHERE in_game = ?', (True, card_add))
    conn.commit()
    cursor.close()
    conn.close()
    selected_cards.clear()

    bot.send_message(message.chat.id, "Карти додані🟢")


@bot.message_handler(func=lambda message: message.text == "Показати залишок🤫")
def output_cards_with_bat_0(message):
    conn = sqlite3.connect('card.db')
    cursor = conn.cursor()

    # Вибірка кард зі значенням in_game, де bat = 0
    cursor.execute("SELECT in_game FROM my_table WHERE bat = 0")
    cards_with_bat_0 = cursor.fetchall()

    cursor.close()
    conn.close()

    if cards_with_bat_0:
        card_list = '\n'.join([card[0] for card in cards_with_bat_0])
        bot.send_message(message.chat.id, f"Залишились такі карти: \n{card_list}")
    else:
        bot.send_message(message.chat.id, "Карт не залишилось")


@bot.message_handler(commands=['new_game'])
def reset_game(message):
    conn = sqlite3.connect('card.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE my_table SET bat = 0")
    conn.commit()
    conn.close()
    selected_cards.clear()
    bot.send_message(message.chat.id, 'Почалась нова ігра💪')
    bot.send_message(message.chat.id, 'Виберіть карти:')

@bot.message_handler(func=lambda message: message.text == "Очистити список🧹")
def clear_list(message):
    selected_cards.clear()
    bot.send_message(message.chat.id, 'Виберіть карти:')

@bot.message_handler(func=lambda message: True)
def selected_card(message):
    card_to_select = message.text

    if card_to_select not in selected_cards:
        selected_cards.append(card_to_select)
        bot.reply_to(message, f'Карта {card_to_select} додана до списку')
    else:
        bot.reply_to(message, f'Карта {card_to_select} вже вибрана')


bot.polling(none_stop=True)