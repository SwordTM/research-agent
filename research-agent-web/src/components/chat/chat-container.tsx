"use client";

import React, { useState } from "react";
import { MessageList } from "./message-list";
import { InputArea } from "./input-area";
import { PDFUploader } from "../upload/pdf-uploader";

interface Message {
  role: "user" | "model";
  parts: { text: string }[];
}

import { Button } from "@/components/ui/button";

interface ChatContainerProps {
  onUploadComplete?: (fileId: string, fileName: string) => void;
  onTestVisualization?: () => void;
}

export function ChatContainer({ onUploadComplete, onTestVisualization }: ChatContainerProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (text: string) => {
    const userMessage: Message = { role: "user", parts: [{ text }] };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          history: messages.map((m) => ({
            role: m.role,
            parts: m.parts,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();
      const modelMessage: Message = {
        role: "model",
        parts: [{ text: data.text }],
      };

      setMessages((prev) => [...prev, modelMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      // Optionally handle error state here
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-background border-r">
      <div className="p-4 border-b flex items-center justify-between gap-4">
        <h2 className="font-semibold whitespace-nowrap">Research Assistant</h2>
        <div className="flex items-center gap-2 flex-1 justify-end">
          {onTestVisualization && (
            <Button variant="outline" size="sm" onClick={onTestVisualization}>
              Test Vis
            </Button>
          )}
          {onUploadComplete && (
            <div className="flex-1 max-w-[200px]">
              <PDFUploader onUploadComplete={onUploadComplete} compact />
            </div>
          )}
        </div>
      </div>
      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center p-8 gap-4">
          <div className="max-w-md w-full space-y-4">
            <div className="text-center space-y-2">
              <h3 className="text-2xl font-bold">Welcome to Research Agent</h3>
              <p className="text-muted-foreground">
                Upload a research paper to get started with analysis and visualization.
              </p>
            </div>
            {onUploadComplete && (
              <PDFUploader onUploadComplete={onUploadComplete} />
            )}
          </div>
        </div>
      ) : (
        <>
          <MessageList messages={messages} isLoading={isLoading} />
          <InputArea onSend={handleSend} disabled={isLoading} />
        </>
      )}
    </div>
  );
}
