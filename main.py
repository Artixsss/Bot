import telebot
from telebot import types
import sqlite3
conn = sqlite3.connect('planner_hse.db')


cursor = conn.cursor()

try:
    query = "CREATE TABLE \"planner\" (\"ID\" INTEGER UNIQUE, \"user_id\" INTEGER, \"plan\" TEXT, PRIMARY KEY (\"ID\"))"
    cursor.execute(query)
except:
    pass


bot = telebot.TeleBot("5942129889:AAFQ6MJPBB_OMIjyx8q7aTx3mpJs36_ZR70")

@bot.message_handler(commands=['start'])
def send_keyboard(message, text="Привет я бот-планнер Мирра, чем я могу тебе помочь?"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Добавить дело в список')
    itembtn2 = types.KeyboardButton('Показать список дел')
    itembtn3 = types.KeyboardButton('Удалить дело из списка')
    itembtn4 = types.KeyboardButton("Удалить все дела из списка")
    itembtn5 = types.KeyboardButton('Другое')
    itembtn6 = types.KeyboardButton('Пока все!')
    keyboard.add(itembtn1, itembtn2)
    keyboard.add(itembtn3, itembtn4, itembtn5, itembtn6)

    msg = bot.send_message(message.from_user.id,
                     text=text, reply_markup=keyboard)


    bot.register_next_step_handler(msg, callback_worker)

@bot.message_handler(content_types=['text'])
def handle_docs_audio(message):
    send_keyboard(message, text="Простите я не понимаю. Выберите один из пунктов меню:")



def add_plan(msg):
    with sqlite3.connect('planner_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('INSERT INTO planner (user_id, plan) VALUES (?, ?)',
                       (msg.from_user.id, msg.text))
        con.commit()
    bot.send_message(msg.chat.id, 'Запомнила')
    send_keyboard(msg, "Чем еще могу помочь?")


def get_plans_string(tasks):
    tasks_str = []
    for val in list(enumerate(tasks)):
        tasks_str.append(str(val[0] + 1) + ') ' + val[1][0] + '\n')
    return ''.join(tasks_str)


def show_plans(msg):
    with sqlite3.connect('planner_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('SELECT plan FROM planner WHERE user_id=={}'.format(msg.from_user.id))
        tasks = get_plans_string(cursor.fetchall())
        bot.send_message(msg.chat.id, tasks)
        send_keyboard(msg, "Чем еще могу помочь?")


def delete_all_plans(msg):
    with sqlite3.connect('planner_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('DELETE FROM planner WHERE user_id=={}'.format(msg.from_user.id))
        con.commit()
    bot.send_message(msg.chat.id, 'Удалены все дела. Хорошего отдыха!')
    send_keyboard(msg, "Чем еще могу помочь?")


def delete_one_plan(msg):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with sqlite3.connect('planner_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('SELECT plan FROM planner WHERE user_id=={}'.format(msg.from_user.id))
        tasks = cursor.fetchall()
        for value in tasks:
            markup.add(types.KeyboardButton(value[0]))
        msg = bot.send_message(msg.from_user.id,
                               text = "Выберите одно дело из списка",
                               reply_markup=markup)
        bot.register_next_step_handler(msg, delete_one_plan_)

def delete_one_plan_(msg):
    with sqlite3.connect('planner_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('DELETE FROM planner WHERE user_id==? AND plan==?', (msg.from_user.id, msg.text))
        bot.send_message(msg.chat.id, 'Ура, минус одна задача, продолжайте в том же духе!')
        send_keyboard(msg, "Чем еще могу помочь?")


def callback_worker(call):
    if call.text == "Добавить дело в список":
        msg = bot.send_message(call.chat.id, 'Давайте добавим дело в ваш список! Напишите его ко мне в чат')
        bot.register_next_step_handler(msg, add_plan)

    elif call.text == "Показать список дел":
        try:
            show_plans(call)
        except:
            bot.send_message(call.chat.id, 'Список дел пуст')
            send_keyboard(call, "Чем еще могу помочь?")

    elif call.text == "Удалить дело из списка":
        try:
            delete_one_plan(call)
        except:
            bot.send_message(call.chat.id, 'Список дел пуст')
            send_keyboard(call, "Чем еще могу помочь?")

    elif call.text == "Удалить все дела из списка":
        try:
            delete_all_plans(call)
        except:
            bot.send_message(call.chat.id, 'Список дел пуст')
            send_keyboard(call, "Чем еще могу помочь?")

    elif call.text == "Другое":
        bot.send_message(call.chat.id, 'Больше я пока ничего не умею, но постараюсь научиться!')
        send_keyboard(call, "Чем еще могу помочь?")

    elif call.text == "Пока все!":
        bot.send_message(call.chat.id, 'Хорошего дня! Когда захотите продолжить пользование моими услугами, нажмите на команду /start')



bot.polling(none_stop=True)