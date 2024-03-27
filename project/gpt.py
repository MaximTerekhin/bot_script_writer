import logging

from config import  IAM_TOKEN, FOLDER_ID, TOKEN_BOT
from info import SYSTEM_PROMPT, MAX_TOKENS
import requests
import telebot
import datetime

bot = telebot.TeleBot(TOKEN_BOT)
user_history = {}





def count_tokens_in_dialog(messages):
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "maxTokens": MAX_TOKENS,
        "messages" : []
    }
    for ell in messages:
        data["messages"].append(ell)

    count_tokens = requests.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion",
        json=data,
        headers=headers
    ).json()['tokens']
    tokens = len(count_tokens)
    user_history['tokens'] = tokens
    return tokens



def ask_gpt(message,promts):
    logging.info('Начал работать метод ask_gpt (обработка запроса)')
    user_id = message.from_user.id
    url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'Content-Type': 'application/json'
    }

    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 1.5,
            "maxTokens": 350
        },
        "messages": [
            {"role": "system", "text": SYSTEM_PROMPT},
            {"role": "user", "text": promts},
        ]
    }


    response = requests.post(url, headers=headers, json=data)
    try:
        if response.status_code == 200:
            result = response.json()['result']['alternatives'][0]['message']['text']
            user_history['role'] = 'assistant'
            now = datetime.datetime.now()
            user_history['date'] = now
            user_history['result'] += result

            #bot.send_message(user_id,result)
            #bot.send_message(user_id, '...')
            return result

    except:
        bot.send_message(user_id,'Ошибка ❌')