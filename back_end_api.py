# back_end_api.py
from flask import Flask, request, jsonify, Response, send_from_directory
import json
import logging
from nexusync import NexuSync, rebuild_index

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configuration Parameters
OPENAI_MODEL_YN = False
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
LANGUAGE_MODEL = "llama3.2"
TEMPERATURE = 0.4
INPUT_DIRS = ["sample_docs/"]  # Can include multiple paths
CHROMA_DB_DIR = "chroma_db"
INDEX_PERSIST_DIR = "index_storage"
CHROMA_COLLECTION_NAME = "my_collection"
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 20
RECURSIVE = True


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

ns = NexuSync(
    input_dirs=INPUT_DIRS,
    openai_model_yn=False,
    embedding_model=EMBEDDING_MODEL,
    language_model=LANGUAGE_MODEL,
    temperature=TEMPERATURE,
    chroma_db_dir=CHROMA_DB_DIR,
    index_persist_dir=INDEX_PERSIST_DIR,
    chroma_collection_name=CHROMA_COLLECTION_NAME,
    chunk_overlap=CHUNK_OVERLAP,
    chunk_size=CHUNK_SIZE,
    recursive=RECURSIVE,
)


# Initialize the Chat Engine Once
ns.initialize_stream_chat(
    text_qa_template=text_qa_template, chat_mode="context", similarity_top_k=3
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
def rebuild_index_route():
    global ns, EMBEDDING_MODEL, LANGUAGE_MODEL, TEMPERATURE, INPUT_DIRS

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # Update global variables
        EMBEDDING_MODEL = data.get("embedding_model", EMBEDDING_MODEL)
        LANGUAGE_MODEL = data.get("llm_model", LANGUAGE_MODEL)
        TEMPERATURE = data.get("temperature", TEMPERATURE)
        INPUT_DIRS = data.get("input_dirs", INPUT_DIRS)

        # Rebuild index
        rebuild_index(
            input_dirs=INPUT_DIRS,
            openai_model_yn=OPENAI_MODEL_YN,
            embedding_model=EMBEDDING_MODEL,
            language_model=LANGUAGE_MODEL,
            temperature=TEMPERATURE,
            chroma_db_dir=CHROMA_DB_DIR,
            index_persist_dir=INDEX_PERSIST_DIR,
            chroma_collection_name=CHROMA_COLLECTION_NAME,
            chunk_overlap=CHUNK_OVERLAP,
            chunk_size=CHUNK_SIZE,
            recursive=RECURSIVE,
        )

        # Reinitialize NexuSync
        ns = NexuSync(
            input_dirs=INPUT_DIRS,
            openai_model_yn=OPENAI_MODEL_YN,
            embedding_model=EMBEDDING_MODEL,
            language_model=LANGUAGE_MODEL,
            temperature=TEMPERATURE,
            chroma_db_dir=CHROMA_DB_DIR,
            index_persist_dir=INDEX_PERSIST_DIR,
            chroma_collection_name=CHROMA_COLLECTION_NAME,
            chunk_overlap=CHUNK_OVERLAP,
            chunk_size=CHUNK_SIZE,
            recursive=RECURSIVE,
        )

        # Reinitialize the chat engine
        ns.initialize_stream_chat(
            text_qa_template=text_qa_template, chat_mode="context", similarity_top_k=3
        )

        return jsonify({"status": "Index rebuilt successfully"}), 200
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


@app.route("/refresh_index", methods=["POST"])
def refresh_index():
    try:
        ns.indexer.refresh()
        return jsonify({"status": "Index refreshed successfully."}), 200
    except Exception as e:
        logging.error(f"Error refreshing index: {e}", exc_info=True)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    # Run the Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
