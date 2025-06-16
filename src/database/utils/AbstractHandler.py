from abc import ABC, abstractmethod
from typing import List
from sqlalchemy import func

from src.database.schemas.base_schemas import *
from src.database.utils.UnitOfWork import IUnitOfWork


class AbstractHandler(ABC):
    @staticmethod
    @abstractmethod
    async def get_one(uow: IUnitOfWork, _filter: func = None, **filter_by) -> SchemaFromDB:
        pass

    @staticmethod
    @abstractmethod
    async def get_all(uow: IUnitOfWork, _filter: func = None, **filter_by) -> List[SchemaFromDB]:
        pass

    @staticmethod
    @abstractmethod
    async def update_one(uow: IUnitOfWork, data: SchemaUpdate, **filter_by) -> int:
        pass

    @staticmethod
    @abstractmethod
    async def delete_one(uow: IUnitOfWork, **filter_by) -> int:
        pass

    @staticmethod
    @abstractmethod
    async def add_one(uow: IUnitOfWork, data: SchemaToDB) -> int:
        pass

    @staticmethod
    @abstractmethod
    async def enrich(*args, **kwargs) -> SchemaOut:
        pass

    @abstractmethod
    async def get_enriched_one(self, uow: IUnitOfWork, _filter: func = None, **filter_by) -> SchemaOut:
        pass

    @abstractmethod
    async def get_enriched_all(self, uow: IUnitOfWork, _filter: func = None, **filter_by) -> List[SchemaOut]:
        pass
