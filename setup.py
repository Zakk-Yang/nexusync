# setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    name="nexusync",
    version="0.2.6",
    author="Zakk Yang",
    author_email="zakkyang@protonmail.com",
    description="A powerful document indexing and querying tool built on top of LlamaIndex",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zakk-Yang/nexusync.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "llama_index>=0.11.17,<0.12",  # Latest stable version
        "llama-index-llms-ollama>=0.3.4,<0.4",  # Compatible with latest llama_index
        "llama-index-embeddings-huggingface>=0.3.1,<0.4",
        "chromadb>=0.3.26",  # Stable version with vector store support
        "llama-index-vector-stores-chroma>=0.3.2,<0.4",
        "torch>=2.1.2,<2.3.1",  # Avoid conflict with Pillow
        "transformers>=4.44,<4.46",  # Version compatible with torch and Huggingface embeddings
        "python-pptx>=0.6.21",  # Latest version
        "Pillow>=10.2.0,<10.4.0",  # Avoid conflicts with torch
        "docx2txt>=0.8",  # Stable version
        "openpyxl>=3.1.2",  # Latest stable release
        "python-dotenv>=1.0.0",  # Updated environment management
        "spacy>=3.4.4,<4.0",  # Compatible with transformers and NLP processing
        "flask>=2.3.3",  # Latest version of Flask for web app
    ],
    include_package_data=True,  # Ensures files specified in MANIFEST.in are included
)
