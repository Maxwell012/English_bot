from datetime import datetime, timedelta
from typing import Tuple

class SpacedRepetition:
    # Константы для алгоритма SM-2
    MIN_EASE_FACTOR = 1.3
    INITIAL_EASE_FACTOR = 2.5
    INITIAL_INTERVAL = 1
    SECOND_INTERVAL = 6

    @staticmethod
    def calculate_next_review(
        current_interval: int,
        current_ease_factor: float,
        repetitions: int,
        quality: int  # 0-5, где 5 - отлично, 0 - не помню
    ) -> Tuple[int, float, int, datetime]:
        """
        Рассчитывает следующие параметры для карточки на основе алгоритма SM-2.
        
        Args:
            current_interval: Текущий интервал в днях
            current_ease_factor: Текущий фактор легкости
            repetitions: Количество повторений
            quality: Качество ответа (0-5)
            
        Returns:
            Tuple[int, float, int, datetime]: (новый интервал, новый фактор легкости, 
                                             новое количество повторений, следующая дата повторения)
        """
        # Обновляем фактор легкости
        new_ease_factor = current_ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease_factor = max(SpacedRepetition.MIN_EASE_FACTOR, new_ease_factor)

        # Обновляем интервал
        if repetitions == 0:
            new_interval = SpacedRepetition.INITIAL_INTERVAL
        elif repetitions == 1:
            new_interval = SpacedRepetition.SECOND_INTERVAL
        else:
            new_interval = int(current_interval * new_ease_factor)

        # Обновляем количество повторений
        new_repetitions = repetitions + 1 if quality >= 3 else 0

        # Рассчитываем следующую дату повторения
        next_review = datetime.now() + timedelta(days=new_interval)

        return new_interval, new_ease_factor, new_repetitions, next_review

    @staticmethod
    def get_initial_values() -> Tuple[int, float, int, datetime]:
        """
        Возвращает начальные значения для новой карточки.
        """
        return (
            SpacedRepetition.INITIAL_INTERVAL,
            SpacedRepetition.INITIAL_EASE_FACTOR,
            0,
            datetime.now() + timedelta(days=SpacedRepetition.INITIAL_INTERVAL)
        ) 