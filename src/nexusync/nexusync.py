# src/nexusync/nexusync.py

from .core.indexer import Indexer
from .core.querier import Querier
from .core.chat_engine import ChatEngine
from .models.embedding_models import set_embedding_model
from .models.language_models import set_language_model
from nexusync.utils.logging_config import get_logger
from typing import List, Dict, Any


class NexuSync:
    def __init__(
        self,
        input_dirs: List[str],
        openai_model_yn: bool = None,
        language_model: str = None,
        embedding_model: str = None,
        temperature: float = 0.4,
        chroma_db_dir: str = "chroma_db",
        index_persist_dir: str = "index_storage",
        chroma_collection_name: str = "my_collection",
        chunk_size: int = 1024,
        chunk_overlap: int = 20,
        recursive: bool = True,
    ):
        self.logger = get_logger("nexusync.NexuSync")
        self.input_dirs = input_dirs
        self.embedding_model = embedding_model
        self.language_model = language_model
        self.temperature = temperature
        self.chroma_db_dir = chroma_db_dir
        self.index_persist_dir = index_persist_dir
        self.chroma_collection_name = chroma_collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.recursive = recursive
        self.openai_model_yn = openai_model_yn
        self._initialize_models()
        self.indexer = Indexer(
            input_dirs=self.input_dirs,
            recursive=self.recursive,
            chroma_db_dir=self.chroma_db_dir,
            index_persist_dir=self.index_persist_dir,
            chroma_collection_name=self.chroma_collection_name,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        self.logger.info("Vectors and Querier initialized successfully.")
        self.index_vector_store = self.indexer.initialize_index()

        # Initialize querier with the indexer
        self.querier = Querier(index=self.index_vector_store)

        # Initialize chat engine with the indexer
        self.chat_engine = ChatEngine(index=self.index_vector_store)

    def _initialize_models(self):
        # Initialize the embedding and language model
        if self.openai_model_yn:
            set_embedding_model(openai_model=self.embedding_model)
            set_language_model(
                openai_model=self.language_model, temperature=self.temperature
            )

        else:
            set_embedding_model(huggingface_model=self.embedding_model)
            set_language_model(
                ollama_model=self.language_model, temperature=self.temperature
            )

    def initialize_stream_chat(
        self,
        text_qa_template: str,
        chat_mode: str = "context",
        similarity_top_k: int = 3,
    ):
        self.chat_engine.initialize_chat_engine(
            text_qa_template=text_qa_template,
            chat_mode=chat_mode,
            similarity_top_k=similarity_top_k,
        )

    def start_chat_stream(self, query: str):
        if not self.chat_engine:
            raise ValueError(
                "Chat engine not initialized. Call initialize_stream_chat first."
            )
        return self.chat_engine.chat_stream(query)

    def start_query(
        self, text_qa_template: str, query: str, similarity_top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Start a query using the initialized Querier.

        Args:
            text_qa_template (str): The template for the QA prompt.
            query (str): The query string.
            similarity_top_k (int, optional): Number of top similar documents to consider. Defaults to 3.

        Returns:
            Dict[str, Any]: A dictionary containing the response and metadata.

        Raises:
            ValueError: If the Querier is not initialized.
        """
        if not self.querier:
            self.logger.error("Querier not initialized. Call initialize_vectors first.")
            raise ValueError("Querier not initialized. Call initialize_vectors first.")

        try:
            self.logger.info(f"Starting query: {query}")
            response = self.querier.query(text_qa_template, query, similarity_top_k)
            self.logger.info("Query completed successfully.")
            return response
        except Exception as e:
            self.logger.error(
                f"An error occurred during query: {str(e)}", exc_info=True
            )
            return {
                "response": f"An error occurred while processing your request: {str(e)}",
                "metadata": {},
            }

    def refresh_index(self):
        self.indexer.refresh()

    def get_index_stats(self):
        return self.indexer.get_index_stats()
