from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_text_splitters import RecursiveCharacterTextSplitter

from models.roadmap import Concept

class ConceptList(BaseModel):
    concepts: List[Concept]

class ConceptExtractorTool:
    def __init__(self, llm: BaseChatModel = None, api_key: str = None):
        self.parser = PydanticOutputParser(pydantic_object=ConceptList)
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            # Max chunk size (e.g., 8000 tokens for a model with 16k context)
            chunk_size=12000, 
            chunk_overlap=500, # Overlap to maintain context across chunks
            separators=["\n\n", "\n", " ", ""]
        )

        if llm:
            self.llm = llm
        else:
            if not api_key:
                import os
                api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY")
                
            self.llm = ChatOpenAI(
                model="google/gemini-2.0-flash-001",
                openai_api_key=api_key,
                openai_api_base="https://openrouter.ai/api/v1",
                default_headers={"HTTP-Referer": "https://research-agent.com", "X-Title": "Research Agent"}
            )

        # This separate LLM will be used for combining/filtering concepts
        self.combiner_llm = ChatOpenAI(
            model="google/gemini-2.0-flash-001",
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={"HTTP-Referer": "https://research-agent.com", "X-Title": "Research Agent"}
        )
    
    def _get_extraction_prompt(self, is_final_pass: bool = False):
        """Generates the appropriate prompt for chunk extraction or final filtering."""
        base_instructions = """You are an expert at analyzing research papers and extracting key concepts.
        As a subprocess of building a research agent, your task is to identify and extract the most important concepts from a research paper.
        Identify the most important concepts, techniques, architectures, algorithms, and innovations.
        For each concept, provide:
        - A unique ID (lowercase, underscore-separated)
        - A clear title
        - A detailed description (Make sure the description is comprehensive and informative)
        - The concept type (architecture, technique, algorithm, methodology, result, innovation)
        - An importance score (0.0 to 1.0)
        
        Focus on concepts that are central to understanding the paper's contribution.
        {format_instructions}"""
        
        if is_final_pass:
            system_message = (
                f"{base_instructions}\n\n"
                "You are performing a final filtering step. Review the provided list of concepts "
                "from different paper sections. MERGE identical or highly redundant concepts, "
                "and select the top {max_concepts} most important concepts overall. "
                "The 'paper_text' will contain the aggregated concepts to review."
            )
        else:
            system_message = (
                f"{base_instructions}\n\n"
                "You are analyzing a CHUNK of a research paper. Extract concepts unique to this section. "
                "Do not repeat general concepts from the introduction unless this section introduces the core details."
            )
            
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("user", "Extract up to {max_concepts} key concepts from this chunk:\n\n{paper_text}")
        ])


    def extract_concepts(self, paper_text: str, max_concepts: int = 5) -> List[Concept]:
            """
            Extract concepts from text using chunking for long papers.
            """
            all_concepts: List[Concept] = []
            
            # 1. Split the paper into chunks
            chunks = self.text_splitter.create_documents([paper_text])
            num_chunks = len(chunks)
            print(f"      -> Paper split into {num_chunks} chunks.")
            
            # 2. Process each chunk
            for i, chunk in enumerate(chunks):
                chunk_text = chunk.page_content
                print(f"      -> Analyzing chunk {i+1}/{num_chunks} ({len(chunk_text)} chars)...")
                
                prompt = self._get_extraction_prompt(is_final_pass=False)
                chain = prompt | self.llm
                
                response = chain.invoke({
                    "paper_text": chunk_text,
                    "max_concepts": max_concepts,
                    "format_instructions": self.parser.get_format_instructions()
                })
                
                # Parse the response
                try:
                    result = self.parser.parse(response.content)
                    all_concepts.extend(result.concepts)
                    print(f"      -> Extracted {len(result.concepts)} concepts from chunk {i+1}.")
                except Exception as e:
                    print(f"      -> ERROR parsing concepts from chunk {i+1}: {e}")
            
            print(f"      -> Total initial concepts extracted: {len(all_concepts)}")
            
            # 3. Final Aggregation and Filtering Pass
            if not all_concepts:
                return []
                
            print(f"      -> Performing final aggregation and filtering...")
            
            # Format all extracted concepts into a single string for the final LLM pass
            aggregated_concepts_str = "[\n"
            for concept in all_concepts:
                # We dump the concept as JSON, but clean it up to avoid escaping issues
                concept_dict = concept.model_dump()
                aggregated_concepts_str += f"{concept_dict},\n"
            aggregated_concepts_str = aggregated_concepts_str.rstrip(",\n") + "\n]"
            
            # Use the final filtering prompt with the combined concepts as the "paper_text" input
            final_prompt = self._get_extraction_prompt(is_final_pass=True)
            final_chain = final_prompt | self.combiner_llm 

            final_response = final_chain.invoke({
                "paper_text": aggregated_concepts_str, # The input is now the list of concepts
                "max_concepts": max_concepts,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Final Parse
            try:
                final_result = self.parser.parse(final_response.content)
                print(f"      -> Final list contains {len(final_result.concepts)} concepts.")
                return final_result.concepts
            except Exception as e:
                print(f"      -> ERROR parsing final concepts: {e}")
                # Fallback: return the un-filtered concepts if final parsing fails
                return all_concepts[:max_concepts]
            
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
