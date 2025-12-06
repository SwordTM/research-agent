"use client";

import React, { useState } from "react";
import { MessageList } from "./message-list";
import { InputArea } from "./input-area";
import { PDFUploader } from "../upload/pdf-uploader";

interface Message {
  role: "user" | "model";
  parts: { text: string }[];
}

interface ChatContainerProps {
  onUploadComplete?: (fileId: string, fileName: string) => void;
}

export function ChatContainer({ onUploadComplete }: ChatContainerProps) {
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
        {onUploadComplete && (
          <div className="flex-1 max-w-[200px]">
            <PDFUploader onUploadComplete={onUploadComplete} compact />
          </div>
        )}
      </div>
      <MessageList messages={messages} isLoading={isLoading} />
      <InputArea onSend={handleSend} disabled={isLoading} />
    </div>
  );
}
