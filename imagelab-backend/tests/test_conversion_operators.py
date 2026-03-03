import numpy as np
import pytest

from app.operators.conversions.bgr_to_hsv import BgrToHsv
from app.operators.conversions.bgr_to_lab import BgrToLab
from app.operators.conversions.bgr_to_ycrcb import BgrToYcrcb
from app.operators.conversions.channel_split import ChannelSplit
from app.operators.conversions.color_maps import ColorMaps
from app.operators.conversions.color_to_binary import ColorToBinary
from app.operators.conversions.gray_image import GrayImage
from app.operators.conversions.gray_to_binary import GrayToBinary
from app.operators.conversions.hsv_to_bgr import HsvToBgr
from app.operators.conversions.lab_to_bgr import LabToBgr
from app.operators.conversions.ycrcb_to_bgr import YcrcbToBgr


@pytest.fixture
def color_image():
    return np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)


@pytest.fixture
def grayscale_image():
    return np.random.randint(0, 256, (100, 100), dtype=np.uint8)


@pytest.fixture
def rgba_image():
    return np.random.randint(0, 256, (100, 100, 4), dtype=np.uint8)


# GrayImage


class TestGrayImage:
    def test_output_is_grayscale(self, color_image):
        result = GrayImage({}).compute(color_image)
        assert len(result.shape) == 2

    def test_output_shape(self, color_image):
        result = GrayImage({}).compute(color_image)
        assert result.shape == (100, 100)

    def test_output_is_uint8(self, color_image):
        result = GrayImage({}).compute(color_image)
        assert result.dtype == np.uint8


# GrayToBinary


class TestGrayToBinary:
    def test_default_params_output_shape(self, grayscale_image):
        result = GrayToBinary({}).compute(grayscale_image)
        assert result.shape == grayscale_image.shape

    def test_custom_threshold_output_shape(self, grayscale_image):
        result = GrayToBinary({"thresholdValue": 127, "maxValue": 255}).compute(grayscale_image)
        assert result.shape == grayscale_image.shape

    def test_output_is_binary_values(self, grayscale_image):
        result = GrayToBinary({"thresholdValue": 100, "maxValue": 255}).compute(grayscale_image)
        unique_values = np.unique(result)
        assert all(v in [0, 255] for v in unique_values)

    def test_output_is_uint8(self, grayscale_image):
        result = GrayToBinary({"thresholdValue": 127, "maxValue": 255}).compute(grayscale_image)
        assert result.dtype == np.uint8


# ColorToBinary


class TestColorToBinary:
    def test_default_params_output_shape(self, color_image):
        result = ColorToBinary({}).compute(color_image)
        assert result.shape == (100, 100)

    def test_output_is_grayscale(self, color_image):
        result = ColorToBinary({}).compute(color_image)
        assert len(result.shape) == 2

    def test_output_is_binary_values(self, color_image):
        result = ColorToBinary({"thresholdValue": 127, "maxValue": 255}).compute(color_image)
        unique_values = np.unique(result)
        assert all(v in [0, 255] for v in unique_values)

    def test_threshold_binary_inv(self, color_image):
        result = ColorToBinary(
            {"thresholdType": "threshold_binary_inv", "thresholdValue": 127, "maxValue": 255}
        ).compute(color_image)
        assert result.shape == (100, 100)

    def test_output_is_uint8(self, color_image):
        result = ColorToBinary({"thresholdValue": 127, "maxValue": 255}).compute(color_image)
        assert result.dtype == np.uint8


# ColorMaps


class TestColorMaps:
    @pytest.mark.parametrize(
        "colormap", ["HOT", "AUTUMN", "BONE", "COOL", "HSV", "JET", "OCEAN", "PARULA", "PINK", "RAINBOW"]
    )
    def test_all_colormaps_output_shape(self, grayscale_image, colormap):
        result = ColorMaps({"type": colormap}).compute(grayscale_image)
        assert result.shape[:2] == grayscale_image.shape[:2]

    def test_default_colormap_output_shape(self, grayscale_image):
        result = ColorMaps({}).compute(grayscale_image)
        assert result.shape[:2] == grayscale_image.shape[:2]

    def test_output_is_bgr(self, grayscale_image):
        result = ColorMaps({}).compute(grayscale_image)
        assert result.shape[2] == 3

    def test_output_is_uint8(self, grayscale_image):
        result = ColorMaps({}).compute(grayscale_image)
        assert result.dtype == np.uint8


# ChannelSplit


