from pathlib import Path

from src.pipeline import classify_and_store


TEST_IMAGE = Path(
    "data/cesppl_processed/BIN WASHING"
)

image_paths = sorted(
    path
    for path in TEST_IMAGE.iterdir()
    if path.suffix.lower() in {".jpg", ".jpeg", ".png"}
)

if not image_paths:
    raise FileNotFoundError(
        f"No test images found inside: {TEST_IMAGE}"
    )

selected_image = image_paths[0]

print("Selected image:", selected_image)

image_bytes = selected_image.read_bytes()

result = classify_and_store(image_bytes)

print("\nPipeline result:")
print(result)