from typing import Dict, Any, List, Generator
from llama_index.core import VectorStoreIndex, PromptTemplate
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.postprocessor import (
    SentenceEmbeddingOptimizer,
    KeywordNodePostprocessor,
)
from nexusync.utils.logging_config import get_logger


class ChatEngine:
    def __init__(self, index: VectorStoreIndex):
        """
        Initialize the ChatEngine with a VectorStoreIndex.

        Args:
            index (VectorStoreIndex): The index to be used for querying in chat.
        """
        self.logger = get_logger("nexusync.core.chat_engine")
        self.chat_engine = None
        self.chat_history = []
        self.index = index

    def initialize_chat_engine(
        self,
        text_qa_template: str,
        chat_mode: str = "context",
        similarity_top_k: int = 3,
    ):
        """
        Initialize the chat engine.

        Args:
            text_qa_template (str): The template for the QA prompt.
            chat_mode (str, optional): The mode for the chat engine. Defaults to 'context'.
            similarity_top_k (int, optional): Number of top similar documents to consider. Defaults to 3.
        """
        qa_template = PromptTemplate(text_qa_template)
        memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
        if not isinstance(self.index, VectorStoreIndex):
            raise ValueError("The index does not contain a valid VectorStoreIndex")

        self.chat_engine = self.index.as_chat_engine(
            memory=memory,
            chat_mode=chat_mode,
            text_qa_template=qa_template,
            similarity_top_k=similarity_top_k,
            node_postprocessors=[
                SentenceEmbeddingOptimizer(percentile_cutoff=0.7),
                KeywordNodePostprocessor(required_keywords=[]),
            ],
        )
        self.logger.info("Chat engine initialized")

    def chat(self, query: str) -> Dict[str, Any]:
        """
        Process a query using the chat engine.

        Args:
            query (str): The user's query string.

        Returns:
            Dict[str, Any]: A dictionary containing the response and metadata.

        Raises:
            ValueError: If the chat engine is not initialized.
        """
        if self.chat_engine is None:
            raise ValueError(
                "Chat engine not initialized. Call initialize_chat_engine first."
            )

        try:
            response = self.chat_engine.chat(query)

            answer = str(response)
            metadata: Dict[str, List[Dict[str, Any]]] = {"sources": []}

            if hasattr(response, "source_nodes"):
                for node in response.source_nodes:
                    source_info = {
                        "source_text": node.node.get_text(),
                        "metadata": node.node.metadata,
                    }
                    metadata["sources"].append(source_info)

            self.chat_history.append({"query": query, "response": answer})

            return {"response": answer, "metadata": metadata}

        except Exception as e:
            self.logger.error(f"An error occurred during chat: {e}", exc_info=True)
            return {
                "response": f"An error occurred while processing your request: {str(e)}",
                "metadata": {},
            }

    def chat_stream(self, query: str) -> Generator[str | Dict[str, Any], None, None]:
        if self.chat_engine is None:
            raise ValueError(
                "Chat engine not initialized. Call initialize_chat_engine first."
            )

        try:
            response_stream = self.chat_engine.stream_chat(query)

            full_response = ""
            for token in response_stream.response_gen:
                full_response += token
                yield token  # Yield each token as it's generated

            # After all tokens have been yielded, prepare and yield the final response with metadata
            metadata = {"sources": []}
            if hasattr(response_stream, "source_nodes"):
                for node in response_stream.source_nodes:
                    source_info = {
                        "source_text": node.node.get_text(),
                        "metadata": node.node.metadata,
                    }
                    metadata["sources"].append(source_info)

            # Append to chat history
            self.chat_history.append({"query": query, "response": full_response})

            # Yield the final response with metadata
            yield {
                "response": full_response,
                "metadata": metadata,
            }

        except Exception as e:
            self.logger.error(
                f"An error occurred during chat streaming: {e}", exc_info=True
            )
            yield {
                "response": f"An error occurred while processing your request: {str(e)}",
                "metadata": {},
            }

    def clear_chat_history(self):
        self.chat_history = []
        self.logger.info("Chat history cleared")

        if hasattr(self.chat_engine, "memory") and self.chat_engine.memory is not None:
            self.chat_engine.memory.clear()
            self.logger.info("Chat engine memory cleared")

    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        Get the current chat history.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing queries and responses.
        """
        return self.chat_history
