import os
from typing import Optional, Any
from utils.logger import logger

def get_llm_instance(provider: str = "gemini", api_key: Optional[str] = None, model_name: Optional[str] = None) -> Optional[Any]:
    """
    Initializes and returns a LangChain LLM instance.
    Supports Google Gemini and OpenAI GPT models.
    Returns None if no valid API key is present.
    """
    provider = provider.lower()

    # Check environment variable if api_key not passed explicitly
    if not api_key:
        if provider in ["gemini", "google"]:
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        elif provider in ["openai", "gpt"]:
            api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        logger.info(f"No API key supplied for provider '{provider}'. Falling back to rule-based engine.")
        return None

    try:
        if provider in ["gemini", "google"]:
            from langchain_google_genai import ChatGoogleGenerativeAI
            # Use Gemini 1.5 Flash (Google AI Studio Free Tier: 15 RPM, 1M TPM, 1500 RPD)
            selected_model = model_name or os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
            
            # List of free-tier model candidates
            model_candidates = [selected_model, "gemini-1.5-flash", "gemini-2.5-flash", "gemini-1.5-pro"]
            
            for candidate in list(dict.fromkeys(model_candidates)):
                try:
                    llm = ChatGoogleGenerativeAI(
                        model=candidate,
                        google_api_key=api_key,
                        temperature=0.1,
                        max_output_tokens=500,
                        convert_system_message_to_human=True
                    )
                    logger.info(f"Initialized Google Gemini Free-Tier Model: '{candidate}'")
                    return llm
                except Exception as candidate_err:
                    logger.warning(f"Candidate model '{candidate}' failed: {candidate_err}. Trying fallback...")

        elif provider in ["openai", "gpt"]:
            from langchain_openai import ChatOpenAI
            selected_model = model_name or "gpt-4o-mini"
            llm = ChatOpenAI(
                model=selected_model,
                api_key=api_key,
                temperature=0.1
            )
            logger.info(f"Initialized OpenAI Chat Model: {selected_model}")
            return llm

    except Exception as e:
        logger.error(f"Failed to initialize LLM provider '{provider}': {e}")
        return None

    return None
