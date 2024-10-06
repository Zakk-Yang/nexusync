from .core.indexer import Indexer
from .core.querier import Querier
from .core.chat_engine import ChatEngine
from .models.embedding_models import set_embedding_model
from .models.language_models import set_language_model
from .utils.logger import setup_logger
from .utils.file_operations import get_all_files, get_file_hash, get_changed_files
from .config import settings


class NexuSync:
    def __init__(self, input_dirs, **kwargs):
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
        self.indexer.refresh()
