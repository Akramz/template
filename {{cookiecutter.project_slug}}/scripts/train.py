#!/usr/bin/env python
import argparse
from dataclasses import replace
from pathlib import Path

from {{ cookiecutter.project_slug }}.config import ExperimentConfig
from {{ cookiecutter.project_slug }}.deep_learning import train_experiment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the configured PyTorch model")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--light", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = ExperimentConfig.from_yaml(args.config)
    if args.output_dir:
        config = replace(config, output_dir=args.output_dir)
    model_path, metrics = train_experiment(config, light=args.light)
    print(f"model={model_path}")
    print(f"accuracy={metrics['accuracy']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
