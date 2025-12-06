"use client";

import React from "react";
import { SlidesViewer } from "./slides-viewer";

interface RoadmapContainerProps {
    slideUrl?: string;
    isAnalyzing?: boolean;
    progressLogs?: string[];
}

export function RoadmapContainer({ slideUrl, isAnalyzing = false, progressLogs = [] }: RoadmapContainerProps) {
    return (
        <div className="flex flex-col h-full p-4 bg-background gap-4">
            <div className="flex-1 min-h-0">
                <SlidesViewer slideUrl={slideUrl} isLoading={isAnalyzing} progressLogs={progressLogs} />
            </div>
        </div>
    );
}
