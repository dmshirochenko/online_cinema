import time
import logging

from pydantic import BaseSettings
from pyspark.sql.dataframe import DataFrame
from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer
from pyspark.ml import Pipeline

from ml_collab.models.als import RecSysALSModel

from src.db_connection import DBConnection
from src.web_connection import fetch_users, fetch_liked_movies
from src.auth import fake_sign_up
from settings import app_settings as conf


# TODO: move data loading logic to the ml_collab lib as separate DataLoader
class UGCDataLoader:
    def __init__(self, spark, conf: BaseSettings):
        self.spark = spark
        self.conf = conf

        # TODO: Here need to add exception catching and repeat
        # excecution on content-db and ugc-db behaviour
        self._load_ugc_data()

    def _load_ugc_data(self):
        auth_token = fake_sign_up()
        logging.info(f"Auth token: {auth_token}")

        users = fetch_users(auth_token=auth_token)
        logging.info(f"Total users to be processed: {len(users)}.")

        data = []
        for user in users:
            user_id = user["id"]
            liked_movies = fetch_liked_movies(self.conf.ugc_api_url, user_id, auth_token)
            for movie_id in liked_movies:
                data.append((user_id, movie_id, 1))
        df = spark.createDataFrame(data, ["user_id", "movie_id", "rating"])

        logging.info(f"Total UGC records: {len(data)}")

        indexer = [
            StringIndexer(inputCol=column, outputCol=column + "_index")
            for column in list(set(df.columns) - set(["overall"]))
        ]
        pipeline = Pipeline(stages=indexer)
        self._dataframe = pipeline.fit(df).transform(df)
        logging.info("Successfully processed data for spark.")

    def load_train_test(self, train_ratio: float = 0.8) -> list[DataFrame]:
        return self._dataframe.randomSplit([train_ratio, (1 - train_ratio)])

    def load_data(self) -> DataFrame:
        return self._dataframe

    @property
    def item_column(self):
        return "movie_id"

    @property
    def user_column(self):
        return "user_id"

    @property
    def rating_column(self):
        return "rating"


if __name__ == "__main__":
    logging.info("Wating for the data generation script...")
    time.sleep(4.0)

    spark = SparkSession.builder.appName("Recommendation_system").getOrCreate()

    data_loader = UGCDataLoader(spark, conf)
    data = data_loader.load_data()
    data.show()

    model = RecSysALSModel(
        user_col=data_loader.user_column + "_index",
        item_col=data_loader.item_column + "_index",
        rating_col=data_loader.rating_column,
    )
    model.train(data)

    db_conn = DBConnection(conf.recsys_db_host, conf.recsys_db_port)
    recs = model.make_reccomendations(data_loader)
    for i in range(recs.shape[0]):
        rec = recs.iloc[i]
        user_id = rec[data_loader.user_column]
        movie_ids = [x[0] for x in rec["recommendations"]]

        db_conn.insert_data(user_id, movie_ids)
        logging.info(f"Insert recs for user {user_id}")
