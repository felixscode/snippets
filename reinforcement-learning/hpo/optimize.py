import gc
import logging
import os
from functools import partial
from typing import Dict

import optuna
from heracless import as_dict, from_dict
from heracless.utils.cfg_tree import as_lowercase
from optuna import Trial

from your_package import train
from your_package.hpo.sample import sample as sample_hyperparameters
from your_package.types import Config
from your_package.utils import get_logger


def disable_logging(config: Dict) -> Config:
    """
    Disable logging in the configuration.

    Args:
        config (Config): The configuration object.

    Returns:
        Config: The modified configuration object.
    """
    config["agent"]["log_level"] = "ERROR"
    config["agent"]["model"]["log_level"] = "ERROR"
    config["agent"]["model"]["train_verbosity"] = 0
    config["default_loglevel"] = "ERROR"
    config["training"]["evaluation"]["eval_verbosity"] = 0
    logging.debug(f"Disabled logging")
    return config


def disable_model_saves(config: Dict) -> Dict:
    """
    Disable model saves in the configuration.

    Args:
        config (Config): The configuration object.

    Returns:
        Config: The modified configuration object.
    """
    config["training"]["evaluation"]["safe_on_new_best"] = False
    config[as_lowercase(config["agent"]["repo"])]["location"] = None

    return config


def objective(config: dict, trial: Trial) -> float:
    """
    Objective function for hyperparameter optimization.
    sample hyperparameters, train the model and return the score.
    logs verbosity and models saving gets disabled

    Args:
        config (dict): The configuration dictionary.
        mode (str): The mode of the optimization.
        train_function (Callable): The function used for training.
        trial (Trial): The Optuna trial object.

    Returns:
        float: The score of the trial.
    """
    logging.info(f"Starting Trial {trial.number}")
    config = sample_hyperparameters(config, trial)
    config = disable_logging(config)
    config = disable_model_saves(config)
    trial.set_user_attr("config", config)
    config = from_dict(config, frozen=True)
    agent = None
    train_loglevel = "error"
    score, train_time = train(train_loglevel, config, agent)

    trial.set_user_attr("best_makespan", int(score))
    trial.set_user_attr("train_time", train_time / 360)
    logging.info(f"Finished Trial with Score: {score}, Train time: {train_time}")

    return score


def _is_valid_sqlite_db(db_string):
    """
    Check if the given string is a valid SQLite database.

    Args:
        db_string (str): The database string.

    Returns:
        bool: True if the database is valid, False otherwise.
    """
    if not db_string.startswith("sqlite:///"):
        raise ValueError("Invalid database string sqlite://<dir> expected")
    if not os.path.exists(db_string[10:]):
        raise ValueError(f"Database file {db_string[10:]} not found")


def _is_valid_remote_storage(location):
    """
    Check if the given location is a valid remote storage.

    Args:
        location (str): The location string.

    Returns:
        bool: True if the location is valid, False otherwise.
    """
    if not location.startswith("mysql+pymysql://"):
        raise ValueError(
            "Invalid remote storage location pattern: mysql+pymysql://<user>:<password>@<host>/<db> expected"
        )
    # check if mysql the database is pingable
    # this is a very basic check
    host = location.split("@")[1].split(":")[0]
    # if type(ping(host)) != float:
    #     raise ValueError(f"Can't ping server at {host}")


def map_config_to_storage(config: Config) -> optuna.storages.RDBStorage:
    """
    Map the configuration object to an Optuna storage object.

    Args:
        config (Config): The configuration object.

    Returns:
        optuna.storages.RDBStorage: The Optuna storage object.
    """
    storage_config = getattr(config.hpo, config.hpo.storage)
    # error if the storage deffinition is not found is quite generic
    # so we need to check if the storage is defined in the config
    if config.hpo.storage == "local_storage":
        _is_valid_sqlite_db(storage_config.location)
    if config.hpo.storage == "remote_storage":
        _is_valid_remote_storage(storage_config.location)

    return optuna.storages.RDBStorage(url=storage_config.location)


def make_study(config: Config) -> optuna.study.Study:
    """
    Create an Optuna study.

    Args:
        config (Config): The configuration object.

    Returns:
        optuna.study.Study: The Optuna study object.
    """
    storage = map_config_to_storage(config)
    study_name = config.hpo.study_name
    return optuna.create_study(
        direction="minimize",  # minimize makespan
        study_name=study_name,
        storage=storage,
        load_if_exists=True,
    )


def run(log_level, config: Config) -> None:
    """
    Run hyperparameter optimization.

    Args:
        config (Config): The configuration object.
        mode (str): The mode of the optimization.
        train_function (Callable): The function used for training.

    Returns:
        None
    """
    logger = get_logger("hpo", log_level)
    logger.info("Starting HPO")
    study = make_study(config)
    config_dict = as_dict(config)  # convert to dict to make it serializable
    objective_function = partial(objective, config_dict)
    study.optimize(
        objective_function,
        n_trials=config.hpo.n_trials,
        callbacks=[lambda study, trial: gc.collect()],
    )

    logging.info("finished hpo")
    logging.info(f"Best trial: {study.best_trial}")


if __name__ == "__main__":
    from your_package.utils.load_config import load_agent_config

    log_level = "DEBUG"
    config = load_agent_config("./data/configs/example.yaml")
    run("INFO", config)
