from typing import List
from sqlalchemy import func

from src.database.schemas import (
    FlashcardSchemaToDB,
    FlashcardSchemaFromDB,
    FlashcardSchemaOut,
    FlashcardSchemaUpdate,
)
from src.database.utils.UnitOfWork import UnitOfWork
from src.database.utils.AbstractHandler import AbstractHandler
from src.services.SingletonBase import SingletonBase
from src.database.exceptions import NotFoundError
from src.services.spaced_repetition import SpacedRepetition

from .word import WordHandler


class FlashcardHandler(AbstractHandler, SingletonBase):
    @staticmethod
    async def get_one(uow: UnitOfWork, _filter: func = None, **filter_by) -> FlashcardSchemaFromDB:
        flashcard = await uow.flashcard.find_one(_filter, **filter_by)
        if not flashcard:
            raise NotFoundError("Flashcard is not found")
        return FlashcardSchemaFromDB.model_validate(flashcard)

    @staticmethod
    async def get_all(uow: UnitOfWork, _filter: func = None, **filter_by) -> List[FlashcardSchemaFromDB]:
        fcs = await uow.flashcard.find_all(_filter=_filter, **filter_by)
        if not fcs:
            raise NotFoundError("Flashcards are not found")
        return [FlashcardSchemaFromDB.model_validate(fc) for fc in fcs]

    @staticmethod
    async def add_one(uow: UnitOfWork, flashcard: FlashcardSchemaToDB) -> int:
        return await uow.flashcard.add_one(data=flashcard)

    @staticmethod
    async def update_one(uow: UnitOfWork, data: FlashcardSchemaUpdate, **filter_by) -> int:
        return await uow.flashcard.edit_one(data, **filter_by)

    @staticmethod
    async def delete_one(uow: UnitOfWork, **filter_by) -> int:
        return await uow.flashcard.delete_one(**filter_by)

    @staticmethod
    async def enrich(uow: UnitOfWork, data: FlashcardSchemaFromDB) -> FlashcardSchemaOut:
        word = await WordHandler().get_enriched_one(uow, id=data.word_id)
        return FlashcardSchemaOut(**data.model_dump(), word=word)

    async def get_enriched_one(self, uow: UnitOfWork, _filter: func = None, **filter_by) -> FlashcardSchemaOut:
        fc = await self.get_one(uow, _filter, **filter_by)
        return await self.enrich(uow, fc)

    async def get_enriched_all(self, uow: UnitOfWork, _filter: func = None, **filter_by) -> List[FlashcardSchemaOut]:
        fcs = await self.get_all(uow, _filter, **filter_by)
        return [await self.enrich(uow, fc) for fc in fcs]

    @staticmethod
    async def process_answer(
        uow: UnitOfWork,
        flashcard_id: int,
        quality: int  # 0-5, где 5 - отлично, 0 - не помню
    ) -> FlashcardSchemaOut:
        """
        Обрабатывает ответ пользователя и обновляет параметры карточки.
        
        Args:
            uow: Unit of Work
            flashcard_id: ID карточки
            quality: Качество ответа (0-5)
            
        Returns:
            FlashcardSchemaOut: Обновленная карточка
        """
        # Получаем текущую карточку
        flashcard = await FlashcardHandler.get_one(uow, id=flashcard_id)
        
        # Рассчитываем новые значения
        new_interval, new_ease_factor, new_repetitions, next_review = SpacedRepetition.calculate_next_review(
            current_interval=flashcard.interval,
            current_ease_factor=flashcard.hardness,
            repetitions=flashcard.repetitions,
            quality=quality
        )
        
        # Обновляем карточку
        update_data = FlashcardSchemaUpdate(
            interval=new_interval,
            hardness=new_ease_factor,
            repetitions=new_repetitions,
            next_review=next_review,
            learned=new_repetitions >= 3  # Считаем слово выученным после 3 успешных повторений
        )
        
        await FlashcardHandler.update_one(uow, update_data, id=flashcard_id)
        
        # Возвращаем обновленную карточку
        return await FlashcardHandler().get_enriched_one(uow, id=flashcard_id)