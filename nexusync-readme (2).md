# NexuSync

NexuSync is a lightweight and powerful library for building Retrieval-Augmented Generation (RAG) systems with ease. It provides developers with a simple, user-friendly interface to configure and deploy RAG systems efficiently.

## 🌟 Features

- **Lightweight Design**: NexuSync is built with simplicity in mind, making it easy for developers to integrate and configure RAG systems without unnecessary complexity.
- **User-Friendly Interface**: With intuitive APIs and clear documentation, setting up your RAG system has never been easier.
- **Flexible Document Indexing**: Automatically index documents from specified directories, keeping your knowledge base up-to-date.
- **Efficient Querying**: Use natural language to query your document collection and get relevant answers quickly.
- **Conversational Interface**: Engage in chat-like interactions with your document collection for more intuitive information retrieval.
- **Customizable Embedding Options**: Choose between various embedding models to suit your needs and constraints.
- **Incremental Updates**: Easily update or insert new documents into the index without rebuilding from scratch.
- **Automatic Deletion Handling**: Documents removed from the filesystem are automatically removed from the index.

## 🚀 Quick Start

### Installation

```bash
pip install nexusync
```

### Basic Usage

```python
from nexusync import NexuSync

# Initialize NexuSync
ns = NexuSync(
    input_dirs=["path/to/your/documents"],
    embedding_model="BAAI/bge-base-en-v1.5",
    language_model="llama3.2",
    temperature=0.4
)

# Initialize models and vectors
ns.initialize_models()
ns.initialize_vectors()

# Start a chat session
ns.initialize_stream_chat()

# Query your documents
query = "What are the main features of our product?"
for token in ns.start_chat_stream(query):
    print(token, end='', flush=True)
```

## 🛠️ Configuration

NexuSync offers a range of configuration options to tailor the RAG system to your needs:

- `input_dirs`: List of directories containing documents for indexing
- `embedding_model`: Model used for generating embeddings
- `language_model`: Model used for language tasks
- `temperature`: Controls the creativity of the language model responses
- `chunk_size`: Size of text chunks for creating embeddings
- `chunk_overlap`: Overlap between text chunks to maintain context

## 🔄 Keeping Your Index Up-to-Date

Refresh your document index with a single line of code:

```python
ns.refresh_index()
```

This automatically detects new, modified, or deleted documents and updates the index accordingly.

## 💬 Interactive Chat

Engage in a conversational interface with your documents:

```python
query = "Explain our product's pricing model"
for token in ns.start_chat_stream(query):
    print(token, end='', flush=True)
```

## 🤝 Contributing

We welcome contributions to NexuSync! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information.

## 📄 License

NexuSync is released under the [MIT License](LICENSE).

## 🙏 Acknowledgements

NexuSync is built on top of several amazing open-source projects. We'd like to thank the contributors of LlamaIndex, Hugging Face Transformers, and all the other libraries that make NexuSync possible.

---

Get started with NexuSync today and simplify your RAG system development!
