from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class ExperimentConfig:
    experiment_name: str
    data_path: Path
    target_column: str
    output_dir: Path
    random_seed: int = 42
    test_size: float = 0.25
    hidden_dim: int = 16
    epochs: int = 100
    learning_rate: float = 0.03
    batch_size: int = 8

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ExperimentConfig":
        config_path = Path(path)
        raw = yaml.safe_load(config_path.read_text())
        if not isinstance(raw, dict):
            raise ValueError(f"Expected a mapping in {config_path}")

        config = cls(
            experiment_name=str(raw["experiment_name"]),
            data_path=Path(raw["data_path"]),
            target_column=str(raw["target_column"]),
            output_dir=Path(raw["output_dir"]),
            random_seed=int(raw.get("random_seed", 42)),
            test_size=float(raw.get("test_size", 0.25)),
            hidden_dim=int(raw.get("hidden_dim", 16)),
            epochs=int(raw.get("epochs", 100)),
            learning_rate=float(raw.get("learning_rate", 0.03)),
            batch_size=int(raw.get("batch_size", 8)),
        )
        if not config.data_path.is_file():
            raise ValueError(f"Data file does not exist: {config.data_path}")
        if not 0 < config.test_size < 1:
            raise ValueError("test_size must be between 0 and 1")
        if min(config.hidden_dim, config.epochs, config.batch_size) < 1:
            raise ValueError("hidden_dim, epochs, and batch_size must be positive")
        if config.learning_rate <= 0:
            raise ValueError("learning_rate must be positive")
        return config
