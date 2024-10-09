# src/utils/language_models.py

from typing import Optional
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
import os
from dotenv import load_dotenv
from nexusync.utils.logging_config import get_logger


def set_language_model(
    openai_model: Optional[str] = None,
    ollama_model: Optional[str] = None,
    temperature: Optional[float] = 0.7,
) -> None:
    """
    Set up the language model for the index.

    Args:
        openai_model (Optional[str]): Name of the OpenAI model.
        ollama_model (Optional[str]): Name of the Ollama model.
        temperature (Optional[float]): Temperature for the language model.

    Raises:
        ValueError: If both or neither model is specified, or if OpenAI API key is missing.
    """
    logger = get_logger("nexusync.utils.embedding_models.set_language_model")
    load_dotenv()

    if (openai_model and ollama_model) or (not openai_model and not ollama_model):
        raise ValueError("Specify either OpenAI or Ollama model, not both or neither.")

    if openai_model:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables.")
        Settings.llm = OpenAI(
            model=openai_model, temperature=temperature, api_key=openai_api_key
        )
        logger.info(f"Using OpenAI LLM model: {openai_model}")
    else:
        Settings.llm = Ollama(model=ollama_model, temperature=temperature)
        logger.info(f"Using Ollama LLM model: {ollama_model}")
