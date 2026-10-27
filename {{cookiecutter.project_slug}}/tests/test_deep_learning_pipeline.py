import json
import subprocess
import sys
from pathlib import Path


def test_light_training_evaluation_and_inference(
    project_root: Path, tmp_path: Path
) -> None:
    output_dir = tmp_path / "run"
    train = subprocess.run(
        [
            sys.executable,
            "scripts/train.py",
            "--config",
            "configs/0_baselines/00_baseline_default.yaml",
            "--output-dir",
            str(output_dir),
            "--light",
        ],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
    )
    model_path = output_dir / "model.pt"
    assert model_path.is_file()
    assert "accuracy=" in train.stdout

    subprocess.run(
        [sys.executable, "scripts/evaluate.py", "--model", str(model_path)],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
    )
    metrics = json.loads((output_dir / "evaluation_metrics.json").read_text())
    assert metrics["evaluation_rows"] > 0
    assert 0.8 <= metrics["accuracy"] <= 1.0

    inference_path = tmp_path / "inference.csv"
    inference_path.write_text("x1,x2\n-1.0,-0.8\n1.0,0.8\n")
    predictions_path = output_dir / "predictions.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/infer.py",
            "--model",
            str(model_path),
            "--input",
            str(inference_path),
            "--output",
            str(predictions_path),
        ],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
    )
    predictions = json.loads(predictions_path.read_text())
    assert len(predictions) == 2
    assert {item["prediction"] for item in predictions} == {0, 1}
    assert all(0 <= item["probability"] <= 1 for item in predictions)
