import React, { useState, KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send } from "lucide-react";

interface InputAreaProps {
    onSend: (message: string) => void;
    disabled: boolean;
}

export function InputArea({ onSend, disabled }: InputAreaProps) {
    const [input, setInput] = useState("");

    const handleSend = () => {
        if (input.trim() && !disabled) {
            onSend(input.trim());
            setInput("");
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="p-4 border-t bg-background">
            <div className="flex gap-2">
                <Textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask a question about the paper..."
                    className="min-h-[50px] max-h-[200px]"
                    disabled={disabled}
                />
                <Button
                    onClick={handleSend}
                    disabled={disabled || !input.trim()}
                    size="icon"
                    className="h-[50px] w-[50px]"
                >
                    <Send className="h-5 w-5" />
                </Button>
            </div>
        </div>
    );
}
