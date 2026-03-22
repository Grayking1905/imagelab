import { useState, useEffect } from "react";
import { useBlocklyWorkspace } from "../hooks/useBlocklyWorkspace";
import { usePipelineStore } from "../store/pipelineStore";
import Navbar from "./Navbar";
import Toolbar from "./Toolbar";
import Sidebar from "./Sidebar/Sidebar";
import PreviewPane from "./Preview/PreviewPane";
import InfoPane from "./InfoPane";
import { ErrorBoundary } from "./ErrorBoundary";

export default function Layout() {
  const { containerRef, workspace } = useBlocklyWorkspace();
  const { reset, isDebugActive, debugStates, debugCursor } = usePipelineStore();
  const [resetKey, setResetKey] = useState(0);

  // Apply visual highlighting to blocks during debug mode
  useEffect(() => {
    if (!workspace) return;

    // First, remove highlight from all blocks
    const allBlocks = workspace.getAllBlocks(false);
    allBlocks.forEach((block) => {
      const svgRoot = block.getSvgRoot();
      if (svgRoot) {
        svgRoot.classList.remove("debug-highlighted-block");
      }
    });

    // Then, if debug is active and we have a valid block, highlight it
    if (isDebugActive && debugStates && debugStates.length > 0) {
      const currentState = debugStates[debugCursor];
      if (currentState && currentState.block_id) {
        const activeBlock = workspace.getBlockById(currentState.block_id);
        if (activeBlock) {
          const svgRoot = activeBlock.getSvgRoot();
          if (svgRoot) {
            svgRoot.classList.add("debug-highlighted-block");

            // Optional: Scroll to the block
            // workspace.centerOnBlock(currentState.block_id);
          }
        }
      }
    }
  }, [workspace, isDebugActive, debugStates, debugCursor]);

  const handleEditorReset = () => {
    setResetKey((prev) => prev + 1);
    reset();
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Navbar />
      <Toolbar workspace={workspace} />
      <div className="flex flex-1 min-h-0">
        <Sidebar workspace={workspace} />
        <ErrorBoundary key={resetKey} onReset={handleEditorReset}>
          <div className="flex-1 flex min-w-0">
            <div className="flex-1 flex flex-col min-w-0">
              <div ref={containerRef} className="flex-1" />
              <InfoPane />
            </div>
            <PreviewPane />
          </div>
        </ErrorBoundary>
      </div>
    </div>
  );
}
