# src/models/__init__.py

from .embedding_models import set_embedding_model
from .language_models import set_language_model

__all__ = ["set_embedding_model", "set_language_model"]
