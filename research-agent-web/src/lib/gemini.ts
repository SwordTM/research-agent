import { GoogleGenerativeAI } from "@google/generative-ai";

const apiKey = process.env.GEMINI_API_KEY;

if (!apiKey) {
    console.error("GEMINI_API_KEY is not defined in environment variables.");
    throw new Error("GEMINI_API_KEY is required");
} else {
    console.log("GEMINI_API_KEY is defined.");
}

const genAI = new GoogleGenerativeAI(apiKey);

export const model = genAI.getGenerativeModel({ model: "gemini-2.5-pro" });
