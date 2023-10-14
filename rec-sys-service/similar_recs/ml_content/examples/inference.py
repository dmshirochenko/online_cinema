import numpy as np
import requests

from ml_content.encoders.ae_mlp import AE
from ml_content.feature_extractors.movie_feature import MovieFeatureExtractor
from ml_content.feature_extractors.text_feature import TextFeatureExtractor

if __name__ == "__main__":
    text_feature_extractor = TextFeatureExtractor(model_name="xlnet-base-cased")
    feature_extractor = MovieFeatureExtractor(
        text_feature_extractor=text_feature_extractor,
        load_path="logs/feature_extractor.pickle",
    )

    # Get random film ID
    url = "http://localhost/api/v1/films/all_films?page[number]=1&page[size]=10"
    film_id = requests.get(url).json()["result"][0]["id"]

    # Get all film info and feature vector from feature extractor
    url = f"http://localhost/api/v1/films/{film_id}"
    film_info = requests.get(url).json()
    features = feature_extractor.transform(film_info)
    features = np.expand_dims(features, 0)

    # Load pytorch model from disk
    model_path = "logs/test2023_07_18_16h37m49s/models/encoder_epoch_499.pt"
    model = AE(input_dim=feature_extractor.feature_dim)
    model.load_encoder(model_path)

    # Model inference
    emb = model.encode(features)
    print("Embedding: ", emb.shape)
