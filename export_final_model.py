from pathlib import Path
import json

import tensorflow as tf

from src.data import get_class_names
from src.model import build_model


PROJECT_ROOT = Path(__file__).resolve().parent

CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "runs"
    / "run_07_canonical"
    / "best.weights.h5"
)

MODELS_DIRECTORY = PROJECT_ROOT / "models"
FINAL_MODEL_PATH = MODELS_DIRECTORY / "final_model.keras"
CLASS_NAMES_PATH = MODELS_DIRECTORY / "class_names.json"


def main() -> None:
    tf.keras.utils.set_random_seed(42)

    if not CHECKPOINT_PATH.exists():
        raise FileNotFoundError(
            f"Canonical checkpoint was not found:\n"
            f"{CHECKPOINT_PATH}"
        )

    MODELS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    class_names = get_class_names()

    if len(class_names) != 10:
        raise ValueError(
            f"Expected 10 classes, but found "
            f"{len(class_names)}."
        )

    print("=" * 60)
    print("EXPORTING FINAL CESPPL MODEL")
    print("=" * 60)

    print(f"\nCheckpoint:\n{CHECKPOINT_PATH}")
    print(f"\nNumber of classes: {len(class_names)}")

    # This must match the canonical Run 07 configuration.
    model = build_model(
        backbone_name="efficientnetb0",
        num_classes=len(class_names),
        img_size=224,
        dropout=0.3,
        learning_rate=1e-5,
        use_augmentation=True,
        augmentation_mode="strong_lighting",
        backbone_trainable=False,
    )

    print("\nLoading canonical weights...")
    model.load_weights(str(CHECKPOINT_PATH))
    print("Canonical weights loaded successfully.")

    print("\nSaving complete model...")
    model.save(str(FINAL_MODEL_PATH))

    class_mapping = {
        str(index): class_name
        for index, class_name in enumerate(class_names)
    }

    with open(
        CLASS_NAMES_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            class_mapping,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print("\nExport completed successfully.")
    print(f"\nFull model:\n{FINAL_MODEL_PATH}")
    print(f"\nClass mapping:\n{CLASS_NAMES_PATH}")

    model_size_mb = (
        FINAL_MODEL_PATH.stat().st_size
        / (1024 * 1024)
    )

    print(f"\nModel size: {model_size_mb:.2f} MB")

    print("\nClass order:")

    for index, class_name in enumerate(class_names):
        print(f"{index}: {class_name}")


if __name__ == "__main__":
    main()