class TestChannelSplit:
    @pytest.mark.parametrize("channel", ["RED", "GREEN", "BLUE"])
    def test_all_channels_output_shape(self, color_image, channel):
        result = ChannelSplit({"channel": channel}).compute(color_image)
        assert result.shape == (100, 100)

    def test_default_channel_is_red(self, color_image):
        result = ChannelSplit({}).compute(color_image)
        assert result.shape == (100, 100)

    def test_output_is_uint8(self, color_image):
        result = ChannelSplit({}).compute(color_image)
        assert result.dtype == np.uint8

    def test_grayscale_input_returned_as_is(self, grayscale_image):
        result = ChannelSplit({}).compute(grayscale_image)
        np.testing.assert_array_equal(result, grayscale_image)

    def test_rgba_input_splits_correctly(self, rgba_image):
        result = ChannelSplit({"channel": "BLUE"}).compute(rgba_image)
        assert result.shape == (100, 100)


# BgrToHsv


class TestBgrToHsv:
    def test_output_shape(self, color_image):
        result = BgrToHsv({}).compute(color_image)
        assert result.shape == color_image.shape

    def test_grayscale_input_converted_to_bgr(self, grayscale_image):
        result = BgrToHsv({}).compute(grayscale_image)
        assert result.shape[2] == 3

    def test_rgba_input_converted_to_bgr(self, rgba_image):
        result = BgrToHsv({}).compute(rgba_image)
        assert result.shape[2] == 3

    def test_output_is_uint8(self, color_image):
        result = BgrToHsv({}).compute(color_image)
        assert result.dtype == np.uint8


# HsvToBgr


class TestHsvToBgr:
    def test_roundtrip_output_shape(self, color_image):
        hsv = BgrToHsv({}).compute(color_image)
        result = HsvToBgr({}).compute(hsv)
        assert result.shape == color_image.shape

    def test_grayscale_input_returns_bgr(self, grayscale_image):
        result = HsvToBgr({}).compute(grayscale_image)
        assert result.shape[2] == 3

    def test_output_is_uint8(self, color_image):
        hsv = BgrToHsv({}).compute(color_image)
        result = HsvToBgr({}).compute(hsv)
        assert result.dtype == np.uint8


# BgrToLab


class TestBgrToLab:
    def test_output_shape(self, color_image):
        result = BgrToLab({}).compute(color_image)
        assert result.shape == color_image.shape

    def test_grayscale_input_converted_to_bgr(self, grayscale_image):
        result = BgrToLab({}).compute(grayscale_image)
        assert result.shape[2] == 3

    def test_rgba_input_converted_to_bgr(self, rgba_image):
        result = BgrToLab({}).compute(rgba_image)
        assert result.shape[2] == 3

    def test_output_is_uint8(self, color_image):
        result = BgrToLab({}).compute(color_image)
        assert result.dtype == np.uint8


# LabToBgr


class TestLabToBgr:
    def test_roundtrip_output_shape(self, color_image):
        lab = BgrToLab({}).compute(color_image)
        result = LabToBgr({}).compute(lab)
        assert result.shape == color_image.shape

    def test_grayscale_input_returns_bgr(self, grayscale_image):
        result = LabToBgr({}).compute(grayscale_image)
        assert result.shape[2] == 3

    def test_output_is_uint8(self, color_image):
        lab = BgrToLab({}).compute(color_image)
        result = LabToBgr({}).compute(lab)
        assert result.dtype == np.uint8


# BgrToYcrcb


class TestBgrToYcrcb:
    def test_output_shape(self, color_image):
        result = BgrToYcrcb({}).compute(color_image)
        assert result.shape == color_image.shape

    def test_grayscale_input_converted_to_bgr(self, grayscale_image):
        result = BgrToYcrcb({}).compute(grayscale_image)
        assert result.shape[2] == 3

    def test_rgba_input_converted_to_bgr(self, rgba_image):
        result = BgrToYcrcb({}).compute(rgba_image)
        assert result.shape[2] == 3

    def test_output_is_uint8(self, color_image):
        result = BgrToYcrcb({}).compute(color_image)
        assert result.dtype == np.uint8


# YcrcbToBgr


class TestYcrcbToBgr:
    def test_roundtrip_output_shape(self, color_image):
        ycrcb = BgrToYcrcb({}).compute(color_image)
        result = YcrcbToBgr({}).compute(ycrcb)
        assert result.shape == color_image.shape

    def test_grayscale_input_returns_bgr(self, grayscale_image):
        result = YcrcbToBgr({}).compute(grayscale_image)
        assert result.shape[2] == 3

    def test_output_is_uint8(self, color_image):
        ycrcb = BgrToYcrcb({}).compute(color_image)
        result = YcrcbToBgr({}).compute(ycrcb)
        assert result.dtype == np.uint8
