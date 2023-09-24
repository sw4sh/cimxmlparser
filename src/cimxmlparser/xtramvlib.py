# @author: Segrenev Mikhail, 2023

import json
import logging
import datetime


class PerfomanceTimeCounter:
    def __init__(self):
        self.start_time = None
        self.start()

    def start(self):
        self.start_time = datetime.datetime.now()

    def elapsedTime(self):
        return datetime.datetime.now() - self.start_time


def write_dictionary(dictionary: dict, dictionary_path: str):
    """
    Записывает словарь в формате .json по указанному пути
    :return: None
    """
    try:
        with open(dictionary_path, 'w', encoding='utf-8') as file:
            json.dump(dictionary, file, ensure_ascii=False, indent=4)
            file.close()
        logging.info("JSON-файл успешно записан.")
    except Exception as excp:
        logging.exception(f"Ошибка при записи JSON-файла: {excp}")