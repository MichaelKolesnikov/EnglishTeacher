import re
import os
import json
import aiohttp
import asyncio
from dotenv import load_dotenv
from typing import List, Dict, Optional

from . import spaces_and_feelings

load_dotenv()
proxy_token = os.getenv("PROXY_TOKEN")
proxy_url = os.getenv("PROXY_OPENAI_URL")

if not proxy_token or not proxy_url:
    raise ValueError("Отсутствует PROXY_TOKEN или PROXY_OPENAI_URL")


class OpenAIInterface:
    def __init__(self):
        self.header = {'Authorization': f"Bearer {proxy_token}"}
        self.url = proxy_url

    @staticmethod
    def clear_intentions(reply: str) -> List[float]:
        """
        Обработка полученных интенций из текста в список чисел.

        Аргументы:
            reply (str): Текст ответа от chatGPT для извлечения интенций.

        Возвращает:
            List[float]: Список числовых значений интенций.
        """
        if not isinstance(reply, str):
            raise ValueError("reply не строка")
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", reply)
        numbers = [float(num) if '.' in num else int(num) for num in numbers]
        return numbers

    async def get_composition(self, intents_dict: Dict[int, str], fraze: str) -> Optional[List[float]]:
        """
        Получение композиции интенций на основе фразы.

        Аргументы:
            intents_dict (Dict[int, str]): Словарь интенций.
            fraze (str): Фраза для анализа.

        Возвращает:
            Optional[List[float]]: Список интенций с их вероятностями, либо None в случае ошибки.
        """
        cat_str = ', '.join(intents_dict.values())
        num = len(intents_dict.values())
        string = f'''
                Ты механизм по определению интенций в речи человека, связанных с его поведением 
                в различных социальных ситуациях.
                Твоей основной задачей является определить вероятность содержания каждой интенции 
                из сказанного предложения от 0 до 1. В твоем распоряжении только {num} 
                интенциональностей для угадывания (они перечислены через запятую):
                {cat_str} Вероятность - число от 0 до 1, где 0 - интенция не содержится совсем, 
                а 1 - содержится точно. Используй интенции только из указанного списка! 
                Выведи {num} значений вероятности каждой интенциональности в фразе:  
                "{fraze}"
                Выведи только значения через запятую
        '''
        body = {
            'model': 'gpt-4o',
            'messages': [{'role': 'assistant', 'content': string}]
        }

        try:
            async with aiohttp.ClientSession() as client:
                async with client.post(url=self.url, headers=self.header, json=body) as response:
                    response.raise_for_status()
                    reply = await response.json()

                    print(f'''Reply1: {reply["choices"][0]["message"]["content"]}''')
                    return self.clear_intentions(reply["choices"][0]["message"]["content"])
        except (aiohttp.ClientError, KeyError, json.JSONDecodeError) as e:
            print(f"Ошибка при запросе к серверу: {e}")
            return None

    async def get_replica(self, last_message: str, messages: List[Dict[str, str]],
                          intension_dict: Dict[int, str], feelings: List[float],
                          prev_scheme: int, current_scheme: int) -> str:
        """
        Генерация новой реплики на основе предыдущих сообщений и схемы.

        Аргументы:
            last_message (str): Последнее сообщение.
            messages (List[Dict[str, str]]): Список сообщений.
            intension_dict (Dict[int, str]): Словарь интенций.
            feelings (List[float]): Список значений чувств.
            prev_scheme (int): Предыдущая схема.
            current_scheme (int): Текущая схема.

        Возвращает:
            str: Ответ на последнюю реплику.
        """
        rlt = [(intension_dict[i if val > -0.05 else -i], val) for i, val in enumerate(feelings, start=1)]
        student_profile = '''Характеристика студента: \n'''

        # Перечисляем элементы
        for idx, (dict_value, list_value) in enumerate(rlt, start=1):
            fnt = f"Студент {dict_value}\n"
            student_profile += fnt

        for idx, (dict_value, list_value) in enumerate(rlt, start=1):
            if list_value < -0.05:
                mov = f"Студент оказался {dict_value}. \
                    Необходимо окрасить свой ответ так, чтобы это поспособствовало \
                    положительной смене этой характеристики"
                student_profile += mov

        changed_message = f'''Последняя реплика человека:{last_message}.
            Сгенерируй фразу - ответ на последнюю реплику человека
            Фраза должна быть адекватным и логичным ответом к последней реплике человека.
            Фраза должна быть уместной в контексте всей истории диалога.
            Фраза должна быть не длиннее 50 слов.
            Фраза не должна содержать никакой информации об этапах диалога
            Выведи только новую реплику.
            Ты должен поменять свой ответ с учетом характеристики студента: {student_profile}
            Параметры по переходам между этапами:
            '''

        if current_scheme - prev_scheme == 1 and current_scheme == 2:
            changed_message = changed_message + spaces_and_feelings.from1to2
        elif current_scheme - prev_scheme == 2 and current_scheme == 3:
            changed_message = changed_message + spaces_and_feelings.from2to3
        elif current_scheme - prev_scheme == 3 and current_scheme == 4:
            changed_message = changed_message + spaces_and_feelings.from3to4
        elif current_scheme == prev_scheme:
            changed_message = changed_message + f"Вы находитесь на {current_scheme + 1} этапе. Переходить пока не нужно"

        messages_opt = list(messages)
        messages_opt.append({"role": "user", "content": changed_message})

        body = {
            'model': 'gpt-4o',
            'messages': messages_opt,
        }

        try:
            async with aiohttp.ClientSession() as client:
                async with client.post(url=self.url, headers=self.header, json=body) as response:
                    response.raise_for_status()
                    reply = await response.json()
                    # reply = json.loads(json.dumps(reply))
                    print(f'''reply2: {reply["choices"][0]["message"]["content"]}''')
                    return reply["choices"][0]["message"]["content"]
        except (aiohttp.ClientError, KeyError, json.JSONDecodeError) as e:
            print(f"Ошибка при запросе к серверу: {e}")
            return "Не удалось связаться с сервером"

    async def get_dummy_replica(self, messages):
        body = {
            'model': 'gpt-4o',
            'messages': messages,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=self.url, headers=self.header, json=body) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        return "Не удалось связаться с сервером"
        except (
                aiohttp.ClientError, aiohttp.ClientResponseError, json.JSONDecodeError, KeyError,
                asyncio.TimeoutError) as e:
            print(f"Ошибка связи с сервером: {e}")
            reply = "Не удалось связаться с сервером"
            return reply
        except Exception as e:
            print(e)
            return f"Непредвиденная ошибка"

    async def get_brain_status(self, messages, last_message, current_scheme):
        if not (0 <= current_scheme <= 2):
            return

        prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', f"scheme{current_scheme}_prompt.md")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            changed_message = f"Последняя реплика человека:{last_message}.\n" + f.read()

        messages_opt = list(messages)
        messages_opt.append({"role": "user", "content": changed_message})

        body = {
            'model': 'gpt-4o',
            'messages': messages_opt,
        }

        try:
            async with aiohttp.ClientSession() as client:
                async with client.post(url=self.url, headers=self.header, json=body) as response:
                    response.raise_for_status()
                    reply = await response.json()
                    print(f'''reply2: {reply["choices"][0]["message"]["content"]}''')
                    return reply["choices"][0]["message"]["content"]
        except (aiohttp.ClientError, aiohttp.ClientResponseError, KeyError, json.JSONDecodeError) as e:
            print(f"Ошибка при запросе к серверу {e}")
            return "Не удалось связаться с сервером"
