import numpy as np
from . import spaces_and_feelings

import logging
from pathlib import Path
import os
from .base_moral_scheme import BaseMoralScheme
from .OpenAIInterface import OpenAIInterface
from dotenv import load_dotenv

load_dotenv()


def create_logger(logger_name, log_dir, log_file):
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    path = str(os.path.join(log_dir, log_file))
    handler = logging.FileHandler(path, mode='w', encoding='utf-8')
    formatter = logging.Formatter("%(asctime)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class DummyVirtualTutor:
    def __init__(self, client_id, start_msg):
        self.client_id = client_id
        self.messages = [{"role": "system", "content": start_msg}]
        self.oai_interface = OpenAIInterface()
        self.logger_dialog = create_logger(
            f"dialog_logger_{self.client_id}",
            f"logs_dummy/{self.client_id}",
            "dialog.log"
        )

        self.logger_dialog.info("This is dialog log")

    async def generate_answer(self, replica):
        self.messages.append({"role": "user", "content": replica})
        tutor_response = await self.oai_interface.get_dummy_replica(self.messages)
        return tutor_response


class VirtualTutor:
    def __init__(self, client_id, start_msg):
        self.client_id = client_id
        self.logger_dialog = create_logger(
            f"dialog_logger_{self.client_id}",
            f"logs_moral/{self.client_id}",
            "dialog.log"
        )

        self.logger_dialog.info("This is dialog log")

        # список моральных схем
        self.ms_list = [
            BaseMoralScheme(spaces_and_feelings.first_space, spaces_and_feelings.from1to2, feelings=spaces_and_feelings.feelings1),
            BaseMoralScheme(spaces_and_feelings.second_space, spaces_and_feelings.from2to3, feelings=spaces_and_feelings.feelings2),
            BaseMoralScheme(spaces_and_feelings.third_space, spaces_and_feelings.from3to4, feelings=spaces_and_feelings.feelings3),
            BaseMoralScheme(spaces_and_feelings.fourth_space, feelings=spaces_and_feelings.feelings4)
        ]

        self.last_replica = ""
        self.prev_moral_id = 0
        self.cur_moral_id = 0
        self.messages = [{"role": "assistant", "content": start_msg}]
        self.schemes = [False, False, False, False]
        self.brain = [False, False, False, False]

    async def generate_answer(self, replica):
        self.logger_dialog.warning(f'Сх: {self.schemes}')  # Выводим состояние моральных схем
        self.logger_dialog.warning(f'Br: {self.brain}')  # Выводим состояние моральных схем

        intents = self.ms_list[self.cur_moral_id].get_base_intentions()
        self.logger_dialog.warning(f"intents: {intents}")
        print(f"Intents:\n{intents}")
        action = await self.ms_list[self.cur_moral_id].oai_interface.get_composition(intents, replica)
        print(f"action:{action}")
        self.logger_dialog.warning(f"action: {action}")
        if action is None:
            return "Не удалось связаться с сервером"
        self.logger_dialog.warning(action)
        self.ms_list[self.cur_moral_id].update_vectors(np.array(action))

        appr_state = self.ms_list[self.cur_moral_id].get_appraisals_state()
        feel_state = self.ms_list[self.cur_moral_id].get_feelings_state()
        dist = self.ms_list[self.cur_moral_id].euc_dist(appr_state, feel_state)

        self.logger_dialog.warning(f'appr:{self.ms_list[self.cur_moral_id].get_appraisals()}')
        self.logger_dialog.warning(f'feel:{self.ms_list[self.cur_moral_id].get_feelings()}')
        self.logger_dialog.warning(f'appr_state:{self.ms_list[self.cur_moral_id].get_appraisals_state()}')
        self.logger_dialog.warning(f'feel_state:{self.ms_list[self.cur_moral_id].get_feelings_state()}')

        diff = appr_state - feel_state

        self.logger_dialog.warning(f'diff: {diff}')

        self.prev_moral_id = self.cur_moral_id

        if self.cur_moral_id <= 2:
            condition = await self.ms_list[self.cur_moral_id].oai_interface.get_brain_status(
                self.messages, replica,
                self.cur_moral_id
            )

            self.logger_dialog.warning(f'cond: {condition}')

            if "да" in condition.lower():
                self.brain[self.cur_moral_id] = True
                self.cur_moral_id = min(self.cur_moral_id + 1, 3)

        if dist < 0.25:  # Проверка на превосходство критической точки
            self.schemes[self.cur_moral_id] = True  # Для начала ставим статус текущей схемы в тру
            ##self.cur_moral_id = min(self.cur_moral_id + 1, 2 ) # переходим на след схему, 3 - это число сколько всего схем

        self.logger_dialog.warning(f'cur: {self.cur_moral_id}')
        self.logger_dialog.warning(f'prev: {self.prev_moral_id}')

        reply = await self.ms_list[self.cur_moral_id].oai_interface.get_replica(
            replica, self.messages, intents, diff,
            self.prev_moral_id,
            self.cur_moral_id
        )
        print(f"reply:\n{reply}")
        self.messages.append({"role": "user", "content": replica})  # обновляем историю диалога
        self.messages.append({"role": "assistant", "content": reply})  # обновляем историю диалога
        return reply
