# src/__init__.py

from .core.indexer import Indexer
from .core.querier import Querier
from .core.chat_engine import ChatEngine
from .models.embedding_models import set_embedding_model
from .models.language_models import set_language_model
from nexusync.utils.logging_config import get_logger


class NexuSync:
    def __init__(self, input_dirs, **kwargs):
        # Initialize a logger for the NexuSync class
        self.logger = get_logger("nexusync.NexuSync")
        self.indexer = Indexer(input_dirs, **kwargs)
        self.querier = Querier(self.indexer.index)
        self.chat_engine = ChatEngine(self.indexer.index)

    def set_embedding_model(self, *args, **kwargs):
        set_embedding_model(*args, **kwargs)

    def set_language_model(self, *args, **kwargs):
        set_language_model(*args, **kwargs)

    def query(self, *args, **kwargs):
        return self.querier.query(*args, **kwargs)

    def chat(self, *args, **kwargs):
        return self.chat_engine.chat(*args, **kwargs)

    def refresh_index(self):
        try:
            self.indexer.refresh()
        except Exception as e:
            self.logger.error(f"Error refreshing index: {e}", exc_info=True)

    def get_index_stats(self):
        return self.indexer.get_index_stats()


__all__ = ["NexuSync"]
