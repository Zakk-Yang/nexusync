# NexuSync

NexuSync is a lightweight and powerful library of Retrieval-Augmented Generation (RAG) systems built on top of LlamaIndex. It provides developers with a simple, user-friendly interface to configure and deploy RAG systems efficiently.

<p align="center">
  <img src="https://raw.githubusercontent.com/Zakk-Yang/nexusync/main/assets/nexusync_logo.png" alt="NexuSync Logo" width="200"/>
</p>

## Features

- **Lightweight Design**: NexuSync is built with simplicity in mind, making it easy for developers to integrate and configure RAG systems without unnecessary complexity.
- **User-Friendly Interface**: With intuitive APIs and clear documentation, setting up your RAG system has never been easier.
- **Flexible Document Indexing**: Automatically index documents from specified directories, keeping your knowledge base up-to-date.
- **Efficient Querying**: Use natural language to query your document collection and get relevant answers quickly.
- **Conversational Interface**: Engage in chat-like interactions with your document collection for more intuitive information retrieval.
- **Customizable Embedding Options**: Choose between various embedding models to suit your needs and constraints.
- **Incremental Updates**: Easily update or insert new documents into the index without rebuilding from scratch.
- **Automatic Deletion Handling**: Documents removed from the filesystem are automatically removed from the index.

## Installation

To install NexuSync, run the following command:

```bash
pip install nexusync
```

## Quick Start

Try yourself:

```python
from nexusync import NexuSync

# Customize your parameters
OPENAI_MODEL_YN = False # if False, you will use ollama model
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5" # suggested embedding model
LANGUAGE_MODEL = 'llama3.2' # you need to download ollama model first, please check https://ollama.com/download
TEMPERATURE = 0.4 # range from 0 to 1, higher means higher creativitiy level
CHROMA_DB_DIR = 'chroma_db' # Your path to the chroma db
INDEX_PERSIST_DIR = 'index_storage' # Your path to the index storage
CHROMA_COLLECTION_NAME = 'my_collection' 
INPUT_DIRS = ["../sample_docs"] # can specify multiple document paths
CHUNK_SIZE = 1024 # Size of text chunks for creating embeddings
CHUNK_OVERLAP = 20 # Overlap between text chunks to maintain context
RECURSIVE = True # Recursive or not under one folder

# Initialize vector DB
ns = NexuSync(input_dirs=INPUT_DIRS, 
              openai_model_yn=False, 
              embedding_model=EMBEDDING_MODEL, 
              language_model=LANGUAGE_MODEL, 
              temperature=TEMPERATURE, 
              chroma_db_dir = CHROMA_DB_DIR,
              index_persist_dir = INDEX_PERSIST_DIR,
              chroma_collection_name=CHROMA_COLLECTION_NAME,
              chunk_overlap=CHUNK_OVERLAP,
              chunk_size=CHUNK_SIZE,
              recursive=RECURSIVE
              )

# Prompt Engineering
text_qa_template = (
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information above, I want you to think step by step to answer the query in a crisp manner. "
    "In case you don't know the answer, say 'I don't know!'.\n"
    "Query: {query_str}\n"
    "Answer: "
)

# Initalize the chat engine
ns.initialize_stream_chat(
    text_qa_template=text_qa_template,
    chat_mode="context",
    similarity_top_k=3
)

# Start the stream chat:
query = "how to install NexuSync?"

for item in ns.start_chat_stream(query):
    if isinstance(item, str):
        # This is a token, print or process as needed
        print(item, end='', flush=True)
    else:
        # This is the final response with metadata
        print("\n\nFull response:", item['response'])
        print("Metadata:", item['metadata'])
        break

# Get chat history
chat_history = ns.chat_engine.get_chat_history()
print("Chat History:")
for entry in chat_history:
    print(f"Human: {entry['query']}")
    print(f"AI: {entry['response']}\n")

# If you have files modified, inserted or deleted, you don't need to rebuild all the index
ns.refresh_index()

# Rebuild your index if you changed the embedding/language model
from nexusync import rebuild_index

OPENAI_MODEL_YN = True # if False, you will use ollama model
EMBEDDING_MODEL = "text-embedding-3-large" # suggested embedding model
LANGUAGE_MODEL = 'gpt-4o-mini' # you need to download ollama model first, please check https://ollama.com/download
TEMPERATURE = 0.4 # range from 0 to 1, higher means higher creativitiy level
CHROMA_DB_DIR = 'chroma_db'
INDEX_PERSIST_DIR = 'index_storage'
CHROMA_COLLECTION_NAME = 'my_collection'
INPUT_DIRS = ["../sample_docs"] # can specify multiple document paths
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 20
RECURSIVE = True

rebuild_index(input_dirs=INPUT_DIRS, 
              openai_model_yn=OPENAI_MODEL_YN, 
              embedding_model=EMBEDDING_MODEL, 
              language_model=LANGUAGE_MODEL, 
              temperature=TEMPERATURE, 
              chroma_db_dir = CHROMA_DB_DIR,
              index_persist_dir = INDEX_PERSIST_DIR,
              chroma_collection_name=CHROMA_COLLECTION_NAME,
              chunk_overlap=CHUNK_OVERLAP,
              chunk_size=CHUNK_SIZE,
              recursive=RECURSIVE
              )

# Reinitialize after rebuilding
ns = NexuSync(input_dirs=INPUT_DIRS, 
              openai_model_yn=False, 
              embedding_model=EMBEDDING_MODEL, 
              language_model=LANGUAGE_MODEL, 
              temperature=TEMPERATURE, 
              chroma_db_dir = CHROMA_DB_DIR,
              index_persist_dir = INDEX_PERSIST_DIR,
              chroma_collection_name=CHROMA_COLLECTION_NAME,
              chunk_overlap=CHUNK_OVERLAP,
              chunk_size=CHUNK_SIZE,
              recursive=RECURSIVE
              )
```

## Use Interface
1. git clone or download this project: 
```bash
git clone https://github.com/Zakk-Yang/nexusync.git
```
2. Under the project folder, open the terminal and run
```
python back-end-api.py
```
<p align="center">
  <img src="https://raw.githubusercontent.com/Zakk-Yang/nexusync/main/assets/chat_snapshot.png" alt="Screen Shot" width="600"/>
</p>


For more detailed usage examples, check out the demo notebooks.
