/**
 * Reusable Blockly mock factory functions.
 *
 * These helpers build minimal, realistic Blockly object shapes that satisfy
 * the API surface used by `extractPipeline()` in `usePipeline.ts`. They are
 * designed to be composable so future tests can reuse them without repetition.
 *
 * Blockly API surface exercised by extractPipeline():
 *   workspace.getTopBlocks(ordered: boolean) → Block[]
 *   block.type                            → string
 *   block.inputList                       → Input[]
 *   block.getNextBlock()                  → Block | null
 *   input.fieldRow                        → Field[]
 *   input.connection?.targetBlock()       → Block | null
 *   input.type                            → number  (1 = VALUE input)
 *   field.name                            → string
 *   field.getValue()                      → string
 */


// ─── Field ────────────────────────────────────────────────────────────────────

export interface MockField {
  name: string;
  getValue: () => string;
}

/**
 * Create a mock Blockly Field.
 *
 * @param name  - The `field.name` identifier (empty string means "skip this field").
 * @param value - The value returned by `field.getValue()`.
 */
export function makeField(name: string, value: string): MockField {
  return { name, getValue: () => value };
}

// ─── Input ────────────────────────────────────────────────────────────────────

export interface MockConnection {
  targetBlock: () => MockBlock | null;
}

export interface MockInput {
  fieldRow: MockField[];
  connection: MockConnection | undefined;
  type: number;
}

/**
 * Create a mock Blockly Input.
 *
 * @param fields      - Array of fields on this input's fieldRow.
 * @param targetBlock - Optional block connected to this input via a VALUE connection.
 * @param inputType   - Blockly input type number. 1 = VALUE (default for connected blocks), 0 = STATEMENT.
 */
export function makeInput(
  fields: MockField[],
  targetBlock?: MockBlock | null,
  inputType = 0,
): MockInput {
  return {
    fieldRow: fields,
    connection: targetBlock !== undefined
      ? { targetBlock: () => targetBlock }
      : undefined,
    type: inputType,
  };
}

// ─── Block ────────────────────────────────────────────────────────────────────

export interface MockBlock {
  type: string;
  inputList: MockInput[];
  getNextBlock: () => MockBlock | null;
}

/**
 * Create a mock Blockly Block.
 *
 * @param type      - The block's type string (e.g. `"basic_readimage"`).
 * @param inputs    - Array of inputs on `block.inputList`.
 * @param nextBlock - The next block in the statement chain, or null.
 */
export function makeBlock(
  type: string,
  inputs: MockInput[] = [],
  nextBlock: MockBlock | null = null,
): MockBlock {
  return {
    type,
    inputList: inputs,
    getNextBlock: () => nextBlock,
  };
}

// ─── Workspace ────────────────────────────────────────────────────────────────

export interface MockWorkspace {
  getTopBlocks: (ordered: boolean) => MockBlock[];
}

/**
 * Create a mock Blockly WorkspaceSvg.
 *
 * @param topBlocks - The blocks returned by `workspace.getTopBlocks(true)`.
 */
export function makeWorkspace(topBlocks: MockBlock[]): MockWorkspace {
  return {
    getTopBlocks: () => topBlocks,
  };
}
