import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from {{ cookiecutter.project_slug }}.config import ExperimentConfig


@dataclass(frozen=True)
class TabularData:
    features: torch.Tensor
    targets: torch.Tensor | None
    feature_names: list[str]


class BinaryMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:  # ty: ignore[invalid-mutable-override]
        return self.layers(features).squeeze(-1)


def load_tabular_data(
    path: Path, target_column: str, *, require_target: bool = True
) -> TabularData:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"Missing CSV header in {path}")
        has_target = target_column in reader.fieldnames
        if require_target and not has_target:
            raise ValueError(f"Missing target column {target_column!r} in {path}")
        feature_names = [name for name in reader.fieldnames if name != target_column]
        rows = list(reader)

    if not feature_names or not rows:
        raise ValueError("Input data needs feature columns and at least one row")
    features = torch.tensor(
        [[float(row[name]) for name in feature_names] for row in rows],
        dtype=torch.float32,
    )
    targets = (
        torch.tensor([float(row[target_column]) for row in rows], dtype=torch.float32)
        if has_target
        else None
    )
    return TabularData(features, targets, feature_names)


def _accuracy(logits: torch.Tensor, targets: torch.Tensor) -> float:
    predictions = (torch.sigmoid(logits) >= 0.5).to(targets.dtype)
    return float((predictions == targets).float().mean().item())


def _load_checkpoint(model_path: Path) -> dict[str, Any]:
    checkpoint = torch.load(model_path, map_location="cpu", weights_only=True)
    if not isinstance(checkpoint, dict):
        raise ValueError(f"Invalid checkpoint: {model_path}")
    return checkpoint


def _model_from_checkpoint(checkpoint: dict[str, Any]) -> BinaryMLP:
    model = BinaryMLP(
        input_dim=int(checkpoint["input_dim"]),
        hidden_dim=int(checkpoint["hidden_dim"]),
    )
    state = checkpoint["model_state"]
    if not isinstance(state, dict):
        raise ValueError("Checkpoint model_state must be a mapping")
    model.load_state_dict(state)
    model.eval()
    return model


def train_experiment(
    config: ExperimentConfig, *, light: bool = False
) -> tuple[Path, dict[str, float | int]]:
    data = load_tabular_data(config.data_path, config.target_column)
    if data.targets is None or len(data.features) < 8:
        raise ValueError("Training data needs targets and at least 8 rows")
    if torch.unique(data.targets).numel() < 2:
        raise ValueError("Training data needs at least two target classes")

    torch.manual_seed(config.random_seed)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)
    generator = torch.Generator().manual_seed(config.random_seed)
    permutation = torch.randperm(len(data.features), generator=generator)
    test_rows = max(1, round(len(permutation) * config.test_size))
    if test_rows >= len(permutation) - 1:
        raise ValueError("test_size leaves too few training rows")
    test_indices = permutation[:test_rows]
    train_indices = permutation[test_rows:]

    # REVIEW REQUIRED: normalization is fit only on training rows.
    train_features = data.features[train_indices]
    feature_mean = train_features.mean(dim=0)
    feature_std = train_features.std(dim=0, unbiased=False).clamp_min(1e-6)
    normalized_train = (train_features - feature_mean) / feature_std
    train_targets = data.targets[train_indices]

    model = BinaryMLP(normalized_train.shape[1], config.hidden_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    loss_fn = nn.BCEWithLogitsLoss()
    loader = DataLoader(
        TensorDataset(normalized_train, train_targets),
        batch_size=min(config.batch_size, len(normalized_train)),
        shuffle=True,
        generator=generator,
    )
    epochs = min(config.epochs, 20) if light else config.epochs
    final_loss = 0.0
    model.train()
    for _ in range(epochs):
        for batch_features, batch_targets in loader:
            optimizer.zero_grad()
            loss = loss_fn(model(batch_features), batch_targets)
            loss.backward()
            optimizer.step()
            final_loss = float(loss.item())

    model.eval()
    with torch.no_grad():
        test_features = (data.features[test_indices] - feature_mean) / feature_std
        accuracy = _accuracy(model(test_features), data.targets[test_indices])

    config.output_dir.mkdir(parents=True, exist_ok=True)
    model_path = config.output_dir / "model.pt"
    torch.save(
        {
            "model_state": model.state_dict(),
            "input_dim": int(data.features.shape[1]),
            "hidden_dim": config.hidden_dim,
            "feature_names": data.feature_names,
            "feature_mean": feature_mean,
            "feature_std": feature_std,
            "data_path": str(config.data_path),
            "target_column": config.target_column,
            "test_indices": test_indices,
        },
        model_path,
    )
    metrics: dict[str, float | int] = {
        "accuracy": accuracy,
        "loss": final_loss,
        "train_rows": int(len(train_indices)),
        "evaluation_rows": int(len(test_indices)),
    }
    (config.output_dir / "train_metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    )
    return model_path, metrics


def evaluate_model(
    model_path: Path, *, output_dir: Path | None = None
) -> dict[str, float | int]:
    checkpoint = _load_checkpoint(model_path)
    data = load_tabular_data(
        Path(str(checkpoint["data_path"])), str(checkpoint["target_column"])
    )
    if data.targets is None:
        raise ValueError("Evaluation data has no targets")
    if data.feature_names != checkpoint["feature_names"]:
        raise ValueError("Evaluation feature columns differ from training")
    indices = checkpoint["test_indices"]
    if not isinstance(indices, torch.Tensor):
        raise ValueError("Checkpoint test_indices must be a tensor")

    # REVIEW REQUIRED: evaluation reuses the exact held-out rows and train statistics.
    features = (data.features[indices] - checkpoint["feature_mean"]) / checkpoint[
        "feature_std"
    ]
    with torch.no_grad():
        accuracy = _accuracy(
            _model_from_checkpoint(checkpoint)(features), data.targets[indices]
        )
    metrics: dict[str, float | int] = {
        "accuracy": accuracy,
        "evaluation_rows": int(len(indices)),
    }
    destination = output_dir or model_path.parent
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "evaluation_metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    )
    return metrics


def infer_file(model_path: Path, input_path: Path, output_path: Path) -> Path:
    checkpoint = _load_checkpoint(model_path)
    data = load_tabular_data(
        input_path, str(checkpoint["target_column"]), require_target=False
    )
    if data.feature_names != checkpoint["feature_names"]:
        raise ValueError("Inference feature columns differ from training")
    features = (data.features - checkpoint["feature_mean"]) / checkpoint["feature_std"]
    with torch.no_grad():
        probabilities = torch.sigmoid(_model_from_checkpoint(checkpoint)(features))
    records = [
        {
            "row": index,
            "probability": float(probability.item()),
            "prediction": int(probability.item() >= 0.5),
        }
        for index, probability in enumerate(probabilities)
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(records, indent=2) + "\n")
    return output_path
