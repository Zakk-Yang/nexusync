# back_end_api.py
from flask import Flask, request, jsonify, Response, send_from_directory
import json
import os
import shutil
import logging
from nexusync.models import set_embedding_model, set_language_model
from nexusync import NexuSync

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configuration Parameters
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
LLM_MODEL = "llama3.2"
TEMPERATURE = 0.4
INPUT_DIRS = ["sample_docs/"]  # Can include multiple paths

# Define the QA Prompt Template
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

# Initialize Embedding and Language Models
set_embedding_model(huggingface_model=EMBEDDING_MODEL)
set_language_model(ollama_model=LLM_MODEL, temperature=TEMPERATURE)

# Initialize NexuSync
ns = NexuSync(input_dirs=INPUT_DIRS)

# Initialize the Chat Engine Once
ns.chat_engine.initialize_chat_engine(
    text_qa_template, chat_mode="context", similarity_top_k=2
)


# Root Route - Serve the index.html file
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Invalid request. 'message' field is required."}), 400

    user_input = data["message"]

    def generate_response():
        try:
            source_file_paths = []
            final_response = ""
            response_generator = ns.chat_engine.chat_stream(user_input)

            for item in response_generator:
                if isinstance(item, str):
                    # Intermediate tokens
                    final_response += item
                    yield json.dumps({"response": item}) + "\n"
                elif isinstance(item, dict):
                    # Final response with metadata
                    full_response = item.get("response", "")
                    metadata = item.get("metadata", {})
                    sources = metadata.get("sources", [])

                    # Log the entire sources list for debugging
                    logging.debug(f"Sources: {sources}")

                    # Extract source file paths
                    for source in sources:
                        # Safely access 'metadata' and 'file_path'
                        metadata_info = source.get("metadata", {})
                        file_path = metadata_info.get("file_path", "Unknown source")
                        source_file_paths.append(file_path)

                    # Remove duplicates while preserving order
                    source_file_paths = list(dict.fromkeys(source_file_paths))

                    if source_file_paths:
                        # Format the source file paths elegantly
                        sources_formatted = "\n".join(
                            f"- {path}" for path in source_file_paths
                        )
                        full_response += f"\n\n**Sources:**\n{sources_formatted}"
                    else:
                        full_response + " No sources found"

                    yield json.dumps({"response": full_response}) + "\n"
        except Exception as e:
            logging.error(f"Error in chat endpoint: {e}", exc_info=True)
            yield json.dumps(
                {"error": f"An error occurred while processing your request: {str(e)}"}
            ) + "\n"

    return Response(generate_response(), mimetype="application/json")


@app.route("/rebuild_index", methods=["POST"])
def rebuild_index():
    """
    Endpoint to rebuild the entire index. This is useful when new documents are added
    or embedding configurations are changed.

    Expected JSON Payload (optional):
    {
        "input_dirs": ["path/to/docs1", "path/to/docs2"],
        "chunk_size": 512,
        "chunk_overlap": 50
    }
    """
    global ns  # Ensure this is at the top of the function

    data = request.get_json() or {}

    input_dirs = data.get("input_dirs", INPUT_DIRS)
    chunk_size = data.get("chunk_size", 1024)
    chunk_overlap = data.get("chunk_overlap", 20)

    try:
        # Delete existing index directory
        if os.path.exists(ns.indexer.index_persist_dir):
            shutil.rmtree(ns.indexer.index_persist_dir)
            app.logger.info(
                f"Deleted existing index directory: {ns.indexer.index_persist_dir}"
            )
        else:
            app.logger.warning(
                f"Index directory {ns.indexer.index_persist_dir} does not exist. Skipping deletion."
            )

        # Delete Chroma DB directory if it exists
        if os.path.exists(ns.indexer.chroma_db_dir):
            shutil.rmtree(ns.indexer.chroma_db_dir)
            app.logger.info(
                f"Deleted existing Chroma DB directory: {ns.indexer.chroma_db_dir}"
            )
        else:
            app.logger.warning(
                f"Chroma DB directory {ns.indexer.chroma_db_dir} does not exist. Skipping deletion."
            )

        # Reinitialize NexuSync with new parameters
        ns_rebuilt = NexuSync(input_dirs=input_dirs)

        # Reinitialize the chat engine with the same template
        ns_rebuilt.chat_engine.initialize_chat_engine(
            text_qa_template, chat_mode="context"
        )

        # Update the global `ns` instance with the rebuilt instance
        ns = ns_rebuilt

        return jsonify({"status": "Index rebuilt successfully."}), 200

    except Exception as e:
        app.logger.error(f"Error rebuilding index: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/reset_chat", methods=["POST"])
def reset_chat():
    try:
        ns.chat_engine.clear_chat_history()
        return jsonify({"status": "Chat history cleared successfully."}), 200
    except Exception as e:
        logging.error(f"Error resetting chat history: {e}", exc_info=True)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    # Run the Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
