from pydantic import BaseModel


class PipelineStep(BaseModel):
    type: str
    params: dict = {}
    id: str | None = None


class PipelineRequest(BaseModel):
    image: str
    image_format: str = "png"
    pipeline: list[PipelineStep]
    debug: bool = False


class StepTiming(BaseModel):
    step: int
    operator_type: str
    duration_ms: float


class PipelineTimings(BaseModel):
    total_ms: float
    steps: list[StepTiming]


class DebugStepState(BaseModel):
    """Snapshot of the image after a single operator executes."""

    step: int
    block_id: str | None = None
    operator_type: str
    image: str
    duration_ms: float


class PipelineResponse(BaseModel):
    success: bool
    image: str | None = None
    image_format: str | None = None
    error: str | None = None
    step: int | None = None
    timings: PipelineTimings | None = None
    debug_states: list[DebugStepState] | None = None
