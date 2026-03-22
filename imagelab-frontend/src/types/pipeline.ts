export interface PipelineStep {
  type: string;
  params: Record<string, unknown>;
  id?: string;
}

export interface PipelineRequest {
  image: string;
  image_format: string;
  pipeline: PipelineStep[];
  debug?: boolean;
}

export interface StepTiming {
  step: number;
  operator_type: string;
  duration_ms: number;
}

export interface PipelineTimings {
  total_ms: number;
  steps: StepTiming[];
}

export interface DebugStepState {
  step: number;
  block_id: string | null;
  operator_type: string;
  image: string;
  duration_ms: number;
}

export interface PipelineResponse {
  success: boolean;
  image?: string;
  image_format?: string;
  error?: string;
  step?: number;
  timings?: PipelineTimings;
  debug_states?: DebugStepState[];
}
