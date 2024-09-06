import json
import os
import sys
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_documents(json_output_path):
    """Loads and validates documents from the JSON file."""
    if not os.path.exists(json_output_path):
        logging.error(f"Data file not found: {json_output_path}")
        return None

    try:
        with open(json_output_path, 'r') as file:
            data = json.load(file)
            
            if isinstance(data, dict) and 'error' in data:
                logging.error(f"Process error: {data['error']}")
                return None
            
            if not isinstance(data, list) or any(not isinstance(d, dict) for d in data):
                logging.error("Invalid JSON format. Expected a list of dictionaries.")
                return None
            
            return data
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding error: {e}")
        return None

def main():
    setup_logging()

    if len(sys.argv) != 2:
        logging.error("Usage: python load_script.py <json_output_path>")
        sys.exit(1)
    
    json_output_path = sys.argv[1]

    # Check if the argument is actually an error message
    if json_output_path.startswith("Skipping unsupported file format:"):
        logging.warning(f"Received error message instead of file path: {json_output_path}")
        logging.info("No documents to load. Exiting gracefully.")
        sys.exit(0)

    documents = load_documents(json_output_path)
    if documents:
        logging.info(f"Documents loaded successfully. {len(documents)} documents processed.")
    else:
        logging.warning("No valid documents were loaded.")

if __name__ == "__main__":
    main()

