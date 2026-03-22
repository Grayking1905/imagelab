import base64

import cv2
import numpy as np


def decode_base64_image(b64: str) -> np.ndarray:
    data = base64.b64decode(b64)
    arr = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise ValueError("Could not decode image data")
    return image


def encode_image_base64(image: np.ndarray, fmt: str = "png", quality: int | None = None) -> str:
    params = []
    if quality is not None:
        if fmt.lower() in ("jpg", "jpeg"):
            params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        elif fmt.lower() == "webp":
            params = [cv2.IMWRITE_WEBP_QUALITY, quality]

    success, buf = cv2.imencode(f".{fmt}", image, params)
    if not success:
        raise ValueError(f"Could not encode image as {fmt}")
    return base64.b64encode(buf).decode("utf-8")
