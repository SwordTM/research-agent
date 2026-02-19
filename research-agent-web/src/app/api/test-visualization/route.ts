import { NextResponse } from "next/server";
import { spawn } from "child_process";
import { join } from "path";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
    const encoder = new TextEncoder();

    const stream = new ReadableStream({
        start(controller) {
            const send = (data: object) => {
                controller.enqueue(
                    encoder.encode(`data: ${JSON.stringify(data)}\n\n`)
                );
            };

            send({ type: "log", message: "Starting SquareToCircle visualization build..." });

            const pythonPath = join(
                process.cwd(),
                "..",
                "python",
                "venv",
                "Scripts",
                "python.exe"
            );
            const scriptPath = join(process.cwd(), "..", "python", "build_manim_web.py");
            const codePath = join(process.cwd(), "..", "python", "temp_scenes", "square_to_circle.dart");
            const projectDir = join(process.cwd(), "..", "manim_project");

            console.log("[Test Vis] Python:", pythonPath);
            console.log("[Test Vis] Script:", scriptPath);
            console.log("[Test Vis] Code:", codePath);
            console.log("[Test Vis] Project:", projectDir);

            const python = spawn(pythonPath, [
                "-u",
                scriptPath,
                "--code-file", codePath,
                "--project-dir", projectDir,
            ]);

            let outputBuffer = "";

            python.stdout.on("data", (data) => {
                const text = data.toString();
                outputBuffer += text;

                const lines = text.split("\n");
                lines.forEach((line: string) => {
                    const trimmed = line.trim();
                    if (trimmed) {
                        send({ type: "log", message: trimmed });
                    }
                });
            });

            python.stderr.on("data", (data) => {
                const text = data.toString().trim();
                if (text) {
                    send({ type: "log", message: `[stderr] ${text}` });
                }
            });

            python.on("close", (code) => {
                console.log(`[Test Vis] Build finished with code: ${code}`);
                if (code === 0) {
                    send({ type: "log", message: "Build succeeded! Loading visualization..." });
                    send({
                        type: "complete",
                        data: {
                            concepts: [
                                {
                                    id: "square-to-circle",
                                    slide_url: "/manim_dist/viz.html",
                                },
                            ],
                        },
                    });
                } else {
                    send({
                        type: "error",
                        message: `Build failed with exit code ${code}`,
                    });
                }
                controller.close();
            });

            python.on("error", (err) => {
                send({ type: "error", message: `Failed to start build: ${err.message}` });
                controller.close();
            });
        },
    });

    return new NextResponse(stream, {
        headers: {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            Connection: "keep-alive",
        },
    });
}
