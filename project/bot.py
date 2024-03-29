import datetime
import time
import telebot
import logging
from telebot.types import ReplyKeyboardMarkup, Message
from config import TOKEN_BOT, TABLE_NAME
from gpt import ask_gpt, count_tokens_in_dialog, messages, token_count
from info import MAX_TOKENS, SYSTEM_PROMPT
from data_bases import (create_table, insert_user_id, get_session, insert_info, check_users)

bot = telebot.TeleBot(TOKEN_BOT)
create_table(TABLE_NAME)
print(0)
user_history = {}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",encoding='utf-8',
    filename="log_file.txt",
    filemode="w",
)
def create_button(buttons):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    keyboard.add(*buttons)
    return keyboard

session = 0

@bot.message_handler(commands=['start'])
def start_message(message : Message):
    global session
    user_id = str(message.from_user.id)
    token_count_dialog = count_tokens_in_dialog(messages)
    max_users = check_users(MAX_USERS=3)
    session += 1
    session_from_user = get_session(user_id)
    now = datetime.datetime.now()
    if not max_users :
        if len(session_from_user) <= 3 and token_count_dialog < MAX_TOKENS :

            if not user_id:
                insert_user_id(user_id)
            user_name = message.from_user.first_name
            bot.send_message(user_id, f'Привет, {user_name} \n'
                                      f' Я бот, который создает истории на разные темы на основе нейросети .'
                                      f'\n Ты можешь создать историю.\n'
                                      f'Для этого нажми /new_story, а когда зохочешь закончить историю - /end.')
            time.sleep(2)
            bot.send_message(user_id, 'Тебе нужно будет выбрать жанр истории, персонажа и местность,'
                                      'где происходят события.', reply_markup=create_button(['/new_story']))
            logging.info('Приветственное сообщение от бота, старт.')
            time.sleep(1)
            user_history['user_id'] = user_id
            user_history[user_id] = {}

            tokens_system = token_count(SYSTEM_PROMPT)
            insert_info([user_id, 'system_content', SYSTEM_PROMPT, now, len(session_from_user), tokens_system])

            time.sleep(1)
        else:
            bot.send_message(user_id, 'Лимит израсходован! Приходите завтра!')





@bot.message_handler(commands=['new_story'])
def start_story(message):
    user_id = str(message.from_user.id)
    bot.send_message(user_id, 'Начинаем!\n'
                              'Выбери жанр.', reply_markup=create_button(['Комедия', 'Спорт', 'Ужасы']))
    bot.register_next_step_handler(message,get_genre)

def get_genre(message):
    user_id = str(message.from_user.id)
    genre = message.text
    logging.info('Пользователь выбрал жанр.')
    if genre == 'Комедия' or genre == 'Спорт' or genre == 'Ужасы':
        user_history[user_id]['genre'] = genre
        print(user_history)
        bot.send_message(user_id,'Обработка....')
        time.sleep(2)
        bot.send_message(user_id,'Выбери персонажа:',reply_markup=create_button(['Леонардо Ди Каприо', 'Илон Маск',
                                                                                 'Анджелина Джоли', 'Винни-Пух']))
        logging.info('Пользователь корректно выбрал жанр')
        bot.register_next_step_handler(message,get_pers)
    else:
        bot.send_message(user_id, 'Начинаем!\n'
                                  'Выбери жанр.', reply_markup=create_button(['Комедия', 'Спорт', 'Ужасы']))
        logging.info('Пользователь некорректно выбрал жанр.')
        bot.register_next_step_handler(message, get_genre)


def get_pers(message):
    user_id = str(message.from_user.id)
    pers = message.text
    if pers == 'Леонардо Ди Каприо' or pers == 'Илон Маск' or pers == 'Анджелина Джоли' or pers == 'Винни-Пух':
        user_history[user_id]['pers'] = pers
        print(user_history)
        bot.send_message(user_id, 'Обработка....')
        time.sleep(2)
        bot.send_message(user_id,'Марс:\n'
                                    'Действия происходят в 3024 году\n'
                                 'Необитаемый остров: \n'
                                    'Одинокий остров посередине океана.\n'
                                 'Уол-стрит: \n'
                                    'Небольшая узкая улица в нижней части Манхэттена в городе Нью-Йорк. ')

        logging.info('Пользователь корректно выбрал персонажа.')
        bot.send_message(user_id, 'Выбери местность:', reply_markup=create_button(['Марс','Необитаемый остров', 'Уол-стрит']))
        bot.register_next_step_handler(message,get_setting)
    else:
        bot.send_message(user_id, 'Выбери персонажа:', reply_markup=create_button(['Леонардо Ди Каприо', 'Илон Маск',
                                                                                   'Анджелина Джоли','Винни-Пух']))
        logging.info('Пользователь некорректно выбрал персонажа.')
        bot.register_next_step_handler(message, get_pers)
