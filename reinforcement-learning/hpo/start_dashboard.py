import os
import optuna
from optuna_dashboard import wsgi  # make sure to install optuna-dashboard
import config_load_function as load_config  # edit this line to import your config object


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


config = load_config("./data/configs/example.yaml")
storage = map_config_to_storage(config)
application = wsgi(storage)
