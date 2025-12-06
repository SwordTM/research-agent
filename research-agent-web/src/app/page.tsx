"use client";
import React, { useState } from "react";
import { SplitScreen } from "@/components/layout/split-screen";
import { ChatContainer } from "@/components/chat/chat-container";
import { RoadmapContainer } from "@/components/visualizer/roadmap-container";

export default function Home() {
  const [slideUrl, setSlideUrl] = useState<string>();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progressLogs, setProgressLogs] = useState<string[]>([]);

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

      if (!response.ok) {
        throw new Error("Analysis failed");
      }

      if (!response.body) {
        throw new Error("No response body");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;

        // Process complete messages
        const parts = buffer.split("\n\n");
        // Keep the last part in buffer if it's incomplete (doesn't end with \n\n)
        // actually split removes the separator, so we check if the original string ended with it
        // simpler approach: split by \n\n, process all except last if it might be incomplete? 
        // The server sends \n\n after each message.

        buffer = parts.pop() || ""; // Keep the last potentially incomplete part

        for (const part of parts) {
          if (part.startsWith("data: ")) {
            try {
              const jsonStr = part.substring(6); // Remove "data: "
              const data = JSON.parse(jsonStr);

              if (data.type === "log") {
                setProgressLogs((prev) => [...prev, data.message]);
              } else if (data.type === "error") {
                console.error("Stream error:", data.message);
                setProgressLogs((prev) => [...prev, `[ERROR] ${data.message}`]);
              } else if (data.type === "complete") {
                // Analysis complete
                setProgressLogs((prev) => [...prev, "[SUCCESS] Analysis complete!"]);
                // Use the first generated slide if available, or a default
                // The backend might return a list of slides or just success
                // For now, we'll try to construct the URL based on the first concept if available
                // or just use the first slide found in the logs if we parsed them?
                // The previous implementation hardcoded "/slides/example.html"
                // Let's see if the data contains the result

                if (data.data && Array.isArray(data.data.concepts) && data.data.concepts.length > 0) {
                  // If we have concepts, try to use the ID of the first one
                  const firstConceptId = data.data.concepts[0].id;
                  setSlideUrl(`/slides/${firstConceptId}.html`);
                } else {
                  // Fallback or try to find from logs? 
                  // Let's assume the user will pick from a list later, but for now show the first one
                  // We can also check if the backend returned a specific slide url
                  setSlideUrl("/slides/example.html");
                }
              }
            } catch (e) {
              console.error("Failed to parse SSE message:", e);
            }
          }
        }
      }
    } catch (error) {
      console.error("Analysis error:", error);
      setProgressLogs((prev) => [...prev, `[ERROR] Failed to analyze PDF: ${error}`]);
      alert("Failed to analyze PDF. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <main className="h-screen w-full overflow-hidden">
      <SplitScreen
        leftPanel={<ChatContainer onUploadComplete={handleUploadComplete} />}
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
