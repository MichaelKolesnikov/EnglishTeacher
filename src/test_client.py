import os

import requests
import json
from dotenv import load_dotenv

if __name__ == "__main__":
    response = requests.get("https://bica-project.tw1.ru/")
    print(response.text)

    response_post_1 = requests.post(
        "https://bica-project.tw1.ru/getAnswerDialog",
        json.dumps({"input_text": "I'm post for dialog"})
    )
    print(response_post_1)

    response_post_2 = requests.post(
        "http://bica-project.tw1.ru/getAnswerEssay/",
        json.dumps({"input_text": "I'm post for essay"})
    )
    print(response_post_2)

    load_dotenv()
    proxy_token = os.getenv("PROXY_TOKEN")
    proxy_url = os.getenv("PROXY_OPENAI_URL")

    headers = {'Authorization': f"Bearer {proxy_token}"}

    body = {
        'model': 'gpt-4o',
        'messages': [
            {
                'role': 'system',
                'content': 'You are a helpful assistant.'
            },
            {
                'role': 'user',
                'content': 'Hello!'
            }
        ]
    }

    response_proxy = requests.post(url=proxy_url, headers=headers, json=body)
    print(response_proxy.json())
