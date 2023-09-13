import abc

from .state_storage import JsonFileStorage, State


class ETLManager:
    """Manager that coordinates ETL Components across processes. """
    def __init__(self, state_path: str):
        self._cnt = JsonFileStorage(state_path)

    def init(self) -> None:
        self._cnt.save_state({"cnt": 0})

    def inc_count(self) -> int:
        """Return current counter value and increment it on disk. """
        cnt = self._cnt.retrieve_state()["cnt"]
        self._cnt.save_state({"cnt": cnt + 1})
        return cnt


class ETLBase:
    @abc.abstractmethod
    def _restore_state(self, data: list):
        """Enriches external data batch with internal state if necessary."""


class ETLComponent(ETLBase):

    def __init__(self, manager: ETLManager, conf: dict, table: str,
            batch_size: int = 0):
        """
        Args:
            manager: ETLManager instance.
            conf: Dictionary with DB configuration.
            table: Name of the table in DB.
            batch_size: size of the data batch.
        """
        _id = manager.inc_count()
        state_fn = f"state_id_{_id}_{self.__class__.__name__}_{table}.json"
        self.state = State(JsonFileStorage(state_fn))
                
        self.conf = conf
        self.table = table
        self.batch_size = batch_size

    def _restore_state(self, data: list) -> list:
        state_internal = self.state.get_state("state")
        if state_internal:
            data += state_internal
        return data
