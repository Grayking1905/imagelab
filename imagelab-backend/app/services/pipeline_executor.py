import time

import cv2
import numpy as np

from app.models.pipeline import (
    DebugStepState,
    PipelineRequest,
    PipelineResponse,
    PipelineTimings,
    StepTiming,
)
from app.operators.registry import get_operator
from app.utils.image import decode_base64_image, encode_image_base64

NOOP_TYPES = {"basic_readimage", "basic_writeimage", "border_for_all", "border_each_side"}

DEBUG_ENCODE_FORMAT = "jpeg"
DEBUG_JPEG_QUALITY = 70
MAX_DEBUG_DIM = 512
MAX_DEBUG_STEPS = 25


def _thumbnail_for_debug(image: np.ndarray) -> np.ndarray:
    """Resize image to fit within MAX_DEBUG_DIM for compact debug snapshots."""
    h, w = image.shape[:2]
    if max(h, w) <= MAX_DEBUG_DIM:
        return image
    scale = MAX_DEBUG_DIM / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def _encode_debug_image(image: np.ndarray) -> str:
    """Encode an intermediate image as a compressed JPEG thumbnail."""
    thumb = _thumbnail_for_debug(image)
    # Ensure the image has 3 channels for JPEG encoding
    if len(thumb.shape) == 2:
        thumb = cv2.cvtColor(thumb, cv2.COLOR_GRAY2BGR)
    elif thumb.shape[2] == 4:
        thumb = cv2.cvtColor(thumb, cv2.COLOR_BGRA2BGR)
    return encode_image_base64(thumb, DEBUG_ENCODE_FORMAT, quality=DEBUG_JPEG_QUALITY)


# Thread-safety: this function is safe to call concurrently from FastAPI's
# threadpool. All processing state (image array, operator instances, encoded
# output) is local to each invocation. The module-level NOOP_TYPES set and
# OPERATOR_REGISTRY dict are read-only after import and never mutated.
def execute_pipeline(request: PipelineRequest) -> PipelineResponse:
    """
    Execute the image-processing pipeline described by *request*.

    Returns a PipelineResponse that always includes a ``timings`` field
    populated with every step that completed before the function returned,
    even when the response indicates failure.  This allows callers to
    inspect partial execution progress on error.
    """
    t_start_total = time.perf_counter()
    step_timings: list[StepTiming] = []
    debug_states: list[DebugStepState] = []

    try:
        image = decode_base64_image(request.image)
    except Exception as e:
        t_fail = time.perf_counter()
        return PipelineResponse(
            success=False,
            error=f"Failed to decode image: {e}",
            step=0,
            timings=PipelineTimings(total_ms=(t_fail - t_start_total) * 1000, steps=step_timings),
        )

    # Step 0: capture the original decoded image as the "before anything" state
    if request.debug:
        debug_states.append(
            DebugStepState(
                step=0,
                block_id=None,
                operator_type="original",
                image=_encode_debug_image(image),
                duration_ms=0.0,
            )
        )

    for i, step in enumerate(request.pipeline):
        if step.type in NOOP_TYPES:
            continue

        operator_cls = get_operator(step.type)
        if operator_cls is None:
            t_fail = time.perf_counter()
            return PipelineResponse(
                success=False,
                error=f"Unknown operator '{step.type}' at step {i + 1}",
                step=i + 1,
                timings=PipelineTimings(total_ms=(t_fail - t_start_total) * 1000, steps=step_timings),
                debug_states=debug_states if request.debug else None,
            )

        try:
            t_step_start = time.perf_counter()
            operator = operator_cls(step.params)
            image = operator.compute(image)
            t_step_end = time.perf_counter()
            step_ms = (t_step_end - t_step_start) * 1000
            step_timings.append(StepTiming(step=i + 1, operator_type=step.type, duration_ms=step_ms))

            # Debug injection: capture this step's output
            if request.debug and len(debug_states) < MAX_DEBUG_STEPS:
                debug_states.append(
                    DebugStepState(
                        step=i + 1,
                        block_id=step.id,
                        operator_type=step.type,
                        image=_encode_debug_image(image),
                        duration_ms=step_ms,
                    )
                )
        except Exception as e:
            t_fail = time.perf_counter()
            return PipelineResponse(
                success=False,
                error=f"Error in step {i + 1} ({step.type}): {type(e).__name__}: {e}",
                step=i + 1,
                timings=PipelineTimings(total_ms=(t_fail - t_start_total) * 1000, steps=step_timings),
                debug_states=debug_states if request.debug else None,
            )

    try:
        encoded = encode_image_base64(image, request.image_format)
    except Exception as e:
        t_fail = time.perf_counter()
        error_msg = f"Failed to encode result: {type(e).__name__}: {e}"
        return PipelineResponse(
            success=False,
            error=error_msg,
            step=len(request.pipeline),
            timings=PipelineTimings(total_ms=(t_fail - t_start_total) * 1000, steps=step_timings),
            debug_states=debug_states if request.debug else None,
        )

    t_end_total = time.perf_counter()

    return PipelineResponse(
        success=True,
        image=encoded,
        image_format=request.image_format,
        timings=PipelineTimings(total_ms=(t_end_total - t_start_total) * 1000, steps=step_timings),
        debug_states=debug_states if request.debug else None,
    )
