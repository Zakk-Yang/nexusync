# setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    name="nexusync",
    version="0.2.2",
    author="Zakk Yang",
    author_email="zakkyang@protonmail.com",
    description="A powerful document indexing and querying tool built on top of LlamaIndex",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zakk-Yang/nexusync.git",  # Replace with your repository URL
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
        "torch",
        "transformers",
        "python-pptx",
        "Pillow",
        "docx2txt",
        "openpyxl",
        "python-dotenv",
        "spacy",
        "flask",
    ],
    include_package_data=True,  # Ensures files specified in MANIFEST.in are included
)
