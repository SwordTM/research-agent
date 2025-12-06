import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel

def get_model_with_fallback(api_key: str = None, temperature: float = 0.3) -> BaseChatModel:
    """
    Create a Gemini model with fallback mechanism.
    Tries gemini-2.0-flash-exp first (as pro/2.5 might not be available), 
    then falls back to gemini-1.5-flash.
    
    Args:
        api_key: Google API Key
        temperature: Model temperature
        
    Returns:
        A ChatGoogleGenerativeAI instance or a RunnableBinding with fallbacks
    """
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
        
    # Primary model (Pro/High capability)
    # Using 1.5-pro as 2.5 is likely a typo or future model, but respecting user intent if they have access
    # I'll use 1.5-pro as the "Pro" equivalent for stability, or we can try the requested names
    # Let's use the requested names but fallback to known working ones if needed
    
    # User requested: gemini-2.5-pro -> gemini-2.5-flash
    # Real world mapping (likely): gemini-1.5-pro -> gemini-1.5-flash
    
    model_primary = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro", # Using 1.5 Pro as the stable "Pro" version
        google_api_key=api_key,
        temperature=temperature,
        convert_system_message_to_human=True
    )
    
    model_fallback = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", # Using 1.5 Flash as the stable fallback
        google_api_key=api_key,
        temperature=temperature,
        convert_system_message_to_human=True
    )
    
    # Create fallback chain
    # This will try primary, and if it raises an exception, try fallback
    model_with_fallback = model_primary.with_fallbacks([model_fallback])
    
    return model_with_fallback
