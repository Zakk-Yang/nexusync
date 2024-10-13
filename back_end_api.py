# back_end_api.py
from flask import Flask, request, jsonify, Response, send_from_directory
import json
import logging
from nexusync import NexuSync, rebuild_index

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configuration Parameters
# For non-openai model:
# OPENAI_MODEL_YN = False
# EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
# LANGUAGE_MODEL = "llama3.2"

# For openai model: need to create .env in the src folder to include OPENAI_API_KEY = 'sk-xxx'
OPENAI_MODEL_YN = True
EMBEDDING_MODEL = "text-embedding-3-large"
LANGUAGE_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.4
INPUT_DIRS = ["sample_docs/"]  # Can include multiple paths
CHROMA_DB_DIR = "chroma_db"
INDEX_PERSIST_DIR = "index_storage"
CHROMA_COLLECTION_NAME = "my_collection"
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 20
RECURSIVE = True


# Define the QA Prompt Template
text_qa_template = """
Context Information:
{context_str}
Query: {query_str}
Instructions:
You are helping NHS doctors to review patients' medical records and give interperetations on the results.
Carefully read the context information and the query.
If the query is in the format [patient_id, summary_report], generate a summary report using the template below.
Use the available information from the context to fill in each section.
Include relevant dates and timeline information in each section.
If information for a section is not available, state "No information available" for that section.
Provide concise and accurate information based on the given context.
Adapt the template as needed to fit the patient's specific medical history and conditions.

Summary Report Template:

Patient Summary Report for {patient_id}
1. Demographics

Name: [First Name] [Last Name]
Date of Birth: [DOB]
Gender: [Gender]
Contact Information:

Address: [Address]
Phone: [Phone Number]
Email: [Email Address]



2. Past Medical History & Procedures

Chronic Conditions: [List of chronic conditions with diagnosis dates]
Major Illnesses: [List of major illnesses with dates]
Surgical Procedures: [List of surgical procedures with dates]
Other Significant Medical Events: [List with dates]
Your interpretation: [Your interpretation of the medical records]

3. Medication History
[List each current medication with the following information]

Name: [Medication Name]
Dosage: [Dosage]
Frequency: [Frequency]
Start Date: [Start Date]
Prescriber: [Prescriber Name]
Purpose: [Brief description of why the medication is prescribed]

[Include a brief list of significant past medications, if available]
4. Allergies and Adverse Reactions

Medication Allergies: [List or "No known medication allergies"]
Other Allergies: [List or "No known other allergies"]
Adverse Reactions: [List any significant adverse reactions to treatments or medications]

5. Social History & Occupation

Occupation: [Current or most recent occupation]
Smoking Status: [Current smoker, former smoker, never smoker]
Alcohol Use: [Description of alcohol use]
Recreational Drug Use: [If applicable]
Exercise Habits: [Brief description]
Diet: [Any significant dietary information]
Other Relevant Social Factors: [e.g., living situation, support system]
Your interpretation: [Your interpretation of the social history]

6. Physical Examination & Vital Signs
Most Recent Vital Signs (Date: [Date of most recent vital signs])

Blood Pressure: [BP]
Heart Rate: [HR]
Respiratory Rate: [RR]
Temperature: [Temp]
Oxygen Saturation: [O2 Sat]
Weight: [Weight]
Height: [Height]
BMI: [BMI]
Your interpretation: [Your interpretation of the vital signs]
[Include any significant physical examination findings]

7. Laboratory Results
[List most recent significant laboratory tests with dates, results, and normal ranges]

8. Imaging and Diagnostic Results
[List recent imaging studies and other diagnostic tests with dates and summary of results]

9. Treatment Plan and Interventions

Current Treatment Plans: [List current treatments or interventions]
Ongoing Therapies: [e.g., physical therapy, chemotherapy, dialysis]
Recent Changes in Management: [Any recent significant changes in treatment]
Your interpretation: [Your interpretation of the treatment plan]

10. Immunizations
[List relevant immunizations with dates]

11. Upcoming Appointments and Follow-ups
[List any scheduled appointments with dates, types, and locations]


Answer: [Generate the report based on the template above, filling in the available information from the context]

Answer: """

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
            response_generator = ns.chat_engine.chat_stream(user_input)

            for item in response_generator:
                if isinstance(item, str):
                    # Stream individual tokens
                    yield json.dumps({"response": item}) + "\n"
                elif isinstance(item, dict):
                    # Final response with metadata
                    metadata = item.get("metadata", {})
                    sources = metadata.get("sources", [])

                    # Extract source file paths
                    for source in sources:
                        metadata_info = source.get("metadata", {})
                        file_path = metadata_info.get("file_path", "Unknown source")
                        source_file_paths.append(file_path)

                    # Remove duplicates while preserving order
                    source_file_paths = list(dict.fromkeys(source_file_paths))

                    # Format the source file paths
                    if source_file_paths:
                        sources_formatted = "\n".join(
                            f"- {path}" for path in source_file_paths
                        )
                        yield json.dumps(
                            {"sources": sources_formatted, "final": True}
                        ) + "\n"
                    else:
                        yield json.dumps(
                            {"sources": "No sources found", "final": True}
                        ) + "\n"

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
    app.run(host="0.0.0.0", port=2024, debug=True)
