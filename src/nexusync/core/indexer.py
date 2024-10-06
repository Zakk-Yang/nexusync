# src/core/indexer.py

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
        self.logger = get_logger("nexusync.core.indexer")  # Use full logger name
        self.input_dirs = input_dirs
        self.recursive = recursive
        self.chroma_db_dir = chroma_db_dir
        self.index_persist_dir = index_persist_dir
        self.chroma_collection_name = chroma_collection_name
        self.index = None
        self._initiate()

    def _initiate(self):
        try:
            self.storage_context = StorageContext.from_defaults(
                persist_dir=self.index_persist_dir
            )
            self.index = load_index_from_storage(self.storage_context)
            self.logger.info("Index already built. Loading from disk.")
        except FileNotFoundError:
            self.logger.warning("Index not found. Building a new index.")
            self.document_list = []
            for file_path in self.input_dirs:
                if not os.path.isdir(file_path):
                    self.logger.error(f"Directory {file_path} does not exist.")
                    raise ValueError(f"Directory {file_path} does not exist.")
                documents = SimpleDirectoryReader(
                    file_path, filename_as_id=True
                ).load_data()
                self.logger.info(f"Loaded {len(documents)} chunks from {file_path}.")
                self.document_list.extend(documents)
            self.index = VectorStoreIndex.from_documents(self.document_list)
            self.index.storage_context.persist(persist_dir=self.index_persist_dir)
            chroma_client = chromadb.PersistentClient(path=self.chroma_db_dir)
            chroma_collection = chroma_client.get_or_create_collection(
                self.chroma_collection_name
            )
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            self.storage_context = StorageContext.from_defaults(
                persist_dir=self.index_persist_dir, vector_store=vector_store
            )

            if not self.document_list:
                self.logger.error("No documents found to build the index.")
                raise ValueError("No documents found to build the index.")

            self.logger.info("Index Built.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during initiation: {e}")
            raise

    def refresh(self):
        """Refresh the index by performing both upinsert and delete operations."""
        self.logger.info("Starting index refresh process...")
        try:
            # Step 1: Collect current files
            current_files = set()
            for input_dir in self.input_dirs:
                for root, _, files in os.walk(input_dir):
                    for file in files:
                        current_files.add(os.path.abspath(os.path.join(root, file)))

            # Step 2: Perform upinsert (this will add new and update existing documents)
            self.upinsert()

            # Step 3: Perform delete (this will remove documents that no longer exist)
            self.delete(current_files)

            # Step 4: Verify and log the results
            updated_stats = self.get_index_stats()
            self.logger.info(
                f"Index refresh completed. Current file count: {updated_stats['num_documents']}"
            )
            self.logger.info(f"Total files in input directories: {len(current_files)}")

            if updated_stats["num_documents"] != len(current_files):
                self.logger.warning(
                    f"Mismatch between indexed documents ({updated_stats['num_documents']}) and files in directories ({len(current_files)})"
                )

        except Exception as e:
            self.logger.error(
                f"An error occurred during index refresh: {e}", exc_info=True
            )
            raise

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
            num_refreshed = sum(1 for r in refreshed_docs if r)
            total_refreshed += num_refreshed
            self.logger.info(f"Updated {num_refreshed} documents in {input_dir}")

            for doc, is_refreshed in zip(documents, refreshed_docs):
                if is_refreshed:
                    doc_path = doc.metadata.get("file_path", "Unknown path")
                    self.logger.info(f"Updated document: {doc_path}")

        self.logger.info(
            f"Upsert operation completed. Total chunks processed: {total_documents}, updated or inserted: {total_refreshed} files"
        )

    def delete(self, current_files: set):
        """Delete documents from the index if their corresponding files have been deleted from the filesystem."""
        ref_doc_info = self.index.ref_doc_info
        deleted_docs = []

        for doc_id, info in ref_doc_info.items():
            file_path = info.metadata.get("file_path")
            if file_path and os.path.abspath(file_path) not in current_files:
                deleted_docs.append(doc_id)

        if deleted_docs:
            self.logger.info(f"Deleting {len(deleted_docs)} files from the index.")
            for doc_id in deleted_docs:
                self.index.delete_ref_doc(doc_id, delete_from_docstore=True)
            self.logger.info("Deletion process completed.")
        else:
            self.logger.info("No deleted files found.")

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the current index."""
        # Count unique file paths in the index
        unique_files = set()
        for doc_id, info in self.index.ref_doc_info.items():
            file_path = info.metadata.get("file_path")
            if file_path:
                unique_files.add(file_path)

        return {
            "num_documents": len(unique_files),  # Count of unique documents
            "num_nodes": len(self.index.ref_doc_info),  # Total number of nodes
            "index_persist_dir": self.index_persist_dir,
            "chroma_db_dir": self.chroma_db_dir,
            "chroma_collection_name": self.chroma_collection_name,
        }
