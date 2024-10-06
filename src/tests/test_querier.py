# test_querier.py
import pytest
from nexusync.core.indexer import Indexer
from nexusync.core.querier import Querier


@pytest.fixture
def sample_index(tmp_path):
    test_dir = tmp_path / "test_docs"
    test_dir.mkdir()
    (test_dir / "test1.txt").write_text("The capital of France is Paris.")
    (test_dir / "test2.txt").write_text("The Eiffel Tower is located in Paris.")

    indexer = Indexer(input_dirs=[str(test_dir)])
    indexer._build_new_index()
    return indexer.index


def test_querier_initialization(sample_index):
    querier = Querier(sample_index)
    assert querier is not None
    assert querier.index == sample_index


def test_querier_query(sample_index):
    querier = Querier(sample_index)
    response = querier.query(
        "What is the capital of France?",
        "Context: {context_str}\nQuestion: {query_str}\nAnswer:",
    )
    assert "Paris" in response["response"]


def test_querier_get_relevant_documents(sample_index):
    querier = Querier(sample_index)
    docs = querier.get_relevant_documents("Eiffel Tower")
    assert len(docs) > 0
    assert any("Eiffel Tower" in doc["content"] for doc in docs)
