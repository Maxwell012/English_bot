import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
import os

from src.config import LOG_DIRECTORY


class LoggerBasicService:
    def __init__(self, name: str, level: int = logging.DEBUG) -> None:
        if not os.path.exists(LOG_DIRECTORY):
            os.makedirs(LOG_DIRECTORY)

        self.name = name
        self.logger = self.__create_logger(name, level)

    def get_logger(self) -> Logger:
        return self.logger

    @staticmethod
    def __create_logger(name: str, level: int) -> Logger:
        logger = logging.getLogger(name)
        logger.setLevel(level)

        path = os.path.join(LOG_DIRECTORY, f"{name}.log")
        if not os.path.exists(path):
            with open(path, 'w') as file:
                file.write('')
        file_handler = RotatingFileHandler(path, maxBytes=1024*1024, backupCount=3)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter("%(levelname)s:\t%(asctime)s - %(message)s"))

        logger.addHandler(file_handler)
        return logger
