import json
import logging
import multiprocessing
import sys
import os
import traceback
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from documentretriever import runner as doc_retriever
except ImportError as e:
    logging.error(f"Error importing documentretriever.runner: {e}")
    logging.error("Please ensure that the documentretriever folder is in the same directory as this script.")
    sys.exit(1)

def process_clause(clause_data, json_output_path, method, k=5):
    """Process a single clause using the document retriever."""
    try:
        clause_id = clause_data['id']
        clause_text = clause_data['Clause']
        result = doc_retriever.main({
            'processed_docs_path': json_output_path,
            'query': clause_text,
            'method': method,
            'k': k
        })
        return clause_id, method, result
    except Exception as e:
        logging.error(f"Error processing clause: {clause_data} with method {method}. Error: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return clause_data['id'], method, None

def main(json_output_path, retrieval_methods):
    # Check if the processed documents file exists
    if not os.path.exists(json_output_path):
        logging.error(f"Processed documents file not found: {json_output_path}")
        logging.error("Please run the initial_processor.py script first to generate this file.")
        sys.exit(1)

    # Load the JSON file into a list of dictionaries
    try:
        with open('pastcod/output_two_columns.json', 'r') as json_file:
            data_list = json.load(json_file)
    except FileNotFoundError:
        logging.error("File 'pastcod/output_two_columns.json' not found. Please ensure it exists.")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error("Error decoding JSON from 'pastcod/output_two_columns.json'. Please ensure it's valid JSON.")
        sys.exit(1)

    # Ensure data_list is a list of dictionaries
    if isinstance(data_list, dict):
        data_list = [{'id': k, **v} for k, v in data_list.items()]

    # Set up multiprocessing pool
    num_processes = multiprocessing.cpu_count()
    
    # Create a list of all tasks (clause, method combinations)
    tasks = [(clause, json_output_path, method, 5) for clause in data_list for method in retrieval_methods]

    # Process clauses and methods in parallel
    results = {}
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        future_to_task = {executor.submit(process_clause, *task): task for task in tasks}
        for future in as_completed(future_to_task):
            clause_id, method, result = future.result()
            if clause_id not in results:
                results[clause_id] = {}
            results[clause_id][method] = result

    # Collect and process results
    for clause_id, method_results in results.items():
        for method, result in method_results.items():
            if result is not None:
                logging.info(f"Process output for clause ID {clause_id}, method {method}: {result}")
            else:
                logging.warning(f"No result for clause ID {clause_id}, method {method}")

    # Save results to a file
    with open('retrieval_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the document retrieval process.")
    parser.add_argument("--processed_docs", type=str, help="Path to the processed documents JSON file.", 
                        default="all_files/20240906_121937/sys/temp/extracted_data.json")
    parser.add_argument("--method", type=str, nargs='+', choices=["bm25", "tfidf", "flash", "lunr", "fuzz", "embedding", "encoder", "dpr"],
                        default=["bm25"], help="Retrieval methods to use")
    args = parser.parse_args()
    
    main(args.processed_docs, args.method)
