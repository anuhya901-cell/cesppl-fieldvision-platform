from __future__ import annotations

from datetime import date
from io import BytesIO
from itertools import count

import pytest
from PIL import Image

import src.pipeline as pipeline


def make_test_image_bytes(
    size: tuple[int, int] = (2000, 1200),
) -> bytes:
    """Create a valid test image entirely in memory."""

    image = Image.new(
        mode="RGB",
        size=size,
        color=(90, 150, 110),
    )

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG",
    )

    return buffer.getvalue()


@pytest.fixture
def fake_pipeline_dependencies(monkeypatch):
    """
    Replace the real model and database with predictable test doubles.

    The pipeline's validation, resizing, JPEG conversion and result handling
    are still tested, but the tests do not need to load the full ML model.
    """

    filename_counter = count(1)
    stored_rows = []
    stored_images = {}

    def fake_predict_image(image):
        assert isinstance(image, Image.Image)
        assert image.mode == "RGB"
        assert max(image.size) <= 1600

        return {
            "class_name": "BIN WASHING",
            "confidence": 0.9734,
        }

    def fake_insert_upload(
        image_bytes,
        class_name,
        confidence,
    ):
        sequence_number = next(filename_counter)
        today = date.today().isoformat()

        filename = (
            f"{class_name.replace(' ', '_')}_"
            f"{today}_120000_{sequence_number}.jpg"
        )

        row = {
            "filename": filename,
            "class_name": class_name,
            "confidence": confidence,
            "uploaded_at": f"{today}T12:00:00",
        }

        stored_rows.append(row)
        stored_images[filename] = image_bytes

        return row

    monkeypatch.setattr(
        pipeline.classifier,
        "predict_image",
        fake_predict_image,
    )

    monkeypatch.setattr(
        pipeline.db,
        "insert_upload",
        fake_insert_upload,
    )

    return {
        "rows": stored_rows,
        "images": stored_images,
    }


def test_valid_image_produces_stored_row(
    fake_pipeline_dependencies,
):
    image_bytes = make_test_image_bytes()

    result = pipeline.classify_and_store(image_bytes)

    today = date.today().isoformat()

    assert result["class_name"] == "BIN WASHING"
    assert result["confidence"] == pytest.approx(0.9734)

    assert result["filename"].startswith("BIN_WASHING")
    assert today in result["filename"]

    assert result["uploaded_at"].startswith(today)

    assert len(fake_pipeline_dependencies["rows"]) == 1


def test_stored_image_is_jpeg_and_capped(
    fake_pipeline_dependencies,
):
    original_bytes = make_test_image_bytes(
        size=(2400, 1800),
    )

    result = pipeline.classify_and_store(original_bytes)

    stored_bytes = fake_pipeline_dependencies["images"][
        result["filename"]
    ]

    with Image.open(BytesIO(stored_bytes)) as stored_image:
        assert stored_image.format == "JPEG"
        assert stored_image.mode == "RGB"
        assert max(stored_image.size) <= 1600


def test_junk_bytes_raise_invalid_image_error(
    fake_pipeline_dependencies,
):
    junk_bytes = b"This is not an image."

    with pytest.raises(
        pipeline.InvalidImageError,
        match="valid supported image",
    ):
        pipeline.classify_and_store(junk_bytes)


def test_empty_bytes_raise_invalid_image_error(
    fake_pipeline_dependencies,
):
    with pytest.raises(
        pipeline.InvalidImageError,
        match="empty",
    ):
        pipeline.classify_and_store(b"")


def test_two_rapid_calls_produce_distinct_filenames(
    fake_pipeline_dependencies,
):
    image_bytes = make_test_image_bytes()

    first_result = pipeline.classify_and_store(image_bytes)
    second_result = pipeline.classify_and_store(image_bytes)

    assert first_result["filename"] != second_result["filename"]

    assert first_result["filename"].startswith("BIN_WASHING")
    assert second_result["filename"].startswith("BIN_WASHING")
    