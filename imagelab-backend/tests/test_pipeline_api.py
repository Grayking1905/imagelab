"""
Integration tests for the /api/pipeline/execute endpoint.

These tests use FastAPI's TestClient to make real HTTP requests against the
application, covering the full request-response cycle: JSON parsing, base64
image decoding, pipeline step execution, result encoding, and error formatting.

All tests are independent — no external services (database, file system) required.
The `client` and `tiny_png_b64` fixtures are defined in conftest.py.
"""

import pytest
from fastapi.testclient import TestClient

URL = "/api/pipeline/execute"


# ─── Helpers ────────────────────────────────────────────────────────────────

def build_body(image: str, pipeline: list[dict], image_format: str = "png") -> dict:
    return {"image": image, "image_format": image_format, "pipeline": pipeline}


READIMAGE  = {"type": "basic_readimage",  "params": {}}
WRITEIMAGE = {"type": "basic_writeimage", "params": {}}
GRAYSCALE  = {"type": "imageconvertions_grayimage", "params": {}}
ROTATE     = {"type": "geometric_rotateimage",      "params": {"angle": "45", "scale": "1"}}
BLUR       = {"type": "blurring_applyblur",          "params": {"ksize": "3"}}
GAUSS_BLUR = {"type": "blurring_applygaussianblur",  "params": {"ksize": "3", "sigma": "0"}}
REFLECT    = {"type": "geometric_reflectimage",      "params": {"flipCode": "1"}}
BGR_HSV    = {"type": "imageconvertions_bgrtohsv",  "params": {}}
HSV_BGR    = {"type": "imageconvertions_hsvtobgr",  "params": {}}


# ─── Health check ───────────────────────────────────────────────────────────

def test_health(client: TestClient) -> None:
    """GET /api/health should return 200 and status ok."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ─── Successful pipelines ───────────────────────────────────────────────────

def test_successful_single_step(client: TestClient, tiny_png_b64: str) -> None:
    """A single real operator (grayscale) should succeed and return an image + timings."""
    body = build_body(tiny_png_b64, [READIMAGE, GRAYSCALE, WRITEIMAGE])
    response = client.post(URL, json=body)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data.get("image"), str) and len(data["image"]) > 0
    # Timing data must be present after a successful run
    assert data.get("timings") is not None
    assert data["timings"]["total_ms"] > 0
    assert len(data["timings"]["steps"]) == 1


def test_successful_multi_step(client: TestClient, tiny_png_b64: str) -> None:
    """Multiple chained operators should all execute and each appear in timings.steps."""
    body = build_body(tiny_png_b64, [READIMAGE, GRAYSCALE, ROTATE, WRITEIMAGE])
    response = client.post(URL, json=body)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data.get("timings") is not None
    # NOOP types are excluded — expect 2 real steps (grayscale + rotate)
    assert len(data["timings"]["steps"]) == 2


def test_noop_only_pipeline(client: TestClient, tiny_png_b64: str) -> None:
    """A pipeline with only NOOP blocks should succeed with zero timed steps."""
    body = build_body(tiny_png_b64, [READIMAGE, WRITEIMAGE])
    response = client.post(URL, json=body)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data.get("timings") is not None
    assert data["timings"]["steps"] == []


def test_large_pipeline(client: TestClient, tiny_png_b64: str) -> None:
    """Five different operators chained — timings.steps should have 5 entries."""
    # Use operators that are safe on a 1×1 image (no colour-space preconditions,
    # no size-dependent operations that could produce a 0×0 result)
    pipeline = [READIMAGE, BGR_HSV, HSV_BGR, BLUR, REFLECT, GAUSS_BLUR, WRITEIMAGE]
    body = build_body(tiny_png_b64, pipeline)
    response = client.post(URL, json=body)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True, f"Pipeline failed: {data.get('error')}"
    assert len(data["timings"]["steps"]) == 5


# ─── Error cases ────────────────────────────────────────────────────────────

def test_unknown_operator(client: TestClient, tiny_png_b64: str) -> None:
    """An unrecognised block type should return success=False with the operator name in the error."""
    body = build_body(tiny_png_b64, [READIMAGE, {"type": "nonexistent_operator", "params": {}}, WRITEIMAGE])
    response = client.post(URL, json=body)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "nonexistent_operator" in data.get("error", "")


def test_invalid_base64_image(client: TestClient) -> None:
    """A non-base64 image string should return success=False mentioning decode failure."""
    body = build_body("!!!not-valid-base64!!!", [READIMAGE, GRAYSCALE, WRITEIMAGE])
    response = client.post(URL, json=body)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data.get("error") is not None


def test_valid_base64_but_not_an_image(client: TestClient) -> None:
    """Valid base64 that decodes to non-image bytes should return success=False."""
    import base64
    garbage_b64 = base64.b64encode(b"this is not image data at all").decode()
    body = build_body(garbage_b64, [READIMAGE, GRAYSCALE, WRITEIMAGE])
    response = client.post(URL, json=body)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data.get("error") is not None


def test_missing_pipeline_field(client: TestClient, tiny_png_b64: str) -> None:
    """A request body missing the required `pipeline` field must return HTTP 422."""
    body = {"image": tiny_png_b64, "image_format": "png"}  # no 'pipeline' key
    response = client.post(URL, json=body)

    assert response.status_code == 422
