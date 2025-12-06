import React, { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

interface Message {
    role: "user" | "model";
    parts: { text: string }[];
}

interface MessageListProps {
    messages: Message[];
    isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages, isLoading]);

    return (
        <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-4">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={cn(
                            "flex w-full",
                            msg.role === "user" ? "justify-end" : "justify-start"
                        )}
                    >
                        <div
                            className={cn(
                                "rounded-lg px-4 py-2 max-w-[80%]",
                                msg.role === "user"
                                    ? "bg-primary text-primary-foreground"
                                    : "bg-muted text-foreground"
                            )}
                        >
                            <p className="whitespace-pre-wrap text-sm">{msg.parts[0].text}</p>
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-muted rounded-lg px-4 py-2">
                            <p className="text-sm text-muted-foreground animate-pulse">
                                Thinking...
                            </p>
                        </div>
                    </div>
                )}
                <div ref={scrollRef} />
            </div>
        </div>
    );
}
