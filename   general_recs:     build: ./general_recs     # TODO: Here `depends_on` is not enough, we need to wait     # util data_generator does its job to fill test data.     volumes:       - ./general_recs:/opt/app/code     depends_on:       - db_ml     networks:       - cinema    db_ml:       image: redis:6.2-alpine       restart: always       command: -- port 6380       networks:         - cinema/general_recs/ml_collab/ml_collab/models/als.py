import logging

import pandas as pd
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.sql.dataframe import DataFrame

from ml_collab.data_loaders.base import DataLoader


class RecSysALSModel:
    """PySpark ALS based recommender system model."""

    def __init__(
        self,
        max_iter: int = 5,
        reg_param: float = 0.09,
        rank: int = 25,
        user_col: str = "user_idx",
        item_col: str = "item_idx",
        rating_col: str = "rating",
        cold_start_strategy: str = "drop",
    ):
        self.als = ALS(
            maxIter=max_iter,
            regParam=reg_param,
            rank=rank,
            userCol=user_col,
            itemCol=item_col,
            ratingCol=rating_col,
            coldStartStrategy=cold_start_strategy,
            nonnegative=True,
        )

        # Trained model that comes from ALS pySpark class
        self._model: ALSModel | None = None

    def train_test(self, df_train: DataFrame, df_test: DataFrame) -> float:
        logging.info("ALS training start...")
        self._model = self.als.fit(df_train)
        logging.info("ALS training done.")

        evaluator = RegressionEvaluator(metricName="rmse", labelCol="overall", predictionCol="prediction")
        predictions = self._model.transform(df_test)
        rmse = evaluator.evaluate(predictions)

        return rmse

    def train(self, df: DataFrame):
        logging.info("ALS training start...")
        self._model = self.als.fit(df)
        logging.info("ALS training done.")

    def save_model(self, path: str):
        self.als.save(path)
        logging.info(f"ALS models saved in {path}.")

    def load_model(self, path: str):
        # TODO: Here we should be sure that loaded model has the same hyperparams as the
        # created one. Probably, the more correct approach is to save them as well to the
        # disk and create ALS object from then in the `load_model` method.
        self.als.load(path)
        logging.info(f"ALS model is loaded from {path}.")

    def make_reccomendations(self, data_loader: DataLoader, n_recommendations: int = 20) -> pd.DataFrame:
        assert self._model is not None, "Call `train` method first."

        user_col = data_loader.user_column
        item_col = data_loader.item_column

        # TODO: Here we load pretty large matrix into the memory which can
        # case issues with large amounts of users in the system
        recs = self._model.recommendForAllUsers(n_recommendations).toPandas()
        logging.info(f"Pandas recommendations dataframe shape {recs.shape}")

        nrecs = (
            recs.recommendations.apply(pd.Series)
            .merge(recs, right_index=True, left_index=True)
            .drop(["recommendations"], axis=1)
            .melt(id_vars=[f"{user_col}_index"], value_name="recommendation")
            .drop("variable", axis=1)
            .dropna()
        )
        nrecs = nrecs.sort_values(f"{user_col}_index")
        nrecs = pd.concat(
            [nrecs["recommendation"].apply(pd.Series), nrecs[f"{user_col}_index"]],
            axis=1,
        )
        nrecs.columns = ["ProductID_index", "Rating", "UserID_index"]

        transformed = data_loader.load_data()
        md = transformed.select(
            transformed[user_col],
            transformed[f"{user_col}_index"],
            transformed[item_col],
            transformed[f"{item_col}_index"],
        )
        md = md.toPandas()

        dict1 = dict(zip(md[f"{user_col}_index"], md[user_col]))
        dict2 = dict(zip(md[f"{item_col}_index"], md[item_col]))

        nrecs[user_col] = nrecs["UserID_index"].map(dict1)
        nrecs[item_col] = nrecs["ProductID_index"].map(dict2)

        nrecs = nrecs.sort_values(user_col)
        nrecs.reset_index(drop=True, inplace=True)
        new = nrecs[[user_col, item_col, "Rating"]]
        new["recommendations"] = list(zip(new[item_col], new.Rating))
        res = new[[user_col, "recommendations"]]

        user_column = res[user_col]
        res_new = res["recommendations"].groupby(user_column).apply(list).reset_index()

        return res_new
