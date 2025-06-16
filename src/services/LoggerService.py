import logging

from .LoggerBasicService import LoggerBasicService

from src.config import LOG_DIRECTORY


class LoggerService(LoggerBasicService):
    # TODO add notifier
    def __init__(self, name: str, level: int = logging.INFO, notifier = None):
        super().__init__(name, level)

        self.notifier = notifier

    async def critical(self, msg, exc_info: bool = True, *args, **kwargs):
        self.logger.critical(msg, exc_info=exc_info, *args, **kwargs)
        if self.notifier: await self.__send_notification(msg)

    async def error(self, msg, exc_info: bool = True, *args, **kwargs):
        self.logger.critical(msg, exc_info=exc_info, *args, **kwargs)
        if self.notifier: await self.__send_notification(msg)

    def warning(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    async def __send_notification(self, msg):
        message = (f"Critical error in <b>{self.name}</b>.\n"
                   f"{msg}")
        file = f'{LOG_DIRECTORY}{self.name}.log'
        await self.notifier.send_document_to_admins(file, message)
