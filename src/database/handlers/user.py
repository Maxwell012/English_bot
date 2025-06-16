from sqlalchemy import func
from typing import List

from src.database.schemas import (
    UserSchemaToDB,
    UserSchemaFromDB,
    UserSchemaOut,
    UserSchemaUpdate,
)
from src.database.utils.UnitOfWork import UnitOfWork
from src.database.utils.AbstractHandler import AbstractHandler
from src.services.SingletonBase import SingletonBase
from src.database.exceptions import NotFoundError


class UserHandler(AbstractHandler, SingletonBase):

    @staticmethod
    async def get_one(uow: UnitOfWork, _filter: func = None, **filter_by) -> UserSchemaFromDB:
        user = await uow.user.find_one(_filter, **filter_by)
        if not user:
            raise NotFoundError("User is not found")
        return UserSchemaFromDB.model_validate(user)

    @staticmethod
    async def get_all(uow: UnitOfWork, _filter: func = None, **filter_by) -> List[UserSchemaFromDB]:
        users = await uow.user.find_all(_filter=_filter, **filter_by)
        if not users:
            raise NotFoundError("Users are not found")
        return [UserSchemaFromDB.model_validate(user) for user in users]

    @staticmethod
    async def add_one(uow: UnitOfWork, user: UserSchemaToDB) -> int:
        user_id = await uow.user.add_one(data=user)
        return user_id

    @staticmethod
    async def update_one(uow: UnitOfWork, data: UserSchemaUpdate, **filter_by) -> int:
        result = await uow.user.edit_one(data, **filter_by)
        return result

    @staticmethod
    async def delete_one(uow: UnitOfWork, **filter_by) -> int:
        result = await uow.user.delete_one(**filter_by)
        return result

    @staticmethod
    def enrich(uow: UnitOfWork, data: UserSchemaFromDB) -> UserSchemaOut:
        return UserSchemaOut(**data.model_dump())

    async def get_enriched_one(self, uow: UnitOfWork, _filter: func = None, **filter_by) -> UserSchemaOut:
        user = await self.get_one(uow, _filter, **filter_by)
        enriched_user = self.enrich(uow, user)
        return enriched_user

    async def get_enriched_all(
            self,
            uow: UnitOfWork,
            _filter: func = None,
            **filter_by
    ) -> list[UserSchemaOut]:
        users = await self.get_all(uow, _filter, **filter_by)
        enriched_users = [self.enrich(uow, user) for user in users]
        return enriched_users
