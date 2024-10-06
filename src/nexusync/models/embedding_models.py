from typing import Optional
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
import os
from dotenv import load_dotenv


def set_embedding_model(
    openai_model: Optional[str] = None, huggingface_model: Optional[str] = None
) -> None:
    """
    Set up the embedding model for the index.

    Args:
        openai_model (Optional[str]): Name of the OpenAI embedding model.
        huggingface_model (Optional[str]): Name of the HuggingFace embedding model.

    Raises:
        ValueError: If both or neither embedding model is specified.
    """
    load_dotenv()

    if (openai_model and huggingface_model) or (
        not openai_model and not huggingface_model
    ):
        raise ValueError(
            "Specify either OpenAI or HuggingFace embedding model, not both or neither."
        )

    if openai_model:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables.")
        Settings.embed_model = OpenAIEmbedding(
            model=openai_model, api_key=openai_api_key
        )
        print(f"Using OpenAI embedding model: {openai_model}")
    else:
        Settings.embed_model = HuggingFaceEmbedding(model_name=huggingface_model)
        print(f"Using HuggingFace embedding model: {huggingface_model}")
