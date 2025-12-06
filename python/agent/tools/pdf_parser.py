"""PDF Parser Tool - Extracts text and metadata from PDF files."""

import PyPDF2
import pdfplumber
from typing import Dict, List, Any
from pathlib import Path


class PDFParserTool:
    """MCP tool for parsing PDF files."""
    
    name = "pdf_parser"
    description = "Extracts text, metadata, and structure from PDF research papers"
    
    def __init__(self):
        self.supported_formats = [".pdf"]
    
    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Parse a PDF file and extract all relevant information.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text, metadata, and structure
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        result = {
            "text": "",
            "pages": [],
            "metadata": {},
            "num_pages": 0,
            "tables": [],
            "figures": []
        }
        
        print(f"      -> Opening PDF file...")
        # Extract text using pdfplumber (better for layout)
        with pdfplumber.open(pdf_path) as pdf:
            result["num_pages"] = len(pdf.pages)
            print(f"      -> Found {result['num_pages']} pages")
            
            for i, page in enumerate(pdf.pages, 1):
                if i == 1 or i % 5 == 0 or i == result["num_pages"]:
                    print(f"      -> Processing page {i}/{result['num_pages']}...")
                    
                page_text = page.extract_text() or ""
                result["pages"].append({
                    "page_number": i,
                    "text": page_text
                })
                result["text"] += f"\n--- Page {i} ---\n{page_text}"
                
                # Extract tables
                tables = page.extract_tables()
                if tables:
                    result["tables"].extend([
                        {"page": i, "table": table} for table in tables
                    ])
        
        print(f"      -> Extracting metadata...")
        # Extract metadata using PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            if pdf_reader.metadata:
                result["metadata"] = {
                    "title": pdf_reader.metadata.get('/Title', ''),
                    "author": pdf_reader.metadata.get('/Author', ''),
                    "subject": pdf_reader.metadata.get('/Subject', ''),
                    "creator": pdf_reader.metadata.get('/Creator', ''),
                }
        
        print(f"      -> PDF parsing complete")
        return result
    
    def extract_page_range(self, pdf_path: str, start_page: int, end_page: int) -> str:
        """Extract text from a specific page range."""
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for i in range(start_page - 1, min(end_page, len(pdf.pages))):
                page_text = pdf.pages[i].extract_text() or ""
                text += f"\n--- Page {i + 1} ---\n{page_text}"
            return text
    
    def get_page_count(self, pdf_path: str) -> int:
        """Get the total number of pages in the PDF."""
        with pdfplumber.open(pdf_path) as pdf:
            return len(pdf.pages)


# MCP tool interface
def create_tool():
    """Create and return the PDF parser tool instance."""
    return PDFParserTool()
