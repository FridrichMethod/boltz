from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

AFFINITY_KEYS = ("affinity_pred_value", "affinity_probability_binary")

PREDICTIONS_DIR = Path("/apps/boltz/results/outputs/boltz_results_inputs/predictions")


def load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def extract_affinity(prediction_dir: Path, dir_name: str) -> tuple[float, float]:
    affinity_path = prediction_dir / f"affinity_{dir_name}.json"

    affinity_data = load_json(affinity_path)

    return (
        affinity_data[AFFINITY_KEYS[0]],
        affinity_data[AFFINITY_KEYS[1]],
    )


def flatten_pair_chains_iptm(value: dict[str, float | dict[str, float]]) -> dict[str, float]:
    flattened: dict[str, float] = {}
    for outer_key, inner in value.items():
        if isinstance(inner, dict):
            for inner_key, inner_value in inner.items():
                flattened[f"pair_chains_iptm_{outer_key}_{inner_key}"] = inner_value
        else:
            flattened[f"pair_chains_iptm_{outer_key}"] = inner
    return flattened


def extract_confidence(confidence_path: Path) -> dict[str, float]:
    confidence_data = load_json(confidence_path)
    row: dict[str, float] = {}
    for key, value in confidence_data.items():
        if key == "chains_ptm":
            continue
        if key == "pair_chains_iptm":
            row.update(flatten_pair_chains_iptm(value))
            continue
        row[key] = value
    return row


def iter_prediction_dirs(predictions_dir: Path) -> list[Path]:
    return sorted([path for path in predictions_dir.iterdir() if path.is_dir()])


def average_metrics(confidence_rows: list[dict[str, float]]) -> dict[str, float]:
    """Average numeric metrics across confidence rows.

    Parameters
    ----------
    confidence_rows : list[dict[str, float]]
        List of confidence metric dictionaries.

    Returns
    -------
    dict[str, float]
        Dict of averaged metrics.
    """
    series_list = [pd.Series(row, dtype="float64") for row in confidence_rows]
    averaged = pd.concat(series_list, axis=1).mean(axis=1)
    return pd.Series(averaged).to_dict()


def build_rows(predictions_dir: Path) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    prediction_dirs = iter_prediction_dirs(predictions_dir)

    for prediction_dir in prediction_dirs:
        dir_name = prediction_dir.name
        affinity_value, affinity_prob = extract_affinity(prediction_dir, dir_name)

        confidence_files = sorted(prediction_dir.glob(f"confidence_{dir_name}_model_*.json"))

        confidence_rows = [
            extract_confidence(confidence_path) for confidence_path in confidence_files
        ]
        averaged_confidence = average_metrics(confidence_rows)
        row = {
            "prediction_name": dir_name,
            AFFINITY_KEYS[0]: affinity_value,
            AFFINITY_KEYS[1]: affinity_prob,
        }
        row.update(averaged_confidence)
        rows.append(row)
    return rows


def main() -> None:
    output_csv = PREDICTIONS_DIR.parent / "predictions_summary.csv"
    rows = build_rows(PREDICTIONS_DIR)
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)

    print(f"Wrote {len(df)} rows to {output_csv}")


if __name__ == "__main__":
    main()
