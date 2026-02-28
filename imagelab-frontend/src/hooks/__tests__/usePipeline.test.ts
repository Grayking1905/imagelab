/**
 * Tests for extractPipeline() in usePipeline.ts
 *
 * Strategy: We mock Blockly's workspace / block / input / field objects using
 * plain JavaScript objects that satisfy the exact properties accessed by
 * extractPipeline(). No real Blockly DOM or registration is needed.
 *
 * The Blockly.WorkspaceSvg type is cast via `as unknown as Blockly.WorkspaceSvg`
 * so TypeScript is happy while we avoid importing the full Blockly runtime.
 */

import { describe, it, expect } from "vitest";
import type * as Blockly from "blockly";

import { extractPipeline } from "../usePipeline";
import {
  makeField,
  makeInput,
  makeBlock,
  makeWorkspace,
  type MockWorkspace,
} from "./blockly.mock";

/** Cast our lightweight mock to the type extractPipeline() expects. */
function asWorkspace(mock: MockWorkspace): Blockly.WorkspaceSvg {
  return mock as unknown as Blockly.WorkspaceSvg;
}

// ─── Empty / missing readimage ────────────────────────────────────────────────

describe("extractPipeline — empty / missing readimage", () => {
  it("returns [] for an empty workspace", () => {
    const workspace = makeWorkspace([]);
    expect(extractPipeline(asWorkspace(workspace))).toEqual([]);
  });

  it("returns [] when no basic_readimage block exists", () => {
    // Workspace has blocks, but none are the required entry-point type.
    const unrelated = makeBlock("geometric_rotateimage", [
      makeInput([makeField("angle", "90")]),
    ]);
    const workspace = makeWorkspace([unrelated]);
    expect(extractPipeline(asWorkspace(workspace))).toEqual([]);
  });
});

// ─── Single block ─────────────────────────────────────────────────────────────

describe("extractPipeline — single block", () => {
  it("returns a single step with empty params for a readimage block with no named fields", () => {
    // basic_readimage has a field_label_serializable ("filename_label") but
    // the label's name value could be empty; here we simulate no name fields.
    const readBlock = makeBlock("basic_readimage", [makeInput([])]);
    const workspace = makeWorkspace([readBlock]);
    expect(extractPipeline(asWorkspace(workspace))).toEqual([
      { type: "basic_readimage", params: {} },
    ]);
  });

  it("extracts numeric field params correctly", () => {
    // Mirrors geometric_rotateimage: field_angle + field_number
    const readBlock = makeBlock("basic_readimage", [
      makeInput([
        makeField("angle", "45"),
        makeField("scale", "1.5"),
      ]),
    ]);
    const workspace = makeWorkspace([readBlock]);
    const result = extractPipeline(asWorkspace(workspace));
    expect(result).toHaveLength(1);
    expect(result[0].params).toEqual({ angle: "45", scale: "1.5" });
  });

  it("extracts dropdown field params correctly", () => {
    // Mirrors geometric_reflectimage: field_dropdown named "type"
    const readBlock = makeBlock("basic_readimage", [
      makeInput([makeField("type", "X")]),
    ]);
    const workspace = makeWorkspace([readBlock]);
    const result = extractPipeline(asWorkspace(workspace));
    expect(result[0].params).toEqual({ type: "X" });
  });

  it("extracts color field params correctly", () => {
    // Mirrors drawingoperations_drawline: field_colour named "rgbcolors_input"
    const readBlock = makeBlock("basic_readimage", [
      makeInput([makeField("rgbcolors_input", "#2828cc")]),
    ]);
    const workspace = makeWorkspace([readBlock]);
    const result = extractPipeline(asWorkspace(workspace));
    expect(result[0].params).toEqual({ rgbcolors_input: "#2828cc" });
  });

  it("skips fields whose name is an empty string", () => {
    // Blockly labels / anonymous fields have name === "" and should be ignored.
    const readBlock = makeBlock("basic_readimage", [
      makeInput([
        makeField("", "ignored"),      // unnamed — should be skipped
        makeField("strength", "1.5"),  // named — should be captured
      ]),
    ]);
    const workspace = makeWorkspace([readBlock]);
    const result = extractPipeline(asWorkspace(workspace));
    expect(result[0].params).toEqual({ strength: "1.5" });
    expect(Object.keys(result[0].params)).not.toContain("");
  });
});

