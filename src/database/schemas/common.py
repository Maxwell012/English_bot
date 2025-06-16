from enum import Enum


class Languages(str, Enum):
    ENGLISH = 'en'
    RUSSIAN = 'ru'


class EnglishLevel(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"