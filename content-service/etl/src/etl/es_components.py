import json
import logging

import elasticsearch

from .base import ETLComponent, ETLManager
from .es_transform import make_normalizer, make_validator
from .utils import backoff


class ElasticLoader(ETLComponent):
    """
    Loads batches of data in Elasticsearch.
    """

    def __init__(self, manager: ETLManager, conf: dict, index: str):
        """
        Args:
            manager: ETLManager instance.
            conf: configuration for elastic.
            index: name of the destination elastic index.
        """
        super().__init__(manager, conf, index)
        self.index = index

        host, port = conf["host"], conf["port"]
        self.es = elasticsearch.Elasticsearch(f"{host}:{port}", timeout=300)

        # Create index if needed
        self._check_index(conf["scheme_path"][index])

    @backoff(logging)
    def load_batch(self, data: dict[str, dict]) -> None:
        """
        Args:
            data: dict mapping id of a filmwork to its info.
        """
        state_data = self._retrieve_state(data)

        bulk_data = []
        for _id, _data in state_data.items():
            index_dict = {"index": {"_index": self.index, "_id": _id}}
            bulk_data.append(index_dict)
            bulk_data.append(_data)

        es_response = self.es.bulk(index=self.index, body=bulk_data)
        if es_response["errors"]:
            logging.error(f"Error during ES update: {es_response}")

        self.state.set_state("data", {})

    def _check_index(self, path: str) -> None:
        """Check if index exists and creates it if necessary."""
        if not self.es.indices.exists(index=self.index):
            with open(path, "r") as f:
                scheme = json.load(f)
            self.es.indices.create(index=self.index, body=scheme)
            logging.info("Index created...")

    def _retrieve_state(self, data: dict):
        state_data = self.state.get_state("data")
        if state_data is None or len(state_data) == 0:
            self.state.set_state("data", data)
            state_data = data
        else:
            state_data.update(data)
            self.state.set_state("data", state_data)

        return state_data


class ElasticTransformer:
    """Transforms given data to ES compatible format."""

    def __init__(self, table: str):
        self.norm_func = make_normalizer(table)
        self.valid_func = make_validator(table)

    def transform(self, data: list[dict]) -> dict[str, dict]:
        try:
            data = self.norm_func(data)
            data = self.valid_func(data)
        except (RuntimeError, ValueError, StopIteration) as err:
            logging.error("Error during ES normalization:", err)
            data = {}
        finally:
            return data
