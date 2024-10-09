# src/core/querier.py

from typing import List, Optional, Dict, Any
from llama_index.core import (
    VectorStoreIndex,
    PromptTemplate,
)
import logging
from llama_index.core.postprocessor import SentenceEmbeddingOptimizer
from llama_index.core.postprocessor import KeywordNodePostprocessor
from nexusync.utils.logging_config import get_logger


class Querier:
    def __init__(self, index: VectorStoreIndex):
        """
        Initialize the Querier with a VectorStoreIndex.

        Args:
            index (VectorStoreIndex): The index to be used for querying.
        """
        self.index = index
        self.logger = get_logger("nexusync.core.querier")

    def query(
        self, text_qa_template: str, query: str, similarity_top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Query the index using a query engine.

        Args:
            text_qa_template (str): The template for the QA prompt.
            query (str): The query string.
            similarity_top_k (int, optional): Number of top similar documents to consider. Defaults to 3.

        Returns:
            Dict[str, Any]: A dictionary containing the response and metadata.
        """
        try:
            qa_template = PromptTemplate(text_qa_template)
            query_engine = self.index.as_query_engine(
                text_qa_template=qa_template,
                similarity_top_k=similarity_top_k,
                node_postprocessors=[
                    SentenceEmbeddingOptimizer(percentile_cutoff=0.5),
                    KeywordNodePostprocessor(required_keywords=[]),
                ],
            )

            response = query_engine.query(query)

            answer = str(response)
            metadata = {"sources": []}

            if hasattr(response, "source_nodes"):
                for node in response.source_nodes:
                    source_info = {
                        "source_text": node.node.get_text(),
                        "metadata": node.node.metadata,
                    }
                    metadata["sources"].append(source_info)

            return {"response": answer, "metadata": metadata}

        except Exception as e:
            self.logger.error(f"An error occurred during query: {e}", exc_info=True)
            return {
                "response": f"An error occurred while processing your request: {str(e)}",
                "metadata": {},
            }

    def get_relevant_documents(
        self, query: str, num_docs: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant documents for a given query.

        Args:
            query (str): The query string.
            num_docs (int): The number of documents to retrieve. Defaults to 3.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing document info and relevance scores.
        """
        try:
            retriever = self.index.as_retriever(similarity_top_k=num_docs)
            nodes = retriever.retrieve(query)

            relevant_docs = []
            for node in nodes:
                doc_info = {
                    "content": node.node.get_text(),
                    "metadata": node.node.metadata,
                    "score": node.score,
                }
                relevant_docs.append(doc_info)

            return relevant_docs

        except Exception as e:
            self.logger.error(
                f"An error occurred while retrieving relevant documents: {e}",
                exc_info=True,
            )
            return []
