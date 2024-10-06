import pytest
from nexusync.core.indexer import Indexer

def test_indexer_initialization():
    indexer = Indexer(input_dirs=["test_docs"])
    assert indexer is not None
    assert indexer.input_dirs == ["test_docs"]

def test_indexer_build_new_index(tmp_path):
    # Create a temporary directory with some test files
    test_dir = tmp_path / "test_docs"
    test_dir.mkdir()
    (test_dir / "test1.txt").write_text("This is a test document.")
    (test_dir / "test2.txt").write_text("This is another test document.")

    indexer = Indexer(input_dirs=[str(test_dir)])
    indexer._build_new_index()
    
    assert indexer.index is not None
    # Add more specific assertions about the index content

def test_indexer_upinsert(tmp_path):
    # Similar to test_indexer_build_new_index, but test the upinsert method
    # Create initial documents, build index, then add/modify documents and upinsert
    pass

def test_indexer_delete(tmp_path):
    # Test the delete method
    # Create documents, build index, delete some files, then call delete method
    pass
