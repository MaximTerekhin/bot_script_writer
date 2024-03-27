import time
import telebot
import logging
from telebot.types import ReplyKeyboardMarkup, Message
from config import TOKEN_BOT, TABLE_NAME
from gpt import ask_gpt, count_tokens_in_dialog, user_history
from info import MAX_TOKENS
from data_bases import create_table, insert_row_user_id_session,insert_row_content

bot = telebot.TeleBot(TOKEN_BOT)
create_table(TABLE_NAME)
print(0)

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
    session += 1
    if session <= 3 :
        user_id = str(message.from_user.id)
        print(1)
        user_name = message.from_user.first_name
        bot.send_message(user_id, f'Привет, {user_name} \n'
                                  f' Я бот, который создает истории на разные темы на основе нейросети .'
                                  f'\n Ты можешь создать историю.\n'
                                  f'Для этого нажми /new_story, а когда зохочешь закончить историю - /end.')
        time.sleep(2)
        bot.send_message(user_id, 'Тебе нужно будет выбрать жанр истории, персонажа и местность,'
                                  'где происходят события.', reply_markup=create_button(['/new_story']))
        time.sleep(1)
        print(1)
        user_history['user_id'] = user_id
        print(user_history)
    else:
        print('конец')
    logging.info('Приветственное сообщение от бота, старт')


    time.sleep(1)



@bot.message_handler(commands=['new_story'])
def start_story(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Начинаем!\n'
                              'Выбери жанр.', reply_markup=create_button(['Комедия', 'Спорт', 'Ужасы']))
    bot.register_next_step_handler(message,get_genre)

def get_genre(message):
    user_id = str(message.from_user.id)
    genre = message.text
    logging.info('Пользователь выбрал жанр')
    if genre == 'Комедия' or genre == 'Спорт' or genre == 'Ужасы':
        user_history['genre'] = genre
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
        logging.info('Пользователь некорректно выбрал жанр')
        bot.register_next_step_handler(message, get_genre)


def get_pers(message):
    user_id = message.from_user.id
    pers = message.text
    if pers == 'Леонардо Ди Каприо' or pers == 'Илон Маск' or pers == 'Анджелина Джоли':
        user_history['pers'] = pers
        print(user_history)
        bot.send_message(user_id, 'Обработка....')
        time.sleep(2)
        bot.send_message(user_id,'Марс:\n'
                                    'Действия происходят в 3024 году\n'
                                 'Необитаемый остров: \n'
                                    'Одинокий остров посередине океана.\n'
                                 'Уол-стрит: \n'
                                    'Небольшая узкая улица в нижней части Манхэттена в городе Нью-Йорк. ')

        logging.info('Пользователь корректно выбрал персонажа')
        bot.send_message(user_id, 'Выбери местность:', reply_markup=create_button(['Марс','Необитаемый остров', 'Уол-стрит']))
        bot.register_next_step_handler(message,get_setting)
    else:
        bot.send_message(user_id, 'Выбери персонажа:', reply_markup=create_button(['Леонардо Ди Каприо', 'Илон Маск',
                                                                                   'Анджелина Джоли']))
        logging.info('Пользователь некорректно выбрал персонажа')
        bot.register_next_step_handler(message, get_pers)
def get_setting(message):
    user_id = message.from_user.id
    setting = message.text
    if setting == 'Марс' or setting == 'Необитаемый остров' or setting == 'Уол-стрит':
        user_history['setting'] = setting
        bot.send_message(user_id, 'Детали ясны.\n'
                                  'Если нужно, укажите дополнительную информацию или переходи к истории.',
                         reply_markup=create_button(['add_info', '/begin']))
        logging.info('Пользователь корректно выбрал setting')
        print(user_history)
    else:
        bot.send_message(user_id, 'Выбери местность:', reply_markup=create_button(['Марс','Необитаемый остров', 'Уол-стрит']))
        logging.info('Пользователь некорректно выбрал setting')
        bot.register_next_step_handler(message, get_setting)
    time.sleep(2)


@bot.message_handler(commands=['add_info'])
def action(message):
    user_id = message.from_user.id
    bot.send_message(user_id,'Введите доп-информацию:')
    logging.info('Пользователь захотел ввести дополнительную информацию.')
    bot.register_next_step_handler(message, get_add_info)
def get_add_info(message):
    user_id = message.from_user.id
    add_info = message.text
    logging.info('Доп-ная инф-ция получена')
    user_history['additional_info'] = add_info
    bot.send_message(user_id,'',reply_markup=create_button('/begin'))

@bot.message_handler(commands=['begin'])
def create_promt(message):
    user_id = message.from_user.id
    promts = (f'Напиши историю в стиле {user_history["genre"]}'
              f'с главным героем {user_history["pers"]}'
              f'начальная позиция {user_history["setting"]}'
              f'История должна состоять из 3-4 предложений')
    logging.info('Промт сгенерирован')
    if user_history['additional_info']:
        promts += f'Дополнительная информация: {user_history["additional_info"]}'
        logging.info('К промту добавлена доп. инфа.')

    user_history['content'] = promts
    result = ask_gpt(message,promts)
    time.sleep(3)
    bot.send_message(user_id, result)
    if result:
        bot.register_next_step_handler(message,continua)

# def continuation_story(message):
#     return '...' in message.text
# @bot.message_handler(func=continuation_story)
def continua (message):
    user_id = message.from_user.id
    bot.send_message(user_id,'1. Ты можешь продолжить историю.'
                             'Для этого просто напиши про героя и его действия.\n'
                             '2. Ты можешь закончить генерацию - /end', reply_markup=create_button(['/end','/continue']))

@bot.message_handler(commands=['continue'])
def cont_story(message):
    user_id = message.from_user.id
    bot.send_message(user_id,'Введи продолжение :')
    bot.register_next_step_handler(message,send_quere)
def send_quere(message):
    continuation_story = message.text
    ask_gpt(message,continuation_story)



@bot.message_handler(commands=['count_tokens'])
def quere_count_tokens(message):
    user_id = message.from_user.id
    tokens = count_tokens_in_dialog(message)
    bot.send_message(user_id,f'Потрачено {tokens} токенов')

@bot.message_handler(commands=['end'])
def the_end(message):
    user_id = message.from_user.id
    bot.send_message(user_id,f'Спасибо, что писал со мной историю.😀 ✌',reply_markup=create_button(['/full_story', '/count_tokens', '/new_story',
                                                                                                   '/debug']))
@bot.message_handler(commands=['full_story'])
def fl_story(message):
    user_id = message.from_user.id
    bot.send_message(user_id,f'Ваша история: {user_history["result"]}')

@bot.message_handler(commands=['new_story'])
def nw_story(message):
    start_message(message)




bot.polling()