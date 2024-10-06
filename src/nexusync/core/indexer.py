# querier.py

import os
import logging
from typing import List, Optional, Dict, Any
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)

from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import logging


class Indexer:
    def __init__(
        self,
        input_dirs: List[str],
        recursive: bool = True,
        chroma_db_dir: str = "chroma_db",
        index_persist_dir: str = "index_storage",
        chroma_collection_name: str = "my_collection",
    ):
        """
        Initialize the Indexer with the given parameters.

        Args:
            input_dirs (List[str]): A list of directory paths containing the documents to be indexed.
                                    These directories will be scanned for documents during indexing operations.

            recursive (bool, optional): If True, subdirectories within input_dirs will also be scanned for documents.
                                        Defaults to True.

            chroma_db_dir (str, optional): The directory where the Chroma database will be stored.
                                           Chroma is used as the vector store for efficient similarity search.
                                           Defaults to "chroma_db".

            index_persist_dir (str, optional): The directory where the index will be persisted to disk.
                                               This allows for faster loading of pre-built indexes.
                                               Defaults to "index_storage".

            chroma_collection_name (str, optional): The name of the collection within the Chroma database.
                                                    This allows for multiple distinct indexes within the same database.
                                                    Defaults to 'my_collection'.

        Attributes:
            input_dirs (List[str]): Stores the list of input directories.
            recursive (bool): Stores the recursive flag for directory scanning.
            chroma_db_dir (str): Stores the Chroma database directory path.
            index_persist_dir (str): Stores the index persistence directory path.
            chroma_collection_name (str): Stores the Chroma collection name.
            index (VectorStoreIndex): Will store the actual index once it's created or loaded.
                                      Initially set to None.
            logger (logging.Logger): A logger instance for this class, used for logging operations and errors.

        Note:
            The __init__ method doesn't create the index immediately. Instead, it calls the _initiate method,
            which either loads an existing index or builds a new one.
        """
        self.input_dirs = input_dirs
        self.recursive = recursive
        self.chroma_db_dir = chroma_db_dir
        self.index_persist_dir = index_persist_dir
        self.chroma_collection_name = chroma_collection_name
        self.index = None
        self.logger = logging.getLogger(__name__)
        self._initiate()  # This will either load an existing index or create a new one

    def _initiate(self):
        """Initialize the index by loading from disk or creating a new one."""
        try:
            self.storage_context = StorageContext.from_defaults(
                persist_dir=self.index_persist_dir
            )
            self.index = VectorStoreIndex.load_from_storage(self.storage_context)
            self.logger.info("Index loaded from disk.")
        except FileNotFoundError:
            self.logger.warning("Index not found. Building a new index.")
            self._build_new_index()

    def _build_new_index(self):
        """Build a new index from the input directories."""
        documents = []
        for input_dir in self.input_dirs:
            if not os.path.isdir(input_dir):
                self.logger.error(f"Directory {input_dir} does not exist.")
                raise ValueError(f"Directory {input_dir} does not exist.")
            docs = SimpleDirectoryReader(
                input_dir, recursive=self.recursive, filename_as_id=True
            ).load_data()
            self.logger.info(f"Loaded {len(docs)} documents from {input_dir}.")
            documents.extend(docs)

        if not documents:
            self.logger.error("No documents found to build the index.")
            raise ValueError("No documents found to build the index.")

        self.index = VectorStoreIndex.from_documents(documents)
        self._persist_index()

    def _persist_index(self):
        """Persist the index to disk."""
        chroma_client = chromadb.PersistentClient(path=self.chroma_db_dir)
        chroma_collection = chroma_client.get_or_create_collection(
            self.chroma_collection_name
        )
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        self.storage_context = StorageContext.from_defaults(
            persist_dir=self.index_persist_dir, vector_store=vector_store
        )
        self.index.storage_context.persist(persist_dir=self.index_persist_dir)
        self.logger.info("Index persisted to disk.")

    def upinsert(self):
        """Smartly upsert (update or insert) documents into the index based on changes or new additions."""
        total_documents = 0
        total_refreshed = 0

        for input_dir in self.input_dirs:
            self.logger.info(f"Processing directory: {input_dir}")
            documents = SimpleDirectoryReader(
                input_dir, recursive=self.recursive, filename_as_id=True
            ).load_data()
            total_documents += len(documents)
            self.logger.info(f"Loaded {len(documents)} documents from {input_dir}")

            refreshed_docs = self.index.refresh_ref_docs(documents)
            num_refreshed = sum(refreshed_docs)
            total_refreshed += num_refreshed
            self.logger.info(f"Updated {num_refreshed} documents in {input_dir}")

            for doc, is_refreshed in zip(documents, refreshed_docs):
                if is_refreshed:
                    doc_path = doc.metadata.get("file_path", "Unknown path")
                    self.logger.info(f"Updated document: {doc_path}")

        self.logger.info(
            f"Upsert operation completed. Total documents processed: {total_documents}, updated or inserted: {total_refreshed}"
        )

    def delete(self):
        """Delete documents from the index if their corresponding files have been deleted from the filesystem."""
        ref_doc_info = self.index.ref_doc_info
        current_files = set()
        for input_dir in self.input_dirs:
            for root, _, files in os.walk(input_dir):
                for file in files:
                    current_files.add(os.path.join(root, file))

        deleted_docs = []
        for doc_id, info in ref_doc_info.items():
            if info.metadata.get("file_path") not in current_files:
                deleted_docs.append(doc_id)

        if deleted_docs:
            self.logger.info(f"Deleting {len(deleted_docs)} documents from the index.")
            for doc_id in deleted_docs:
                self.index.delete_ref_doc(doc_id, delete_from_docstore=True)
            self.logger.info("Deletion process completed.")
        else:
            self.logger.info("No deleted files found.")

    def refresh(self):
        """Refresh the index by performing both upinsert and delete operations."""
        self.logger.info("Starting index refresh process...")
        self.upinsert()
        self.delete()
        self.logger.info("Index refresh completed.")

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the current index."""
        return {
            "num_documents": len(self.index.ref_doc_info),
            "index_persist_dir": self.index_persist_dir,
            "chroma_db_dir": self.chroma_db_dir,
            "chroma_collection_name": self.chroma_collection_name,
        }
