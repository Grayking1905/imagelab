import cv2
import numpy as np

from app.operators.base import BaseOperator


class KMeansSegmentation(BaseOperator):
    def compute(self, image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        k = int(self.params.get("k", 3))
        k = max(2, min(10, k))

        max_iter = int(self.params.get("max_iter", 100))
        epsilon = float(self.params.get("epsilon", 0.2))

        pixel_values = image.reshape((-1, 3))
        pixel_values = np.float32(pixel_values)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, max_iter, epsilon)
        _, labels, centers = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        centers = np.uint8(centers)
        segmented = centers[labels.flatten()]
        result = segmented.reshape(image.shape)

        return result
