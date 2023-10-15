import argparse
import logging
from datetime import datetime

from ml_content.trainers.base_trainer import BaseTrainer
from ml_content.utils.config import load_config
from ml_content.utils.logger import TBLogger

logging.basicConfig(level=logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser(prog="ml_content_trainer")
    parser.add_argument("--config", type=str, help="path to .py config")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    config = load_config(args.config)

    log_dir = "logs"
    experiment_name = "test"
    log_dir = f"{log_dir}/{experiment_name}"
    log_dir += datetime.now().strftime("%Y_%m_%d_%Hh%Mm%Ss")
    logger = TBLogger(log_dir)

    trainer = BaseTrainer(
        epochs=config.epochs,
        data_loader=config.data_loader,
        make_loss=config.make_loss,
        make_model_optimizer=config.make_model_optimizer,
        logger=logger,
        trainer_conf=config.trainer_conf,
    )
    trainer.train()

    # See couple of recommendations
    trainer.run_inference(n_samples=5)

    # Save feature extractor for later use
    config.feature_extractor.save("logs/feature_extractor.pickle")
