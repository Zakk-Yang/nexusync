import os
from dotenv import load_dotenv

load_dotenv()

# Directory settings
DEFAULT_CHROMA_DB_DIR = os.getenv("DEFAULT_CHROMA_DB_DIR", "chroma_db")
DEFAULT_INDEX_PERSIST_DIR = os.getenv("DEFAULT_INDEX_PERSIST_DIR", "index_storage")

# Chroma settings
DEFAULT_CHROMA_COLLECTION_NAME = os.getenv(
    "DEFAULT_CHROMA_COLLECTION_NAME", "my_collection"
)

# Model settings
DEFAULT_OPENAI_EMBEDDING_MODEL = os.getenv(
    "DEFAULT_OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"
)
DEFAULT_HUGGINGFACE_EMBEDDING_MODEL = os.getenv(
    "DEFAULT_HUGGINGFACE_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)
DEFAULT_OPENAI_LANGUAGE_MODEL = os.getenv(
    "DEFAULT_OPENAI_LANGUAGE_MODEL", "gpt-4o-mini"
)
DEFAULT_OLLAMA_LANGUAGE_MODEL = os.getenv("DEFAULT_OLLAMA_LANGUAGE_MODEL", "llama3.2")

# Query settings
DEFAULT_SIMILARITY_TOP_K = int(os.getenv("DEFAULT_SIMILARITY_TOP_K", "3"))
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))

# Logging settings
DEFAULT_LOG_LEVEL = os.getenv("DEFAULT_LOG_LEVEL", "INFO")
DEFAULT_LOG_FILE = os.getenv("DEFAULT_LOG_FILE", "nexusync.log")

# Other settings
RECURSIVE_DIRECTORY_SEARCH = (
    os.getenv("RECURSIVE_DIRECTORY_SEARCH", "True").lower() == "true"
)
