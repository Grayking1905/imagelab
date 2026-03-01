import cv2
import numpy as np

from app.operators.base import BaseOperator


class SepiaFilter(BaseOperator):
    def compute(self, image: np.ndarray) -> np.ndarray:
        intensity = float(self.params.get("intensity", 1.0))
        intensity = max(0.0, min(1.0, intensity))

        if len(image.shape) == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        # Sepia color matrix
        sepia_matrix = np.array(
            [
                [0.131, 0.534, 0.272],
                [0.168, 0.686, 0.349],
                [0.189, 0.769, 0.393],
            ],
            dtype=np.float32,
        )

        sepia = cv2.transform(image.astype(np.float32), sepia_matrix)
        sepia = np.clip(sepia, 0, 255).astype(np.uint8)

        result = cv2.addWeighted(image, 1.0 - intensity, sepia, intensity, 0)

        return result
