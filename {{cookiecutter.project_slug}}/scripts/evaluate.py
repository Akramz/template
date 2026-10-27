#!/usr/bin/env python
import argparse
from pathlib import Path

from {{ cookiecutter.project_slug }}.deep_learning import evaluate_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a trained PyTorch model")
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    metrics = evaluate_model(args.model, output_dir=args.output_dir)
    print(f"accuracy={metrics['accuracy']:.3f}")
    print(f"evaluation_rows={metrics['evaluation_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
