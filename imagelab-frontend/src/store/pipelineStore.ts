import { create } from "zustand";
import * as Blockly from "blockly";
import { categories } from "../blocks/categories";
import type { PipelineTimings, DebugStepState } from "../types/pipeline";

interface PipelineState {
  originalImage: string | null;
  imageFormat: string;
  processedImage: string | null;
  isExecuting: boolean;
  error: string | null;
  errorStep: number | null;
  selectedBlockType: string | null;
  selectedBlockTooltip: string | null;
  timings: PipelineTimings | null;

  // Statistics
  blockCount: number;
  uniqueBlockTypes: number;
  categoryCounts: Record<string, number>;
  complexity: "Low" | "Medium" | "High";

  // Debug mode
  debugMode: boolean;
  debugStates: DebugStepState[];
  debugCursor: number;
  isDebugActive: boolean;

  setOriginalImage: (image: string, format: string) => void;
  setProcessedImage: (image: string | null) => void;
  setExecuting: (executing: boolean) => void;
  setError: (error: string | null, step?: number | null) => void;
  setSelectedBlock: (type: string | null, tooltip: string | null) => void;
  setTiming: (timings: PipelineTimings | null) => void;
  updateBlockStats: (workspace: Blockly.WorkspaceSvg) => void;
  reset: () => void;
  clearImage: () => void;
  _imageResetFn: (() => void) | null;
  registerImageReset: (fn: () => void) => void;

  // Debug actions
  setDebugMode: (on: boolean) => void;
  setDebugStates: (states: DebugStepState[]) => void;
  setDebugCursor: (cursor: number) => void;
  stepForward: () => void;
  stepBackward: () => void;
  exitDebug: () => void;
}

function calculateComplexity(blocks: number, unique: number): "Low" | "Medium" | "High" {
  if (blocks === 0) return "Low";
  if (blocks > 10 || unique > 5) return "High";
  if (blocks > 3 || unique > 2) return "Medium";
  return "Low";
}

export const usePipelineStore = create<PipelineState>((set, get) => ({
  originalImage: null,
  imageFormat: "png",
  processedImage: null,
  isExecuting: false,
  error: null,
  errorStep: null,
  selectedBlockType: null,
  selectedBlockTooltip: null,
  timings: null,
  blockCount: 0,
  uniqueBlockTypes: 0,
  categoryCounts: {},
  complexity: "Low",

  // Debug mode defaults
  debugMode: false,
  debugStates: [],
  debugCursor: 0,
  isDebugActive: false,

  setOriginalImage: (image, format) =>
    set({
      originalImage: image,
      imageFormat: format,
      processedImage: null,
      error: null,
      timings: null,
    }),
  setProcessedImage: (image) => set({ processedImage: image, error: null, errorStep: null }),
  setExecuting: (executing) => set({ isExecuting: executing }),
  setError: (error, step = null) => set({ error, errorStep: step }),
  setSelectedBlock: (type, tooltip) =>
    set({ selectedBlockType: type, selectedBlockTooltip: tooltip }),
  setTiming: (timings) => set({ timings }),
  _imageResetFn: null as (() => void) | null,
  registerImageReset: (fn) => set({ _imageResetFn: fn }),
  clearImage: () => {
    const state = usePipelineStore.getState();
    if (state._imageResetFn) state._imageResetFn();
    set({
      originalImage: null,
      processedImage: null,
      error: null,
      errorStep: null,
      timings: null,
      debugStates: [],
      debugCursor: 0,
      isDebugActive: false,
    });
  },
  updateBlockStats: (workspace) => {
    const blocks = workspace.getAllBlocks(false);

    const typeToCategory: Record<string, string> = {};
    categories.forEach((cat) => {
      cat.blocks.forEach((b) => {
        typeToCategory[b.type] = cat.name;
      });
    });

    const uniqueTypes = new Set<string>();
    const counts: Record<string, number> = {};

    blocks.forEach((block) => {
      uniqueTypes.add(block.type);
      const cat = typeToCategory[block.type] || "Unknown";
      counts[cat] = (counts[cat] || 0) + 1;
    });

    set({
      blockCount: blocks.length,
      uniqueBlockTypes: uniqueTypes.size,
      categoryCounts: counts,
      complexity: calculateComplexity(blocks.length, uniqueTypes.size),
    });
  },
  reset: () =>
    set({
      originalImage: null,
      imageFormat: "png",
      processedImage: null,
      isExecuting: false,
      error: null,
      errorStep: null,
      selectedBlockType: null,
      selectedBlockTooltip: null,
      blockCount: 0,
      uniqueBlockTypes: 0,
      categoryCounts: {},
      complexity: "Low",
      timings: null,
      debugMode: false,
      debugStates: [],
      debugCursor: 0,
      isDebugActive: false,
    }),

  // Debug actions
  setDebugMode: (on) => set({ debugMode: on }),

  setDebugStates: (states) =>
    set({
      debugStates: states,
      debugCursor: states.length - 1,
      isDebugActive: true,
    }),

  setDebugCursor: (cursor) => {
    const { debugStates } = get();
    set({ debugCursor: Math.max(0, Math.min(cursor, debugStates.length - 1)) });
  },

  stepForward: () => {
    const { debugCursor, debugStates } = get();
    if (debugCursor < debugStates.length - 1) {
      set({ debugCursor: debugCursor + 1 });
    }
  },

  stepBackward: () => {
    const { debugCursor } = get();
    if (debugCursor > 0) {
      set({ debugCursor: debugCursor - 1 });
    }
  },

  exitDebug: () =>
    set({
      isDebugActive: false,
      debugStates: [],
      debugCursor: 0,
    }),
}));
