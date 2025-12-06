import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import { join } from "path";

export async function POST(request: NextRequest) {
    try {
        const { fileId, filePath } = await request.json();

        if (!fileId || !filePath) {
            return NextResponse.json(
                { error: "Missing fileId or filePath" },
                { status: 400 }
            );
        }

        // Use the virtual environment Python
        const pythonPath = join(
            process.cwd(),
            "..",
            "python",
            "venv",
            "Scripts",
            "python.exe"
        );
        const scriptPath = join(process.cwd(), "..", "python", "agent", "roadmap_agent.py");
        // filePath is relative to the Next.js project root (e.g. "uploads/file.pdf")
        // process.cwd() is the Next.js project root
        const fullFilePath = join(process.cwd(), filePath);

        const result = await executePythonScript(pythonPath, scriptPath, [fullFilePath]);

        return NextResponse.json({
            fileId,
            analysis: JSON.parse(result),
            status: "success",
        });
    } catch (error) {
        console.error("Analysis error:", error);
        return NextResponse.json(
            { error: "Failed to analyze PDF", details: error instanceof Error ? error.message : String(error) },
            { status: 500 }
        );
    }
}

function executePythonScript(pythonPath: string, scriptPath: string, args: string[]): Promise<string> {
    return new Promise((resolve, reject) => {
        console.log("\n" + "=".repeat(70));
        console.log("[NEXT.JS] Spawning Python script...");
        console.log(`[NEXT.JS] Python: ${pythonPath}`);
        console.log(`[NEXT.JS] Script: ${scriptPath}`);
        console.log(`[NEXT.JS] Args: ${args.join(", ")}`);
        console.log("=".repeat(70) + "\n");

        // Use -u flag for unbuffered output so we see logs in real-time
        const python = spawn(pythonPath, ["-u", scriptPath, ...args]);

        let output = "";
        let errorOutput = "";

        python.stdout.on("data", (data) => {
            const text = data.toString();
            output += text;
            // Log to Next.js console in real-time
            process.stdout.write(text);
        });

        python.stderr.on("data", (data) => {
            const text = data.toString();
            errorOutput += text;
            // Log warnings/errors to Next.js console in real-time
            process.stderr.write(text);
        });

        python.on("close", (code) => {
            console.log("\n" + "=".repeat(70));
            console.log(`[NEXT.JS] Python script finished with code: ${code}`);
            console.log("=".repeat(70) + "\n");

            if (code !== 0) {
                reject(new Error(`Python script failed with code ${code}: ${errorOutput}`));
            } else {
                // If successful, we resolve with stdout
                // We log stderr warnings but don't fail because of them
                if (errorOutput) {
                    console.warn("[NEXT.JS] Python script warnings:", errorOutput);
                }
                resolve(output);
            }
        });
    });
}
