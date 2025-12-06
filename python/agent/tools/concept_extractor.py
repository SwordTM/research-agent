            paper_text: Full text of the research paper
            max_concepts: Maximum number of concepts to extract
            
        Returns:
            List of Concept objects
        """
        print(f"      -> Calling Gemini AI to analyze paper...")
        print(f"      -> Analyzing {len(paper_text[:15000])} characters...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at analyzing research papers and extracting key concepts.
            Identify the most important concepts, techniques, architectures, algorithms, and innovations.
            For each concept, provide:
            - A unique ID (lowercase, underscore-separated)
            - A clear title
            - A detailed description
            - The concept type (architecture, technique, algorithm, methodology, result, innovation)
            - An importance score (0.0 to 1.0)
            
            Focus on concepts that are central to understanding the paper's contribution.
            {format_instructions}"""),
            ("user", "Extract up to {max_concepts} key concepts from this research paper:\n\n{paper_text}")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "paper_text": paper_text[:15000],  # Limit to avoid token limits
            "max_concepts": max_concepts,
            "format_instructions": self.parser.get_format_instructions()
        })
        
        print(f"      -> AI response received, parsing concepts...")
        
        # Parse the response
        try:
            result = self.parser.parse(response.content)
            return result.concepts
        except Exception as e:
            print(f"      -> ERROR parsing concepts: {e}")
            # Return empty list if parsing fails
            return []
    
    def extract_from_section(self, section_text: str, section_name: str) -> List[Concept]:
        """Extract concepts from a specific section of the paper."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract key concepts from the {section_name} section of a research paper.
            {format_instructions}"""),
            ("user", "{section_text}")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "section_name": section_name,
            "section_text": section_text,
            "format_instructions": self.parser.get_format_instructions()
        })
        
        try:
            result = self.parser.parse(response.content)
            return result.concepts
        except Exception:
            return []


def create_tool(api_key: str = None):
    """Create and return the concept extractor tool instance."""
    return ConceptExtractorTool(api_key=api_key)
