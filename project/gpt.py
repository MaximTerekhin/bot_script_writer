import logging
from config import  IAM_TOKEN, FOLDER_ID
from info import SYSTEM_PROMPT, MAX_TOKENS
import requests






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

    return tokens
messages = []
messages.append({
    'role': 'system', 'text': SYSTEM_PROMPT
})

def ask_gpt(promts):
    logging.info('Начал работать метод ask_gpt (обработка запроса)')
    url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'Content-Type': 'application/json'
    }
    logging.info('IAM - токен получен.')

    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 1,
            "maxTokens": 350
        },
        "messages": [
            {"role": "system", "text": SYSTEM_PROMPT},
            {"role": "user", "text": promts},
        ]
    }
    logging.info('Данные к запросу сформаровались.')


    response = requests.post(url = url, headers=headers, json=data)
    logging.info('Запрос отправлен.')
    print(response)
    if response.status_code == 200:
        result = response.json()['result']['alternatives'][0]['message']['text']
        logging.info('Получен результат.')
        assistant = result
        messages.append({
                 'role': 'assistant', 'text': assistant})
        return result



def token_count(text):
    logging.info('Подсчет токенов в определённом сообщении...')
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'Content-Type': 'application/json'
    }

    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite/latest",
        "maxTokens": MAX_TOKENS,
        'text': text
        }
    tokens = requests.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion",
        json=data,
        headers=headers
    ).json()['tokens']

    print(len(tokens))
