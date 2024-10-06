# NexuSync

NexuSync is a powerful document indexing and querying tool built on top of LlamaIndex. It allows you to efficiently manage, search, and interact with large collections of documents using advanced natural language processing techniques.

## 🌟 Features

- **Smart Document Indexing**: Automatically index documents from specified directories.
- **Efficient Querying**: Use natural language to query your document collection.
- **Upsert Capability**: Easily update or insert new documents into the index.
- **Deletion Handling**: Remove documents from the index when they're deleted from the filesystem.
- **Chat Interface**: Engage in conversational interactions with your document collection.
- **Flexible Embedding Options**: Choose between OpenAI and HuggingFace embedding models.
- **Customizable LLM Integration**: Use OpenAI or Ollama models for language processing.

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/nexusync.git
   cd nexusync
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   Create a `.env` file in the project root and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Basic Usage

1. Initialize NexuSync:
   ```python
   from nexusync import NexuSync

   ns = NexuSync(input_dirs=["path/to/your/documents"])
   ```

2. Build or load the index:
   ```python
   ns.load_index()  # If you have a pre-existing index
   # or
   ns._build_new_index()  # To create a new index
   ```

3. Set up embedding and language models:
   ```python
   ns.set_embedding(openai_embedding_model_name="text-embedding-ada-002")
   ns.setup_llm(openai_model_name="gpt-3.5-turbo")
   ```

4. Query the index:
   ```python
   response = ns.ns_query_engine("What is the capital of France?", qa_prompt_tmpl_str)
   print(response['response'])
   ```

## 🔧 Advanced Usage

### Upsert and Delete Operations

To update your index with new or modified documents:

```python
ns.upinsert()
```

To remove documents from the index that no longer exist in the filesystem:

```python
ns.delete()
```

To perform both operations:

```python
ns.refresh()
```

### Chat Interface

Initialize the chat engine:

```python
ns.initialize_chat_engine(text_qa_template, chat_mode='context')
```

Start a chat session:

```python
response = ns.ns_chat_engine("Tell me about machine learning.")
print(response['response'])
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LlamaIndex](https://github.com/jerryjliu/llama_index) for providing the core indexing and querying capabilities.
- All contributors who have helped shape and improve NexuSync.

## 📞 Support

If you encounter any issues or have questions, please [open an issue](https://github.com/yourusername/nexusync/issues) on our GitHub repository.
