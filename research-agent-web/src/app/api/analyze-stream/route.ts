import { NextRequest } from "next/server";
import { spawn } from "child_process";
import { join } from "path";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
    const encoder = new TextEncoder();
    const { fileId, filePath } = await request.json();

    if (!fileId || !filePath) {
        return new Response("Missing fileId or filePath", { status: 400 });
    }

    const stream = new ReadableStream({
        start(controller) {
            const pythonPath = join(
                process.cwd(),
                "..",
                "python",
                "venv",
                "Scripts",
                "python.exe"
            );
            const scriptPath = join(process.cwd(), "..", "python", "agent", "roadmap_agent.py");
            const fullFilePath = join(process.cwd(), filePath);

            console.log("[SSE] Starting Python script...");
            console.log(`[SSE] Python: ${pythonPath}`);
            console.log(`[SSE] Script: ${scriptPath}`);
            console.log(`[SSE] File: ${fullFilePath}`);

            const python = spawn(pythonPath, ["-u", scriptPath, fullFilePath]);

            let outputBuffer = "";

            python.stdout.on("data", (data) => {
                const text = data.toString();
                outputBuffer += text;

                // Send each line as an SSE event
                const lines = text.split("\n");
                lines.forEach((line: string) => {
                    if (line.trim() && !line.includes("__JSON_RESULT__")) {
                        const message = `data: ${JSON.stringify({ type: "log", message: line })}\n\n`;
                        controller.enqueue(encoder.encode(message));
                    }
                });
            });

            python.stderr.on("data", (data) => {
                const text = data.toString();
                const message = `data: ${JSON.stringify({ type: "error", message: text })}\n\n`;
                controller.enqueue(encoder.encode(message));
            });

            python.on("close", (code) => {
                console.log(`[SSE] Python script finished with code: ${code}`);

                if (code === 0) {
                    // Try to parse the final output as JSON using the delimiter
                    try {
                        const parts = outputBuffer.split("__JSON_RESULT__");
                        if (parts.length > 1) {
                            const jsonContent = parts[1].split("__JSON_RESULT_END__")[0].trim();
                            const result = JSON.parse(jsonContent);
                            const message = `data: ${JSON.stringify({ type: "complete", data: result })}\n\n`;
                            controller.enqueue(encoder.encode(message));
                        } else {
                            throw new Error("JSON result delimiter not found");
                        }
                    } catch (e) {
                        console.error("Failed to parse result JSON:", e);
                        const message = `data: ${JSON.stringify({ type: "complete", data: { fileId } })}\n\n`;
                        controller.enqueue(encoder.encode(message));
                    }
                } else {
                    const message = `data: ${JSON.stringify({ type: "error", message: `Process exited with code ${code}` })}\n\n`;
                    controller.enqueue(encoder.encode(message));
                }

                controller.close();
            });

            python.on("error", (error) => {
                const message = `data: ${JSON.stringify({ type: "error", message: error.message })}\n\n`;
                controller.enqueue(encoder.encode(message));
                controller.close();
            });
        },
    });

    return new Response(stream, {
        headers: {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    });
}
