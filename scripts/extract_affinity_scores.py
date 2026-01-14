import csv
import json
import os
from pathlib import Path

INPUT_DIR = "/apps/boltz/results/outputs/boltz_results_inputs/predictions"
OUTPUT_FILE = "/apps/boltz/results/outputs/affinity_scores.csv"


def extract_scores(root_dir: str, output_file: str) -> None:
    results = []

    print(f"Scanning directory: {root_dir}")

    if not Path(root_dir).exists():
        raise FileNotFoundError(f"Directory '{root_dir}' does not exist.")

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.startswith("affinity_") and filename.endswith(".json"):
                json_path = os.path.join(dirpath, filename)

                # Assume prediction name is the directory name
                prediction_name = os.path.basename(dirpath)

                with Path(json_path).open() as f:
                    data = json.load(f)

                pred_value = data.get("affinity_pred_value")
                prob_binary = data.get("affinity_probability_binary")

                results.append({
                    "name": prediction_name,
                    "affinity_pred_value": pred_value,
                    "affinity_probability_binary": prob_binary,
                })

    # Write to CSV
    keys = ["name", "affinity_pred_value", "affinity_probability_binary"]
    # Sort by prediction name for better readability
    results.sort(key=lambda x: x["name"])

    with Path(output_file).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    print(f"Successfully extracted {len(results)} records to {output_file}")


def main() -> None:
    extract_scores(INPUT_DIR, OUTPUT_FILE)


if __name__ == "__main__":
    main()
