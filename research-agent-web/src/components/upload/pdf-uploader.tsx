"use client";

import React, { useState, useCallback } from "react";
import { Upload, File, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface PDFUploaderProps {
    onUploadComplete: (fileId: string, fileName: string) => void;
    compact?: boolean;
}

export function PDFUploader({ onUploadComplete, compact = false }: PDFUploaderProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const files = Array.from(e.dataTransfer.files);
        const pdfFile = files.find((file) => file.type === "application/pdf");

        if (pdfFile) {
            setSelectedFile(pdfFile);
        }
    }, []);

    const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file && file.type === "application/pdf") {
            setSelectedFile(file);
        }
    }, []);

    const handleUpload = async () => {
        if (!selectedFile) return;

        setIsUploading(true);
        setUploadProgress(0);

        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const response = await fetch("/api/upload", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Upload failed");
            }

            const data = await response.json();
            onUploadComplete(data.fileId, selectedFile.name);
            setSelectedFile(null);
        } catch (error) {
            console.error("Upload error:", error);
            alert("Failed to upload PDF. Please try again.");
        } finally {
            setIsUploading(false);
            setUploadProgress(0);
        }
    };

    const handleRemove = () => {
        setSelectedFile(null);
    };

    if (compact) {
        return (
            <div className="flex items-center gap-2 w-full">
                <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="pdf-upload-compact"
                />

                {!selectedFile ? (
                    <label htmlFor="pdf-upload-compact" className="w-full">
                        <Button variant="outline" size="sm" className="w-full gap-2 cursor-pointer" asChild>
                            <span>
                                <Upload className="h-4 w-4" />
                                Upload PDF
                            </span>
                        </Button>
                    </label>
                ) : (
                    <div className="flex items-center gap-2 w-full">
                        <div className="flex-1 min-w-0 flex items-center gap-2 px-2 py-1 border rounded text-sm">
                            <File className="h-3 w-3 flex-shrink-0" />
                            <span className="truncate">{selectedFile.name}</span>
                        </div>
                        <Button size="sm" onClick={handleUpload} disabled={isUploading}>
                            {isUploading ? "..." : "Analyze"}
                        </Button>
                        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleRemove}>
                            <X className="h-4 w-4" />
                        </Button>
                    </div>
                )}
            </div>
        );
    }

    return (
        <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Upload Research Paper</h3>

            {!selectedFile ? (
                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={cn(
                        "border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer",
                        isDragging
                            ? "border-primary bg-primary/10"
                            : "border-muted-foreground/25 hover:border-primary/50"
                    )}
                >
                    <input
                        type="file"
                        accept=".pdf"
                        onChange={handleFileSelect}
                        className="hidden"
                        id="pdf-upload"
                    />
                    <label htmlFor="pdf-upload" className="cursor-pointer">
                        <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                        <p className="text-sm font-medium mb-2">
                            Drop your PDF here or click to browse
                        </p>
                        <p className="text-xs text-muted-foreground">
                            Supports PDF files only
                        </p>
                    </label>
                </div>
            ) : (
                <div className="space-y-4">
                    <div className="flex items-center gap-3 p-4 border rounded-lg">
                        <File className="h-8 w-8 text-primary" />
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{selectedFile.name}</p>
                            <p className="text-xs text-muted-foreground">
                                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                        </div>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={handleRemove}
                            disabled={isUploading}
                        >
                            <X className="h-4 w-4" />
                        </Button>
                    </div>

                    {isUploading && (
                        <div className="space-y-2">
                            <div className="h-2 bg-muted rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-primary transition-all duration-300"
                                    style={{ width: `${uploadProgress}%` }}
                                />
                            </div>
                            <p className="text-xs text-center text-muted-foreground">
                                Uploading... {uploadProgress}%
                            </p>
                        </div>
                    )}

                    <Button
                        onClick={handleUpload}
                        disabled={isUploading}
                        className="w-full"
                    >
                        {isUploading ? "Uploading..." : "Analyze Paper"}
                    </Button>
                </div>
            )}
        </Card>
    );
}
