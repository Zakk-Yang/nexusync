# NexuSync

NexuSync is a powerful document indexing and querying tool built on top of LlamaIndex. It allows you to efficiently manage, search, and interact with large collections of documents using advanced natural language processing techniques.

## 🌟 Features

- **Smart Document Indexing**: Automatically index documents from specified directories, keeping your knowledge base up-to-date.
- **Efficient Querying**: Use natural language to query your document collection and get relevant answers quickly.
- **Upsert Capability**: Easily update or insert new documents into the index without rebuilding from scratch.
- **Deletion Handling**: Automatically remove documents from the index when they're deleted from the filesystem.
- **Chat Interface**: Engage in conversational interactions with your document collection, making information retrieval more intuitive.
- **Flexible Embedding Options**: Choose between OpenAI and HuggingFace embedding models to suit your needs and constraints.
- **Customizable LLM Integration**: Use OpenAI or Ollama models for language processing, allowing for both cloud-based and local deployments.

## 🚀 Quick Start

### Installation

```bash
pip install nexusync
```

### Basic Usage

```python
from nexusync import NexuSync

# Initialize NexuSync with your documents directory
ns = NexuSync(input_dirs=["path/to/your/documents", "path/to/your/documents"])

# Set up ollama models
ns.set_embedding_model(hugging_face_embedding_name="BAAI/bge-large-en-v1.5")
ns.set_language_model(ollama_model_name="llama3.2")


# Set up openai models
ns.set_embedding_model(openai_model="text-embedding-ada-002")
ns.set_language_model(openai_model="gpt-4o-mini")

# Query the index (one-time query)
response = ns.query("What is the xxx ?")
print(response['response'])

# Use the chat interface (with context memoery)
chat_response = ns.chat("Tell me more about xxx.")
print(chat_response['response'])

# Refresh the index after adding new folders, or documents in existing folders or deleting any folders
ns.refresh_index()

# Upinsert new or modified documents
ns.upinsert()
print("Index updated with new or modified documents.")

# Delete documents that no longer exist in the filesystem
ns.delete()
print("Removed deleted documents from the index.")

# Get index statistics
stats = ns.get_index_stats()
print(f"Number of documents in index: {stats['num_documents']}")
print(f"Index storage location: {stats['index_persist_dir']}")
```

## 🔧 Why NexuSync is Handy

1. **Effortless Document Management**: 
   NexuSync automatically handles document indexing, updating, and deletion. You don't need to manually manage your document database.

   ```python
   # After adding new documents to your directory
   ns.refresh_index()
   # NexuSync automatically detects and indexes new or modified documents
   ```

2. **Natural Language Queries**: 
   Instead of complex search syntax, use natural language to find information.

   ```python
   response = ns.query("What are the main features of Python?")
   print(response['response'])
   # Get a concise summary of Python's main features from your documents
   ```

3. **Conversational Interface**: 
   Interact with your documents as if you're chatting with an AI assistant.

   ```python
   ns.chat("Explain the concept of machine learning.")
   ns.chat("How does it differ from deep learning?")
   # The chat maintains context, providing coherent follow-up responses
   ```

4. **Flexible Model Selection**: 
   Choose between different embedding and language models based on your requirements.


5. **Scalability**: 
   NexuSync efficiently handles large document collections, making it suitable for personal knowledge bases to enterprise-scale document management.


### Embedding Comparison

```python
ns.set_embedding_model(openai_model="text-embedding-ada-002")
response_openai = ns.query("What is quantum computing?")

ns.set_embedding_model(huggingface_model="sentence-transformers/all-MiniLM-L6-v2")
response_hf = ns.query("What is quantum computing?")

print("OpenAI:", response_openai['response'])
print("HuggingFace:", response_hf['response'])
```

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the Repository
2. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

3. Commit Your Changes
```bash
git commit -am 'Add new feature'
```
4.Push to the Branch
```bash
git push origin feature/your-feature-name
```

## License
The source code for the site is licensed under the MIT license, which you can find in the LICENSE.txt file.
