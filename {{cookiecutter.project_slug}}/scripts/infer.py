#!/usr/bin/env python
import argparse
from pathlib import Path

from {{ cookiecutter.project_slug }}.deep_learning import infer_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a trained PyTorch model on a numeric CSV"
    )
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = args.output or args.model.parent / "predictions.json"
    result = infer_file(args.model, args.input, output_path)
    print(f"predictions={result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
