# src/core/indexing_functions.py

import shutil
import os
from nexusync.core.indexer import Indexer
from nexusync.utils.logging_config import get_logger
from llama_index.core import Settings
from typing import List
import os
from typing import List, Optional, Dict, Any
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from nexusync.utils.logging_config import get_logger
import shutil
from llama_index.core import Settings
from nexusync.models.embedding_models import set_embedding_model
from nexusync.models.language_models import set_language_model

logger = get_logger("nexusync.core.indexing_functions")


def rebuild_index(
    input_dirs: List[str],
    openai_model_yn: bool,
    embedding_model: str,
    language_model: str,
    temperature: float,
    chroma_db_dir: str,
    index_persist_dir: str,
    chroma_collection_name: str,
    chunk_overlap: int,
    chunk_size: int,
    recursive: bool,
):
    """
    Standalone function to rebuild the index.

    This function can be called independently of NexuSync initialization.
    """
    logger.info("Starting index rebuild process...")

    Settings.chunk_overlap = chunk_overlap
    Settings.chunk_size = chunk_size
    # Initialize the embedding and language model
    if openai_model_yn:
        set_embedding_model(openai_model=embedding_model)
        set_language_model(openai_model=language_model)

    else:
        set_embedding_model(huggingface_model=embedding_model)
        set_language_model(ollama_model=language_model, temperature=temperature)

    # Step 1: Delete the existing index directory
    if os.path.exists(index_persist_dir):
        logger.info(f"Deleting existing index directory: {index_persist_dir}")
        shutil.rmtree(index_persist_dir)
    else:
        logger.warning(
            f"Index directory {index_persist_dir} does not exist. Skipping deletion."
        )

    # Step 2: Delete the Chroma database directory
    if os.path.exists(chroma_db_dir):
        logger.info(f"Deleting existing Chroma DB directory: {chroma_db_dir}")
        shutil.rmtree(chroma_db_dir)
    else:
        logger.warning(
            f"Chroma DB directory {chroma_db_dir} does not exist. Skipping deletion."
        )

    try:
        storage_context = StorageContext.from_defaults(persist_dir=index_persist_dir)
        index = load_index_from_storage(storage_context)
        logger.info("Index already built. Loading from disk.")
    except FileNotFoundError:
        logger.warning("Index not found. Building a new index.")
        document_list = []
        for file_path in input_dirs:
            if not os.path.isdir(file_path):
                logger.error(f"Directory {file_path} does not exist.")
                raise ValueError(f"Directory {file_path} does not exist.")
            documents = SimpleDirectoryReader(
                file_path, filename_as_id=True, recursive=recursive
            ).load_data()
            logger.info(f"Loaded {len(documents)} chunks from {file_path}.")
            document_list.extend(documents)
        index = VectorStoreIndex.from_documents(document_list)
        index.storage_context.persist(persist_dir=index_persist_dir)
        chroma_client = chromadb.PersistentClient(path=chroma_db_dir)
        chroma_collection = chroma_client.get_or_create_collection(
            chroma_collection_name
        )
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(
            persist_dir=index_persist_dir, vector_store=vector_store
        )

        if not document_list:
            logger.error("No documents found to build the index.")
            raise ValueError("No documents found to build the index.")

        logger.info("Index Built.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during initiation: {e}")
        raise
