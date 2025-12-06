"""MCP Server - Exposes tools via Model Context Protocol."""

import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our tools
from tools.pdf_parser import PDFParserTool
from tools.concept_extractor import ConceptExtractorTool

# Initialize tools
pdf_parser = PDFParserTool()
concept_extractor = ConceptExtractorTool()

# Create MCP server
app = Server("research-agent-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="parse_pdf",
            description="Parse a PDF file and extract text, metadata, and structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "Path to the PDF file to parse"
                    }
                },
                "required": ["pdf_path"]
            }
        ),
        Tool(
            name="extract_concepts",
            description="Extract key concepts from research paper text using AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_text": {
                        "type": "string",
                        "description": "Full text of the research paper"
                    },
                    "max_concepts": {
                        "type": "integer",
                        "description": "Maximum number of concepts to extract",
                        "default": 10
                    }
                },
                "required": ["paper_text"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool with given arguments."""
    
    if name == "parse_pdf":
        pdf_path = arguments["pdf_path"]
        result = pdf_parser.parse_pdf(pdf_path)
        return [TextContent(type="text", text=str(result))]
    
    elif name == "extract_concepts":
        paper_text = arguments["paper_text"]
        max_concepts = arguments.get("max_concepts", 10)
        concepts = concept_extractor.extract_concepts(paper_text, max_concepts)
        
        # Convert concepts to dict for JSON serialization
        concepts_dict = [c.model_dump() for c in concepts]
        return [TextContent(type="text", text=str(concepts_dict))]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
