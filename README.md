# NexuSync

NexuSync is a powerful document indexing and querying tool built on top of LlamaIndex. It allows you to efficiently manage, search, and interact with large collections of documents using advanced natural language processing techniques.

<p align="center">
  <img src="https://raw.githubusercontent.com/Zakk-Yang/nexusync/main/assets/nexusync_logo.png" alt="NexuSync Logo" width="200"/>
</p>

## Features

- **Smart Document Indexing**: Automatically index documents from specified directories, keeping your knowledge base up-to-date.
- **Efficient Querying**: Use natural language to query your document collection and get relevant answers quickly.
- **Upsert Capability**: Easily update/insert new documents or remove documents from the index without rebuilding from scratch. Use `refresh_index`.
- **Chat Interface**: Engage in conversational interactions with your document collection, making information retrieval more intuitive.
- **Flexible Embedding Options**: Choose between OpenAI and HuggingFace embedding models to suit your needs and constraints.
- **Streaming Responses**: Get real-time, token-by-token responses for a more interactive experience.

## Installation

To install NexuSync, run the following command:

```bash
pip install nexusync
```

## Quick Start

Here's a simple example to get you started with NexuSync:

```python
from nexusync import NexuSync
from nexusync.models import set_embedding_model, set_language_model

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
LLM_MODEL = 'llama3.2'
TEMPERATURE = 0.4
INPUT_DIRS = ["../sample_docs"] # can put multiple folder paths

# Set up open-source models from ollama
set_embedding_model(huggingface_model= EMBEDDING_MODEL) 
set_language_model(ollama_model = LLM_MODEL, temperature=TEMPERATURE)\

# Or, set up models for openai models (create .env to include your OPENAI_API_KEY)
# set_embedding_model(openai_model="text-embedding-ada-002")
# set_language_model(openai_model="gtp-4o-mini", temperature=0.4)
```
Next, we initiate the `NexuSync` class and initiate a simple query.

```python
# Initialize NexuSync
ns = NexuSync(input_dirs=INPUT_DIRS)

# Refresh with one line of code (upinsert or delete incrementally)
ns.refresh_index()

# Prepare your instruction prompt
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


# Perform a query
query = "News about Nvidia?"
response = ns.query(text_qa_template = text_qa_template, query = query )

print(f"Query: {query}")
print(f"Response: {response['response']}")
print(f"Response: {response['metadata']}")
```

Chat in a word-by-word stream chat style: 
```python
# Initiate the chat engine once
ns.chat_engine.initialize_chat_engine(text_qa_template, chat_mode="context")

# Print each token as it's generated
response_generator = ns.chat_engine.chat_stream(query)
for item in response_generator:
    if isinstance(item, str):
        print(item, end='', flush=True)
    else:
        # This is the final yield with the full response and metadata
        full_response = item
        break

print("\n\nFull response:", full_response['response'])
print("Metadata:", full_response['metadata'])
```

For more detailed usage examples, check out the demo notebooks.
