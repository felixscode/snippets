from typing import Dict

from optuna import Trial


def get_hyp_dict(config: Dict) -> Dict:
    """
    Convert the PPO configuration to a dictionary.

    Args:
        config (Dict): The configuration dictionary.
        mode (str): The mode of the optimization.

    Returns:
        Dict: The PPO configuration dictionary.
    """
    return config["agent"]["model"]["hyperparameters"]


def set_hyp_dict(config: Dict, hyp_dict: Dict) -> Dict:
    """
    Set the PPO configuration from a dictionary.

    Args:
        config (Dict): The configuration dictionary.
        hyp_dict (Dict): The PPO configuration dictionary.

    Returns:
        Dict: The modified configuration dictionary.
    """
    config["agent"]["model"]["hyperparameters"] = hyp_dict
    return config


def sample(config: Dict, trial: Trial) -> Dict:
    """
    Sample hyperparameters for the given configuration.

    Args:
        config (Dict): The configuration dictionary.
        mode (str): The mode of the optimization.
        trial (Trial): The Optuna trial object.

    Returns:
        Config: The modified configuration object.
    """
    ppo_cfg_dict = get_hyp_dict(config)

    ppo_cfg_dict["learning_rate"] = trial.suggest_float(
        "learning_rate", 0.00005, 0.0003, step=0.000025
    )  # 0.0001-0.0005
    ppo_cfg_dict["ent_coef"] = trial.suggest_float("ent_coef", 0.01, 0.05, step=0.005)
    ppo_cfg_dict["n_steps"] = trial.suggest_categorical(
        "n_steps", [256, 512, 1024, 2048, 4096]
    )
    ppo_cfg_dict["n_epochs"] = trial.suggest_categorical(
        "n_epochs",
        [
            5,
            10,
            20,
        ],
    )
    ppo_cfg_dict["batch_size"] = trial.suggest_categorical("batch_size", [32, 64])
    ppo_cfg_dict["gamma"] = trial.suggest_categorical("gamma", [0.999, 0.9999, 1])
    ppo_cfg_dict["gae_lambda"] = trial.suggest_categorical(
        "gae_lambda", [0.99, 0.999, 1]
    )

    config_dict = set_hyp_dict(config, ppo_cfg_dict)
    config_dict["agent"]["environment"]["num_envs"] = trial.suggest_categorical(
        "num_envs", [1, 4, 8, 16]
    )
    return config_dict
