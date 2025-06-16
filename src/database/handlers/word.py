from typing import List
from sqlalchemy import func

from src.database.schemas import (
    WordSchemaToDB,
    WordSchemaFromDB,
    WordSchemaOut,
    WordSchemaUpdate,
)
from src.database.utils.UnitOfWork import UnitOfWork
from src.database.utils.AbstractHandler import AbstractHandler
from src.services.SingletonBase import SingletonBase
from src.database.exceptions import NotFoundError


class WordHandler(AbstractHandler, SingletonBase):
    @staticmethod
    async def get_one(uow: UnitOfWork, _filter: func = None, **filter_by) -> WordSchemaFromDB:
        word = await uow.word.find_one(_filter, **filter_by)
        if not word:
            raise NotFoundError("Word is not found")
        return WordSchemaFromDB.model_validate(word)

    @staticmethod
    async def get_all(uow: UnitOfWork, _filter: func = None, **filter_by) -> List[WordSchemaFromDB]:
        words = await uow.word.find_all(_filter=_filter, **filter_by)
        if not words:
            raise NotFoundError("Words are not found")
        return [WordSchemaFromDB.model_validate(word) for word in words]

    @staticmethod
    async def add_one(uow: UnitOfWork, word: WordSchemaToDB) -> int:
        return await uow.word.add_one(data=word)

    @staticmethod
    async def update_one(uow: UnitOfWork, data: WordSchemaUpdate, **filter_by) -> int:
        return await uow.word.edit_one(data, **filter_by)

    @staticmethod
    async def delete_one(uow: UnitOfWork, **filter_by) -> int:
        return await uow.word.delete_one(**filter_by)

    @staticmethod
    def enrich(data: WordSchemaFromDB) -> WordSchemaOut:
        return WordSchemaOut(**data.model_dump())

    async def get_enriched_one(self, uow: UnitOfWork, _filter: func = None, **filter_by) -> WordSchemaOut:
        word = await self.get_one(uow, _filter, **filter_by)
        return self.enrich(word)

    async def get_enriched_all(self, uow: UnitOfWork, _filter: func = None, **filter_by) -> List[WordSchemaOut]:
        words = await self.get_all(uow, _filter, **filter_by)
        return [self.enrich(word) for word in words]