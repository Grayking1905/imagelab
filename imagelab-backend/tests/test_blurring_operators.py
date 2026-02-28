import numpy as np
import pytest

from app.operators.blurring.blur import Blur
from app.operators.blurring.gaussian_blur import GaussianBlur
from app.operators.blurring.median_blur import MedianBlur


@pytest.fixture
def color_image():
    return np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)


@pytest.fixture
def grayscale_image():
    return np.random.randint(0, 256, (100, 100), dtype=np.uint8)


# Blur


class TestBlur:
    def test_default_params_output_shape(self, color_image):
        result = Blur({}).compute(color_image)
        assert result.shape == color_image.shape

    def test_custom_params_output_shape(self, color_image):
        result = Blur({"widthSize": 5, "heightSize": 5}).compute(color_image)
        assert result.shape == color_image.shape

    def test_grayscale_input(self, grayscale_image):
        result = Blur({}).compute(grayscale_image)
        assert result.shape == grayscale_image.shape

    def test_large_kernel(self, color_image):
        result = Blur({"widthSize": 15, "heightSize": 15}).compute(color_image)
        assert result.shape == color_image.shape

    def test_output_is_uint8(self, color_image):
        result = Blur({}).compute(color_image)
        assert result.dtype == np.uint8

    def test_blur_smooths_image(self, color_image):
        result = Blur({"widthSize": 9, "heightSize": 9}).compute(color_image)
        assert result.std() <= color_image.std()


# GaussianBlur


class TestGaussianBlur:
    def test_default_params_output_shape(self, color_image):
        result = GaussianBlur({}).compute(color_image)
        assert result.shape == color_image.shape

    def test_custom_params_output_shape(self, color_image):
        result = GaussianBlur({"widthSize": 5, "heightSize": 5}).compute(color_image)
        assert result.shape == color_image.shape

    def test_even_kernel_corrected_to_odd(self, color_image):
        result = GaussianBlur({"widthSize": 4, "heightSize": 4}).compute(color_image)
        assert result.shape == color_image.shape

    def test_grayscale_input(self, grayscale_image):
        result = GaussianBlur({}).compute(grayscale_image)
        assert result.shape == grayscale_image.shape

    def test_large_kernel(self, color_image):
        result = GaussianBlur({"widthSize": 15, "heightSize": 15}).compute(color_image)
        assert result.shape == color_image.shape

    def test_output_is_uint8(self, color_image):
        result = GaussianBlur({}).compute(color_image)
        assert result.dtype == np.uint8


# MedianBlur


class TestMedianBlur:
    def test_default_params_output_shape(self, color_image):
        result = MedianBlur({}).compute(color_image)
        assert result.shape == color_image.shape

    def test_custom_params_output_shape(self, color_image):
        result = MedianBlur({"kernelSize": 5}).compute(color_image)
        assert result.shape == color_image.shape

    def test_even_kernel_corrected_to_odd(self, color_image):
        result = MedianBlur({"kernelSize": 4}).compute(color_image)
        assert result.shape == color_image.shape

    def test_grayscale_input(self, grayscale_image):
        result = MedianBlur({}).compute(grayscale_image)
        assert result.shape == grayscale_image.shape

    def test_large_kernel(self, color_image):
        result = MedianBlur({"kernelSize": 11}).compute(color_image)
        assert result.shape == color_image.shape

    def test_output_is_uint8(self, color_image):
        result = MedianBlur({}).compute(color_image)
        assert result.dtype == np.uint8
