import os
from dotenv import load_dotenv

load_dotenv()

USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"


def get_llm():
    """
    Main LLM for Brains 3, 4, 5 — reasoning and judgment.
    Ollama locally, Groq for cloud deployment.
    """
    if USE_OLLAMA:
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model="mistral",
            temperature=0
        )
    else:
        from langchain_groq import ChatGroq
        return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",
            temperature=0
        )


def get_extraction_llm():
    """
    LLM for Brain 2 — claim extraction.
    Same model locally, smaller model on Groq to save tokens.
    """
    if USE_OLLAMA:
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model="mistral",
            temperature=0
        )
    else:
        from langchain_groq import ChatGroq
        return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama3-8b-8192",
            temperature=0
        )