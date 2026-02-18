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

    return (
        <Card className="flex flex-col h-full p-4 relative">
            {slideUrl ? (
                <div className="flex-1 w-full min-h-[60%] mb-4 rounded-lg overflow-hidden border bg-black">
                    <iframe
                        src={slideUrl}
                        className="w-full h-full border-0"
                        title="Concept Slides"
                        sandbox="allow-scripts allow-same-origin"
                    />
                </div>
            ) : (
                <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-slate-50 dark:bg-slate-900 rounded-lg border border-dashed mb-4">
                    <div className="max-w-md space-y-4">
                        <h3 className="text-lg font-semibold">
                            {isLoading ? "Generating Visualization..." : "No Slides Yet"}
                        </h3>
                        {isLoading && <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />}
                        {!isLoading && (
                            <p className="text-sm text-muted-foreground">
                                Upload a research paper to generate visual concept slides using Manim.
                            </p>
                        )}
                    </div>
                </div>
            )}

            {/* Always show logs for debugging */}
            <div className="h-[30%] border-t pt-4">
                <div className="flex items-center gap-2 mb-2">
                    <Terminal className="h-4 w-4 text-muted-foreground" />
                    <h4 className="text-sm font-semibold text-muted-foreground">Build Logs & Debug Output</h4>
                </div>
                <ScrollArea className="h-full w-full rounded-md border bg-slate-950 p-4">
                    <div ref={scrollRef} className="space-y-1 font-mono text-xs text-slate-100">
                        {progressLogs.length === 0 ? (
                            <div className="text-slate-500 italic">Waiting for logs...</div>
                        ) : (
                            progressLogs.map((log, index) => (
                                <div
                                    key={index}
                                    className={`${log.includes("[ERROR]") || log.includes("ERROR")
                                        ? "text-red-400 font-bold bg-red-950/30"
                                        : log.includes("[WARNING]") || log.includes("WARNING")
                                            ? "text-yellow-400"
                                            : log.includes("[OK]") || log.includes("SUCCESS")
                                                ? "text-green-400 font-semibold"
                                                : log.includes("[webdev]")
                                                    ? "text-blue-300"
                                                    : "text-slate-300"
                                        } break-words whitespace-pre-wrap`}
                                >
                                    {log}
                                </div>
                            ))
                        )}
                    </div>
                </ScrollArea>
            </div>
        </Card>
    );
}
