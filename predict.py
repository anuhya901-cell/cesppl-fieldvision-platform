from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import pandas as pd
from PIL import Image, UnidentifiedImageError

from src.classifier import load_model, predict_image


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_TEST_CSV = REPO_ROOT / "Week-09" / "test.csv"
DEFAULT_IMAGE_DIR = REPO_ROOT / "data" / "cesppl_processed"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the final CESPPL model on images listed in a split CSV."
    )

    parser.add_argument(
        "--split_csv",
        type=str,
        default=str(DEFAULT_TEST_CSV),
        help="CSV file containing filename and class columns.",
    )

    parser.add_argument(
        "--image_dir",
        type=str,
        default=str(DEFAULT_IMAGE_DIR),
        help="Root directory containing processed images.",
    )

    parser.add_argument(
        "--output_csv",
        type=str,
        default="final_results/service_predictions.csv",
        help="Path for prediction results.",
    )

    parser.add_argument(
        "--benchmark_images",
        type=int,
        default=20,
        help="Number of images used for latency measurement.",
    )

    parser.add_argument(
        "--expected_accuracy",
        type=float,
        default=None,
        help="Expected accuracy from evaluate.py, for example 0.9503.",
    )

    parser.add_argument(
        "--accuracy_tolerance",
        type=float,
        default=0.002,
        help="Maximum permitted difference from expected accuracy.",
    )

    return parser.parse_args()


def find_image_path(
    filename: str,
    image_dir: Path,
    split_csv: Path,
) -> Path:
    filename_path = Path(filename)

    possible_paths = []

    if filename_path.is_absolute():
        possible_paths.append(filename_path)

    possible_paths.extend(
        [
            image_dir / filename_path,
            REPO_ROOT / filename_path,
            split_csv.parent / filename_path,
        ]
    )

    for path in possible_paths:
        if path.exists():
            return path.resolve()

    attempted = "\n".join(f"- {path}" for path in possible_paths)

    raise FileNotFoundError(
        f"Image not found for CSV entry:\n{filename}\n\n"
        f"Attempted paths:\n{attempted}"
    )


def normalize_class_name(class_name: str) -> str:
    return str(class_name).strip().replace("_", " ")


def main() -> None:
    args = parse_arguments()

    split_csv = Path(args.split_csv).resolve()
    image_dir = Path(args.image_dir).resolve()
    output_csv = Path(args.output_csv).resolve()

    if not split_csv.exists():
        raise FileNotFoundError(
            f"Split CSV not found:\n{split_csv}"
        )

    if not image_dir.exists():
        raise FileNotFoundError(
            f"Image directory not found:\n{image_dir}"
        )

    dataframe = pd.read_csv(split_csv)

    required_columns = {"filename", "class"}

    if not required_columns.issubset(dataframe.columns):
        raise ValueError(
            f"{split_csv.name} must contain filename and class columns."
        )

    if dataframe.empty:
        raise ValueError(
            f"{split_csv.name} contains no rows."
        )

    dataframe = dataframe[["filename", "class"]].copy()

    dataframe["filename"] = (
        dataframe["filename"]
        .astype(str)
        .str.strip()
    )

    dataframe["class"] = (
        dataframe["class"]
        .astype(str)
        .map(normalize_class_name)
    )

    output_csv.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 65)
    print("CESPPL SERVICE PREDICTION CROSS-CHECK")
    print("=" * 65)

    print(f"\nSplit CSV:\n{split_csv}")
    print(f"\nImage directory:\n{image_dir}")
    print(f"\nImages listed: {len(dataframe)}")

    load_model()

    first_image_path = find_image_path(
        dataframe.iloc[0]["filename"],
        image_dir,
        split_csv,
    )

    print("\nRunning warm-up prediction...")

    with Image.open(first_image_path) as image:
        predict_image(image.copy())

    rows = []
    correct = 0
    processed = 0
    skipped = 0
    latency_values = []

    for index, record in dataframe.iterrows():
        filename = record["filename"]
        actual_class = record["class"]

        try:
            image_path = find_image_path(
                filename,
                image_dir,
                split_csv,
            )

            with Image.open(image_path) as image:
                image_copy = image.copy()

            start_time = time.perf_counter()

            top1, top1_conf, top_three = predict_image(
                image_copy
            )

            elapsed = time.perf_counter() - start_time

        except (
            FileNotFoundError,
            OSError,
            UnidentifiedImageError,
        ) as error:
            skipped += 1
            print(f"\nSkipped: {filename}")
            print(error)
            continue

        if len(latency_values) < args.benchmark_images:
            latency_values.append(elapsed)

        is_correct = top1 == actual_class

        if is_correct:
            correct += 1

        processed += 1

        rows.append(
            {
                "filename": filename,
                "actual": actual_class,
                "top1": top1,
                "top1_conf": f"{top1_conf:.8f}",
                "top2": top_three[1]["class_name"],
                "top2_conf": f"{top_three[1]['confidence']:.8f}",
                "top3": top_three[2]["class_name"],
                "top3_conf": f"{top_three[2]['confidence']:.8f}",
                "correct": is_correct,
            }
        )

        if processed % 50 == 0 or processed == len(dataframe):
            print(
                f"Processed {processed}/{len(dataframe)} images"
            )

    if processed == 0:
        raise RuntimeError(
            "No images were successfully processed."
        )

    fieldnames = [
        "filename",
        "actual",
        "top1",
        "top1_conf",
        "top2",
        "top2_conf",
        "top3",
        "top3_conf",
        "correct",
    ]

    with open(
        output_csv,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(rows)

    accuracy = correct / processed

    print("\n" + "=" * 65)
    print("RESULTS")
    print("=" * 65)

    print(f"\nProcessed images: {processed}")
    print(f"Skipped images: {skipped}")
    print(f"Correct predictions: {correct}")

    print(
        f"Service accuracy: {accuracy:.6f} "
        f"({accuracy * 100:.2f}%)"
    )

    if latency_values:
        average_latency_seconds = (
            sum(latency_values) / len(latency_values)
        )

        average_latency_ms = (
            average_latency_seconds * 1000
        )

        print(
            f"\nBenchmark images: "
            f"{len(latency_values)}"
        )

        print(
            f"Average prediction latency: "
            f"{average_latency_ms:.2f} ms/image"
        )

        print(
            f"Approximate throughput: "
            f"{1 / average_latency_seconds:.2f} images/second"
        )

    if args.expected_accuracy is not None:
        difference = abs(
            accuracy - args.expected_accuracy
        )

        print(
            f"\nExpected evaluate.py accuracy: "
            f"{args.expected_accuracy:.6f}"
        )

        print(
            f"Absolute difference: "
            f"{difference:.6f}"
        )

        if difference <= args.accuracy_tolerance:
            print(
                "\nCROSS-CHECK PASSED: "
                "serving accuracy matches evaluation accuracy."
            )
        else:
            raise RuntimeError(
                "\nCROSS-CHECK FAILED: serving accuracy differs "
                "from evaluate.py. Stop and inspect preprocessing."
            )

    print(f"\nPredictions saved to:\n{output_csv}")


if __name__ == "__main__":
    main()