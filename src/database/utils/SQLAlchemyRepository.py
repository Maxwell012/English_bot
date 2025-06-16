from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from sqlalchemy import insert, select, update, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.schemas.base_schemas import *


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: SchemaToDB) -> int:
        stmt = insert(self.model).values(**data.model_dump(exclude_none=True)).returning(self.model.c.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def edit_one(self, data: SchemaUpdate, **filter_by) -> int:
        stmt = (update(self.model).values(**data.model_dump(exclude_none=True))
                .filter_by(**filter_by).returning(self.model.c.id))
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def edit_all(self, data: SchemaUpdate, _filter: func = None, **filter_by) -> List[int]:
        stmt = (update(self.model).values(**data.model_dump(exclude_none=True))
                .filter_by(**filter_by).returning(self.model.c.id))
        if _filter is not None:
            stmt = stmt.filter(_filter)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def find_all(self, _filter: func = None, **filter_by) -> List[Dict]:
        stmt = select(self.model).filter_by(**filter_by)
        if _filter is not None:
            stmt = stmt.filter(_filter)
        res = await self.session.execute(stmt)
        res = [dict(row._mapping) for row in res.all()]
        return res

    async def find_one(self, _filter: func = None, **filter_by) -> Optional[Dict]:
        stmt = select(self.model).filter_by(**filter_by)
        if _filter is not None:
            stmt = stmt.filter(_filter)
        res = await self.session.execute(stmt)

        row = res.one_or_none()
        return dict(row._mapping) if row else None

    async def delete_one(self, **filter_by) -> int:
        stmt = delete(self.model).filter_by(**filter_by).returning(self.model.c.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def delete_all(self, **filter_by) -> List[Dict]:
        # TODO test it
        stmt = delete(self.model).filter_by(**filter_by).returning(self.model.c.id)
        res = await self.session.execute(stmt)
        res = [dict(row._mapping) for row in res.all()]
        print(res)
        return res
