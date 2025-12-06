"use client";

import React, { useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Loader2, Terminal } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface SlidesViewerProps {
    slideUrl?: string;
    isLoading?: boolean;
    progressLogs?: string[];
}

export function SlidesViewer({ slideUrl, isLoading, progressLogs = [] }: SlidesViewerProps) {
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new logs arrive
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [progressLogs]);

    if (isLoading) {
        return (
            <Card className="flex flex-col h-full p-6">
                <div className="flex items-center gap-3 mb-4 pb-4 border-b">
                    <Loader2 className="h-5 w-5 animate-spin text-primary" />
                    <h3 className="text-lg font-semibold">Generating Visual Slides</h3>
                </div>

                <ScrollArea className="flex-1">
                    <div
                        ref={scrollRef}
                        className="space-y-1 font-mono text-sm bg-slate-950 text-slate-100 p-4 rounded-lg overflow-auto max-h-[calc(100vh-200px)]"
                    >
                        {progressLogs.length === 0 ? (
                            <div className="flex items-center gap-2 text-slate-400">
                                <Terminal className="h-4 w-4" />
                                <span>Initializing...</span>
                            </div>
                        ) : (
                            progressLogs.map((log, index) => (
                                <div
                                    key={index}
                                    className={`${log.includes("[ERROR]") || log.includes("ERROR")
                                            ? "text-red-400"
                                            : log.includes("[WARNING]") || log.includes("WARNING")
                                                ? "text-yellow-400"
                                                : log.includes("[OK]") || log.includes("SUCCESS")
                                                    ? "text-green-400"
                                                    : log.includes("[ROADMAP AGENT]") || log.includes("[NEXT.JS]")
                                                        ? "text-cyan-400 font-bold"
                                                        : log.includes("[AI]")
                                                            ? "text-purple-400"
                                                            : log.includes("[RENDER]")
                                                                ? "text-blue-400"
                                                                : log.includes("[SLIDE")
                                                                    ? "text-yellow-300 font-semibold"
                                                                    : log.startsWith("      ")
                                                                        ? "text-slate-300 pl-6"
                                                                        : "text-slate-200"
                                        }`}
                                >
                                    {log}
                                </div>
                            ))
                        )}
                    </div>
                </ScrollArea>

                <div className="mt-4 pt-4 border-t">
                    <p className="text-xs text-muted-foreground text-center">
                        This may take several minutes depending on the paper complexity...
                    </p>
                </div>
            </Card>
        );
    }

    if (!slideUrl) {
        return (
            <Card className="flex flex-col items-center justify-center h-full p-8 text-center">
                <div className="max-w-md space-y-4">
                    <h3 className="text-lg font-semibold">No Slides Yet</h3>
                    <p className="text-sm text-muted-foreground">
                        Upload a research paper to generate visual concept slides using Manim.
                    </p>
                </div>
            </Card>
        );
    }

    return (
        <div className="h-full w-full">
            <iframe
                src={slideUrl}
                className="w-full h-full border-0 rounded-lg"
                title="Concept Slides"
                sandbox="allow-scripts allow-same-origin"
            />
        </div>
    );
}
