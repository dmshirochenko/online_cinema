import abc
import json
from typing import Any, Optional


class BaseStorage:
    """
    Абстрактный класс для дальнейшей модернизации в необходимых условиях
    """

    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        try:
            with open(self.file_path, "r") as read_file:
                data = json.load(read_file)
        except IOError:
            data = dict()
        data.update(state)
        with open(self.file_path, "w") as write_file:
            json.dump(data, write_file, default=str)

    def retrieve_state(self) -> dict:
        try:
            with open(self.file_path, "r") as read_file:
                data = json.load(read_file)
            return data
        except FileNotFoundError:
            return dict()


class State:
    """
    Класс для хранения состояния при работе с данными, чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или распределённым хранилищем.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.storage.save_state({key: value})

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        data = self.storage.retrieve_state()
        if key in data:
            return data[key]
        else:
            return None
