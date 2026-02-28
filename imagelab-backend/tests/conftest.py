"""
Shared fixtures for integration tests.

Key design decisions:
  - The app's lifespan tries to run Alembic migrations on startup, which requires
    a real PostgreSQL connection. We patch that out so tests run without any DB.
  - `tiny_png_b64` builds a valid 1×1 white PNG using only stdlib (struct + zlib)
    so no cv2/numpy import is needed at test-collection time.
"""

import base64
import struct
import zlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


def _make_png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    """Build a single PNG chunk: length + type + data + CRC."""
    chunk = chunk_type + data
    return struct.pack(">I", len(data)) + chunk + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)


def _build_1x1_white_png() -> bytes:
    """Construct a minimal valid 1×1 white RGB PNG using only stdlib."""
    signature = b"\x89PNG\r\n\x1a\n"

    # IHDR: width=1, height=1, bit_depth=8, color_type=2 (RGB), compression=0, filter=0, interlace=0
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    ihdr = _make_png_chunk(b"IHDR", ihdr_data)

    # IDAT: one scanline — filter byte 0x00 + RGB bytes for white (255, 255, 255)
    raw_scanline = b"\x00\xff\xff\xff"
    compressed = zlib.compress(raw_scanline)
    idat = _make_png_chunk(b"IDAT", compressed)

    # IEND
    iend = _make_png_chunk(b"IEND", b"")

    return signature + ihdr + idat + iend


@pytest.fixture(scope="session")
def tiny_png_b64() -> str:
    """1×1 white PNG encoded as base64 — valid input for all image tests."""
    return base64.b64encode(_build_1x1_white_png()).decode("utf-8")


@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    FastAPI TestClient with the Alembic migration step suppressed.

    The lifespan context manager in `app.main` calls `alembic.command.upgrade`.
    Patching it means the app starts cleanly without needing a running database,
    keeping tests fully independent of external services.
    """
    with patch("alembic.command.upgrade"):
        with TestClient(app) as c:
            yield c
