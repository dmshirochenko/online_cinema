import logging

import numpy as np

from db_managers.db_embeddings import Manager as DBEmbeddings
from db_managers.db_similar import Manager as DBSimilar
from db_managers.db_content import Manager as DBContent
from ml_content.encoders.ae_mlp import AE
from ml_content.feature_extractors.movie_feature import MovieFeatureExtractor
from ml_content.feature_extractors.text_feature import TextFeatureExtractor
from settings import settings

logging.basicConfig(level=logging.INFO)


def load_model(model_path: str, feature_extractor_path: str):
    text_feature_extractor = TextFeatureExtractor(model_name="xlnet-base-cased")
    feature_extractor = MovieFeatureExtractor(
        text_feature_extractor=text_feature_extractor,
        load_path=feature_extractor_path,
    )
    logging.info("Feature extractor loaded.")

    model = AE(input_dim=feature_extractor.feature_dim)
    model.load_encoder(model_path)

    return model, feature_extractor


class EmbeddingsGenWorker:
    def __init__(self, db_embeddings: DBEmbeddings, db_content: DBContent, encoder: AE, feature_extractor):
        self.db_embeddings = db_embeddings
        self.db_content = db_content
        self.encoder = encoder
        self.feature_extractor = feature_extractor

    def update_movies_embeddings(self):
        n_movies = self.db_content.get_num_movies()
        logging.info(f"Num movies to update: {n_movies}")

        for i, movie_info in enumerate(self.db_content.iterate_movie_info()):
            features = self.feature_extractor.transform(movie_info)
            emb = list(self.encoder.encode(features))

            self.db_embeddings.set(movie_info["id"], emb)

            if i % 100 == 0:
                logging.info(f"Processing {i}-th movie...")


class RecsUpdateWorker:
    embs: np.ndarray
    ids: list[str]

    def __init__(self, db_embeddings: DBEmbeddings, db_recs: DBSimilar):
        self.db_embeddings = db_embeddings
        self.db_recs = db_recs

        self._load_embs()

    def _load_embs(self):
        """Load embedded data for recommendation."""
        emb_count = self.db_embeddings.get_count()
        emb_width = self.db_embeddings.get_emb_size()

        self.embs = np.zeros((emb_count, emb_width))
        self.ids = []
        for i, row in enumerate(self.db_embeddings.iterate_all_embeddings()):
            self.embs[i, :] = np.array(row["emb"])
            self.ids.append(row["id"])

    def get_one_recommendation(self, id: str, count: int) -> list[str]:
        """Get one recommendation from embedded model.

        Args:
            id: base object id.
            count: count of recommendations.

        Returns:
            list of recommend similar objects.
        """
        i = self.ids.index(id)
        source_emb = np.expand_dims(self.embs[i, :], 0)
        dists = np.linalg.norm(self.embs - source_emb, axis=1)
        inds_sorted = np.argsort(dists)
        rec_ids = []
        for i, idx_sim in enumerate(inds_sorted[1: count + 1]):
            rec_ids.append(self.ids[idx_sim])

        return rec_ids

    def gen_all_recommendations(self, count: int = 5):
        """Gen and save recommendation for each object

        Args:
            count: Count of receommendation for one object.
        """
        for _id in self.ids:
            rec_ids = self.get_one_recommendation(_id, count)
            self.db_recs.set(_id, rec_ids)
        logging.info("Recommendations generated.")


if __name__ == "__main__":
    model, feature_extractor = load_model(settings.model_path, settings.feature_extractor_path)

    db_embeddings = DBEmbeddings(conf=settings.Embeddings)
    db_recs = DBSimilar(conf=settings.Similar)
    db_content = DBContent(conf=settings.Content)

    embeddings_worker = EmbeddingsGenWorker(
        db_embeddings=db_embeddings, db_content=db_content, encoder=model, feature_extractor=feature_extractor
    )
    embeddings_worker.update_movies_embeddings()
    logging.info("Embeddings updated.")

    worker = RecsUpdateWorker(db_embeddings=db_embeddings, db_recs=db_recs)
    worker.gen_all_recommendations(5)
    logging.info("Similar recommendations uploaded.")
