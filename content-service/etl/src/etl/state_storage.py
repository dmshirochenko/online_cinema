import abc
import json
import os
from typing import Any, Optional

from config.settings import JsonStorageSettings


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Save state in permanent storage."""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Load state from the permanent storage."""
        pass
 

class JsonFileStorage(BaseStorage):
    def __init__(self, fn: Optional[str] = None):
        """
        Args:
            fn: name of the json state file.
        """
        conf = JsonStorageSettings()
        if not os.path.exists(conf.dir_path):
            os.makedirs(conf.dir_path)
        
        if fn is None:
            self.file_path = conf.get_path()
        else: 
            self.file_path = os.path.join(conf.dir_path, fn)

        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({}, f)
        
    def save_state(self, state: dict) -> None:
        with open(self.file_path, "r") as f:
            data = json.load(f)
            
        for k, v in state.items():
            data[k] = v
           
        with open(self.file_path, "w") as f:
            json.dump(data, f)
    
    def retrieve_state(self) -> dict | None: 
        with open(self.file_path, "r") as f:
            data = json.load(f) 
        return data if len(data) else None


class State:
    """
    Class that stores state into permanent storage.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage
        
        self.state = self.storage.retrieve_state()
        if self.state is None:
            self.state = {}

    def set_state(self, key: str, value: Any) -> None:
        self.state[key] = value
        self.storage.save_state({key: value})

    def get_state(self, key: str) -> Any:
        return self.state.get(key)
