import logging
import random
from typing import Callable

import numpy as np
import torch

from ml_content.utils.data_loader import DataLoader
from ml_content.utils.logger import AbstractLogger


class BaseTrainer:
    """Basic training loop with fixed number of epochs to run."""

    def __init__(
        self,
        epochs: int,
        data_loader: DataLoader,
        make_loss: Callable,
        make_model_optimizer: Callable,
        logger: AbstractLogger,
        trainer_conf: dict,
    ):
        """
        Args:
            epochs: Number of epochs to run the training.
            data_loader: DataLoader class.
            make_loss: Loss function factory.
            make_model_optimizer: Model & optimizer factory.
            logger: Logger to save scalars and models.
            trainer_conf: Config with trainer specific parameters.
        """
        self._epochs = epochs
        self._logger = logger
        self._data_loader = data_loader
        self.conf = trainer_conf

        self._loss = make_loss()
        self._model, self._opt = make_model_optimizer()

    def train(self) -> None:
        val_data = self._data_loader.get_val_data()
        val_data = torch.tensor(val_data, dtype=torch.float32)

        test_data = self._data_loader.get_test_data()
        test_data = torch.tensor(test_data, dtype=torch.float32)

        for epoch in range(self._epochs):
            train_loss = self.train_one_epoch(epoch)

            val_reconstr = self._model(val_data)
            val_loss = self._loss(val_reconstr, val_data)
            self._logger.log_scalar("loss/val", val_loss.item(), epoch)

            if (epoch + 1) % self.conf["save_model_every_epoch"] == 0:
                self._logger.save_model(self._model, epoch)

            if epoch % 10 == 0:
                logging.info(f"Epoch {epoch:5d} Train loss {train_loss:4.3f} Val loss {val_loss:4.3f}")

    def train_one_epoch(self, epoch: int) -> float:
        """
        Train one epoch.

        Args:
            epoch: Epoch number.

        Returns:
            last train loss value.
        """
        train_losses = []
        for batch in self._data_loader.get_batch(batch_size=128):
            t_batch = torch.tensor(batch, dtype=torch.float32)

            reconstr = self._model(t_batch)
            loss = self._loss(reconstr, t_batch)
            train_losses.append(loss.item())

            self._opt.zero_grad()
            loss.backward()
            self._opt.step()

            self._logger.log_scalar("loss/train", loss.item(), epoch)

        return np.average(train_losses)

    def run_inference(self, n_samples: int = 5) -> None:
        """
        Run example of reccomendation inference.

        Args:
            n_samples: Number of movies to see recommendations for.
        """
        # Here we run model also on train samples, which is ok, as we mostly
        # be running the model also on train data in future.
        embs = np.zeros((self._data_loader.get_db_size(), self._model.emb_size))
        titles = []
        for i, (title, features) in enumerate(self._data_loader.get_samples_raw_features()):
            titles.append(title)
            embs[i, :] = self._model.encode(features).flatten()

            if i % 100 == 0:
                logging.info(f"Processing {i}-th entry")

        for _ in range(n_samples):
            i = random.randrange(embs.shape[0])
            print(f"Movie: {titles[i]}. Recommened movies: ")
            source_emb = np.expand_dims(embs[i, :], 0)
            dists = np.linalg.norm(embs - source_emb, axis=1)

            inds_sorted = np.argsort(dists)
            for i, idx_sim in enumerate(inds_sorted[1:5]):
                print(f"\t{i+1})  {titles[idx_sim]}")
            print()
