# Deep-learning scripts

- `train.py` trains the configured PyTorch MLP and writes a checkpoint plus metrics.
- `evaluate.py` evaluates the exact held-out rows stored with the checkpoint.
- `infer.py` writes probabilities and class predictions for a numeric CSV.

Use `--light` while iterating. The end-to-end path is exercised by
`tests/test_deep_learning_pipeline.py`.