// ─── Block chain traversal ────────────────────────────────────────────────────

describe("extractPipeline — block chain traversal", () => {
  it("returns steps in chain order (readimage is first, writeimage is last)", () => {
    const writeBlock = makeBlock("basic_writeimage", [], null);
    const rotateBlock = makeBlock(
      "geometric_rotateimage",
      [makeInput([makeField("angle", "90"), makeField("scale", "1")])],
      writeBlock,
    );
    const readBlock = makeBlock("basic_readimage", [], rotateBlock);

    const workspace = makeWorkspace([readBlock]);
    const result = extractPipeline(asWorkspace(workspace));

    expect(result).toHaveLength(3);
    expect(result[0].type).toBe("basic_readimage");
    expect(result[1].type).toBe("geometric_rotateimage");
    expect(result[2].type).toBe("basic_writeimage");
  });

  it("extracts params for each block in the chain independently", () => {
    const blurBlock = makeBlock("filtering_bilateral", [
      makeInput([
        makeField("filterSize", "5"),
        makeField("sigmaColor", "75"),
        makeField("sigmaSpace", "75"),
      ]),
    ]);
    const rotateBlock = makeBlock(
      "geometric_rotateimage",
      [makeInput([makeField("angle", "45"), makeField("scale", "2")])],
      blurBlock,
    );
    const readBlock = makeBlock("basic_readimage", [], rotateBlock);

    const workspace = makeWorkspace([readBlock]);
    const result = extractPipeline(asWorkspace(workspace));

    expect(result).toHaveLength(3);
    expect(result[1].params).toEqual({ angle: "45", scale: "2" });
    expect(result[2].params).toEqual({ filterSize: "5", sigmaColor: "75", sigmaSpace: "75" });
  });

  it("stops traversal at the end of the chain (null next block)", () => {
    const readBlock = makeBlock("basic_readimage", [], null);
    const workspace = makeWorkspace([readBlock]);
    const result = extractPipeline(asWorkspace(workspace));
    expect(result).toHaveLength(1);
  });
});

// ─── VALUE-type connected child block ─────────────────────────────────────────

describe("extractPipeline — VALUE input child block merging", () => {
  /**
   * The INPUT_TYPE_VALUE constant inside usePipeline.ts is 1.
   * When an input has type === 1 and a connected block, that child block's
   * fields are merged into the parent step's params.
   */
  const INPUT_TYPE_VALUE = 1;
  const INPUT_TYPE_STATEMENT = 0;

  it("merges child block fields into parent step params for VALUE inputs", () => {
    // Simulates a border-value block plugged into an applyborders block.
    const childBlock = makeBlock("some_value_block", [
      makeInput([makeField("borderType", "REFLECT")]),
    ]);
    const parentInput = makeInput(
      [makeField("iterations", "3")],
      childBlock,
      INPUT_TYPE_VALUE,
    );
    const readBlock = makeBlock("basic_readimage", [parentInput]);

    const workspace = makeWorkspace([readBlock]);
    const result = extractPipeline(asWorkspace(workspace));

    // Child's field is merged into the parent step's params.
    expect(result[0].params).toEqual({ iterations: "3", borderType: "REFLECT" });
  });

  it("does NOT merge child block fields for non-VALUE (statement) inputs", () => {
    const childBlock = makeBlock("some_statement_block", [
      makeInput([makeField("shouldNotAppear", "oops")]),
    ]);
    const parentInput = makeInput(
      [makeField("myParam", "good")],
      childBlock,
      INPUT_TYPE_STATEMENT, // type = 0, not a VALUE input
    );
    const readBlock = makeBlock("basic_readimage", [parentInput]);

    const workspace = makeWorkspace([readBlock]);
    const result = extractPipeline(asWorkspace(workspace));

    expect(result[0].params).toEqual({ myParam: "good" });
    expect(result[0].params).not.toHaveProperty("shouldNotAppear");
  });

  it("handles a VALUE input with no connected block gracefully", () => {
    // connection exists but targetBlock() returns null
    const parentInput = makeInput(
      [makeField("param", "value")],
      null,       // targetBlock() will return null
      INPUT_TYPE_VALUE,
    );
    const readBlock = makeBlock("basic_readimage", [parentInput]);

    const workspace = makeWorkspace([readBlock]);
    const result = extractPipeline(asWorkspace(workspace));

    expect(result[0].params).toEqual({ param: "value" });
  });
});
