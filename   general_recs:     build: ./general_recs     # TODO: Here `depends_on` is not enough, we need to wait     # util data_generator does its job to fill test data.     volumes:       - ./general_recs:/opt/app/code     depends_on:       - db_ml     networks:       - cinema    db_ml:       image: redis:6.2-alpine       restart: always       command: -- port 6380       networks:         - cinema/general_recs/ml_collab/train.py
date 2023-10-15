import logging

from pyspark.sql import SparkSession

from ml_collab.data_loaders.musical_instruments import (
    MusicalInstrumentsDataLoader as DataLoader,
)
from ml_collab.models.als import RecSysALSModel

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    spark = SparkSession.builder.appName("Recommendation_system").getOrCreate()

    data_path = "/opt/app//Musical_Instruments_5.json"
    data_loader = DataLoader(spark, data_path)

    data = data_loader.load_data()
    # train.show()

    model = RecSysALSModel(
        user_col=data_loader.user_column + "_index",
        item_col=data_loader.item_column + "_index",
        rating_col=data_loader.rating_column,
    )
    model.train(data)

    recs = model.make_reccomendations(data_loader)
    for i in range(recs.shape[0]):
        rec = recs.iloc[i]
        user_id = rec[data_loader.user_column]
        items_ids = [x[0] for x in rec["recommendations"]]
        print(f"Reccomendation for user {user_id}: {items_ids}")
        break
