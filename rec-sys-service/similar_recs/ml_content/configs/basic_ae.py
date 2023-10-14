import torch

from ml_content.encoders.ae_mlp import AE
from ml_content.feature_extractors.movie_feature import MovieFeatureExtractor
from ml_content.feature_extractors.text_feature import TextFeatureExtractor
from ml_content.utils.data_loader import ContentDBDataLoader

url = "http://localhost/api/v1"
text_feature_extractor = TextFeatureExtractor(model_name="xlnet-base-cased")
feature_extractor = MovieFeatureExtractor(text_feature_extractor=text_feature_extractor)
data_loader = ContentDBDataLoader(
    api_url=url,
    train_ratio=0.9,
    val_ratio=0.1,
    feature_extractor=feature_extractor,
    cache_on_disk=True,
)


feature_dim = data_loader._feature_extractor.feature_dim


def make_loss():
    return torch.nn.MSELoss()


def make_model_optimizer():
    model = AE(input_dim=feature_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=3e-4, weight_decay=1e-8)
    return model, optimizer


# Hyperparams
epochs: int = 500

trainer_conf = {"save_model_every_epoch": 250}
