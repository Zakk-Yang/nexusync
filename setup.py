# setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ollama_rag",
    version="0.4.1",
    author="Zakk Yang",
    author_email="zakkyang@protonmail.com",
    description="A RAG (Retrieval-Augmented Generation) system using Llama Index and ChromaDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zakk-Yang/ollama-rag.git",  # Replace with your repository URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Choose your license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "llama_index",
        "llama-index-llms-ollama",
        "llama-index-embeddings-huggingface",
        "chromadb",
        "llama-index-vector-stores-chroma",
        "pandas",
    ],
    include_package_data=True,  # Ensures files specified in MANIFEST.in are included
    # entry_points={
    #     "console_scripts": [
    #         "ollama-rag=ollama_rag.ollama_rag:main",  # Points to the standalone main function
    #     ],
    # },
)
