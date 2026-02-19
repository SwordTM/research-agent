"use client";
import React, { useState } from "react";
import { SplitScreen } from "@/components/layout/split-screen";
import { ChatContainer } from "@/components/chat/chat-container";
import { RoadmapContainer } from "@/components/visualizer/roadmap-container";

export default function Home() {
  const [slideUrl, setSlideUrl] = useState<string>();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progressLogs, setProgressLogs] = useState<string[]>([]);

  const processStream = async (response: Response) => {
    if (!response.ok) throw new Error("Request failed");
    if (!response.body) throw new Error("No response body");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;

      const parts = buffer.split("\n\n");
      buffer = parts.pop() || "";

      for (const part of parts) {
        if (part.startsWith("data: ")) {
          try {
            const data = JSON.parse(part.substring(6));
            if (data.type === "log") {
              setProgressLogs((prev) => [...prev, data.message]);
            } else if (data.type === "error") {
              console.error("Stream error:", data.message);
              setProgressLogs((prev) => [...prev, `[ERROR] ${data.message}`]);
            } else if (data.type === "complete") {
              setProgressLogs((prev) => [...prev, "[SUCCESS] Analysis complete!"]);
              if (data.data && Array.isArray(data.data.concepts) && data.data.concepts.length > 0) {
                const firstConcept = data.data.concepts[0];
                if (firstConcept.slide_url) {
                  setSlideUrl(firstConcept.slide_url);
                } else {
                  setSlideUrl(`/slides/${firstConcept.id}.html`);
                }
              } else {
                setSlideUrl("/slides/example.html");
              }
            }
          } catch (e) {
            console.error("Failed to parse SSE message:", e);
          }
        }
      }
    }
  };

  const handleUploadComplete = async (fileId: string, fileName: string) => {
    setIsAnalyzing(true);
    setSlideUrl(undefined);
    setProgressLogs(["Initializing analysis process..."]);

    try {
      const response = await fetch("/api/analyze-stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fileId, filePath: `uploads/${fileId}` }),
      });
      await processStream(response);
    } catch (error) {
      console.error("Analysis error:", error);
      setProgressLogs((prev) => [...prev, `[ERROR] Failed to analyze PDF: ${error}`]);
      alert("Failed to analyze PDF. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleTestVisualization = async () => {
    setIsAnalyzing(true);
    setSlideUrl(undefined);
    setProgressLogs(["Starting test visualization..."]);

    try {
      const response = await fetch("/api/test-visualization");
      await processStream(response);
    } catch (error) {
      console.error("Test error:", error);
      setProgressLogs((prev) => [...prev, `[ERROR] Test failed: ${error}`]);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <main className="h-full w-full overflow-hidden">
      <SplitScreen
        leftPanel={<ChatContainer onUploadComplete={handleUploadComplete} onTestVisualization={handleTestVisualization} />}
        rightPanel={
          <RoadmapContainer
            slideUrl={slideUrl}
            isAnalyzing={isAnalyzing}
            progressLogs={progressLogs}
          />
        }
      />
    </main>
  );
}
