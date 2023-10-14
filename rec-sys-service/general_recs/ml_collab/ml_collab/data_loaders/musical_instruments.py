import logging

from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import col
from pyspark.sql.session import SparkSession

from ml_collab.data_loaders.base import DataLoader


class MusicalInstrumentsDataLoader(DataLoader):
    """Example dataloader for MusicalInstruments dataset from
    https://cseweb.ucsd.edu/~jmcauley/datasets/amazon/links.html
    """

    def __init__(self, spark: SparkSession, data_path: str):
        """
        Args:
            spark: Spark session object.
            data_path: Path to the the Musical_Instruments_5.json
        """
        df = spark.read.json(data_path)

        nd = df.select(df["asin"], df["overall"], df["reviewerID"])
        indexer = [
            StringIndexer(inputCol=column, outputCol=column + "_index")
            for column in list(set(nd.columns) - set(["overall"]))
        ]
        pipeline = Pipeline(stages=indexer)
        self._dataframe = pipeline.fit(nd).transform(nd)
        logging.info("Successfully processed data for spark.")

    def load_train_test(self, train_ratio: float = 0.8) -> list[DataFrame]:
        return self._dataframe.randomSplit([train_ratio, (1 - train_ratio)])

    def load_data(self) -> DataFrame:
        return self._dataframe

    @property
    def item_column(self):
        return "asin"

    @property
    def user_column(self):
        return "reviewerID"

    @property
    def rating_column(self):
        return "overall"
