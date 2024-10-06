# test_chat_engine.py

import pytest
from nexusync.core.indexer import Indexer
from nexusync.core.chat_engine import ChatEngine

@pytest.fixture
def sample_index(tmp_path):
    test_dir = tmp_path / "test_docs"
    test_dir.mkdir()
    (test_dir / "test1.txt").write_text("NexuSync is a document indexing and querying tool.")
    (test_dir / "test2.txt").write_text("It uses advanced NLP techniques for efficient searching.")
    
    indexer = Indexer(input_dirs=[str(test_dir)])
    indexer._build_new_index()
    return indexer.index

def test_chat_engine_initialization(sample_index):
    chat_engine = ChatEngine(sample_index)
    assert chat_engine is not None
    assert chat_engine.index == sample_index

def test_chat_engine_chat(sample_index):
    chat_engine = ChatEngine(sample_index)
    chat_engine.initialize_chat_engine("Context: {context_str}\nHuman: {query_str}\nAI:")
    response = chat_engine.chat("What is NexuSync?")
    assert "document indexing" in response['response'].lower()

def test_chat_engine_history(sample_index):
    chat_engine = ChatEngine(sample_index)
    chat_engine.initialize_chat_engine("Context: {context_str}\nHuman: {query_str}\nAI:")
    chat_engine.chat("What is NexuSync?")
    chat_engine.chat("What techniques does it use?")
    history = chat_engine.get_chat_history()
    assert len(history) == 2
    assert "NexuSync" in history[0]['query']
    assert "techniques" in history[1]['query']
