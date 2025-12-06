"use client";

import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable";
import { ReactNode } from "react";

interface SplitScreenProps {
    leftPanel: ReactNode;
    rightPanel: ReactNode;
}

export function SplitScreen({ leftPanel, rightPanel }: SplitScreenProps) {
    return (
        <ResizablePanelGroup direction="horizontal" className="min-h-screen rounded-lg border">
            <ResizablePanel defaultSize={50} minSize={20}>
                {leftPanel}
            </ResizablePanel>
            <ResizableHandle withHandle />
            <ResizablePanel defaultSize={50} minSize={20}>
                {rightPanel}
            </ResizablePanel>
        </ResizablePanelGroup>
    );
}