def get_setting(message):
    user_id = str(message.from_user.id)
    setting = message.text
    if setting == 'Марс' or setting == 'Необитаемый остров' or setting == 'Уол-стрит':
        user_history[user_id]['setting'] = setting
        bot.send_message(user_id, 'Детали ясны.\n'
                                  'Если нужно, укажите дополнительную информацию или переходи к истории.',
                         reply_markup=create_button(['/add_info', '/begin']))
        logging.info('Пользователь корректно выбрал setting.')
        print(user_history)
    else:
        bot.send_message(user_id, 'Выбери местность:', reply_markup=create_button(['Марс','Необитаемый остров', 'Уол-стрит']))
        logging.info('Пользователь некорректно выбрал setting.')
        bot.register_next_step_handler(message, get_setting)
    time.sleep(2)


@bot.message_handler(commands=['add_info'])
def action(message):
    user_id = str(message.from_user.id)
    bot.send_message(user_id,'Введите доп-информацию:')
    logging.info('Пользователь захотел ввести дополнительную информацию.')
    bot.register_next_step_handler(message, get_add_info)
def get_add_info(message):
    user_id = str(message.from_user.id)
    add_info = message.text
    print(add_info)
    logging.info('Доп-ная инф-ция получена.')
    user_history[user_id]['additional_info'] = add_info
    bot.send_message(user_id,'Жми - кнопку!',reply_markup=create_button(['/begin']))

@bot.message_handler(commands=['begin'])
def create_promt(message):
    user_id = str(message.from_user.id)
    promts = (f'Напиши историю в стиле {user_history[user_id]["genre"]}'
              f'с главным героем {user_history[user_id]["pers"]}'
              f'начальная позиция {user_history[user_id]["setting"]}'
              )
    logging.info('Промт сгенерирован.')
    if 'additional_info' in user_history[user_id] and user_history[user_id]['additional_info']:
        promts += f'Дополнительная информация: {user_history[user_id]["additional_info"]}'

        logging.info('К промту добавлена доп. инфа.')
    messages.append({
        'role': 'user', 'text': promts
    })
    user_history[user_id]['user_content'] = promts
    now = datetime.datetime.now()
    session_user = get_session(user_id)
    tokens_user = token_count(promts)
    insert_info([user_id, 'user', promts, now, len(session_user), tokens_user])



    result = ask_gpt(promts)
    token_result = token_count(result)
    insert_info([user_id, 'assistant', result, now, len(session_user), token_result])
    time.sleep(1.5)
    bot.send_message(user_id, result)
    if 'result' in user_history and user_history['result']:
        user_history[user_id]['result'] += result
    else:
        user_history[user_id]['result'] = result

    logging.info('Выбор между /end и /continue.')
    user_id = message.from_user.id
    bot.send_message(user_id,'1. Ты можешь продолжить историю.'
                             'Для этого просто напиши про героя и его действия.\n'
                             '2. Ты можешь закончить генерацию - /end', reply_markup=create_button(['/end','/continue']))

@bot.message_handler(commands=['continue'])
def cont_story(message):
    user_id = message.from_user.id
    tokens = count_tokens_in_dialog(messages)
    if tokens < MAX_TOKENS:
        bot.send_message(user_id,'Введи продолжение :')
        bot.register_next_step_handler(message,send_quere)
    else:
        bot.send_message(user_id,'Вы израсходовали лимит токенов!', reply_markup=create_button(['/full_story', '/count_tokens', '/new_story',
                                                                                                   '/debug']))
        time.sleep(7200)
def send_quere(message):
    user_id = str(message.from_user.id)
    now = datetime.datetime.now()
    session_user = get_session(user_id)
    tokens_user = token_count(user_history[user_id]['user_content'])
    continuation_story = message.text
    result = ask_gpt(continuation_story)
    token_result = token_count(result)
    insert_info([user_id, 'user', continuation_story, now, tokens_user, len(session_user)])
    insert_info([user_id, 'assistant', result, now, len(session_user), token_result])
    user_history[user_id]['result'] += result
    bot.send_message(user_id,result, reply_markup=create_button(['/end','/continue']))



@bot.message_handler(commands=['count_tokens'])
def quere_count_tokens(message):
    logging.info('Пользователь запросил кол-во токенов.')
    user_id = str(message.from_user.id)
    tokens = count_tokens_in_dialog(messages)
    user_history[user_id]['tokens'] = tokens
    bot.send_message(user_id,f'Потрачено {tokens} токенов')

@bot.message_handler(commands=['end'])
def the_end(message):
    user_id = message.from_user.id
    bot.send_message(user_id,f'Спасибо, что писал со мной историю.😀 ✌',reply_markup=create_button(['/full_story', '/count_tokens', '/new_story',
                                                                                                   '/debug']))
    print(user_history)
@bot.message_handler(commands=['full_story'])
def fl_story(message):
    user_id = str(message.from_user.id)
    bot.send_message(user_id,f'Ваша история: {user_history[user_id]["result"]}')

@bot.message_handler(commands=['new_story'])
def nw_story(message):
    user_id = message.from_user.id
    tokens = count_tokens_in_dialog(messages)
    if tokens > MAX_TOKENS:
        bot.send_message(user_id,'Токены закончились!')
        time.sleep(7200)
    else:
        start_message(message)


@bot.message_handler(commands=['debug'])
def deb(message):
    user_id = message.from_user.id
    with open('log_file.txt') as f:
        bot.send_document(user_id,f)


bot.polling()