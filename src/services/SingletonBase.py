
class SingletonBase:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def __del__(self):
        cls = self.__class__
        if cls in cls._instances:
            del cls._instances[cls]
