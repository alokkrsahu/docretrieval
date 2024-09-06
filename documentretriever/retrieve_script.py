import argparse
import json
import sys
import logging
import time
import signal
import os
import hashlib
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from retrievers.main import main as retriever_main

def setup_logging():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def timeout_handler(signum, frame):
    raise TimeoutError("Function call timed out")

def get_cache_key(query, method, k):
    """Generate a unique cache key based on the query, method, and k."""
    return hashlib.md5(f"{query}_{method}_{k}".encode()).hexdigest()

def execute_retrieval(documents, query, method, k, timeout=300):
    """Calls the main retrieval function with a timeout."""
    def retrieval_wrapper():
        return retriever_main(documents, query, method, k)

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    try:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(retrieval_wrapper)
            result = future.result(timeout=timeout)

        logging.info(f"Retriever result type: {type(result)}")
        logging.info(f"Retriever result: {result}")
        return result
    except TimeoutError:
        logging.error(f"Retrieval operation timed out after {timeout} seconds")
        raise
    except Exception as e:
        logging.error(f"Error in retriever_main: {str(e)}")
        raise
    finally:
        signal.alarm(0)

def display_similar_documents(documents, similar_documents):
    """Displays similar documents."""
    try:
        logging.info(f"Type of similar_documents: {type(similar_documents)}")
        logging.info(f"Content of similar_documents: {similar_documents}")
        
        if isinstance(similar_documents, list) and len(similar_documents) > 0:
            for item in similar_documents[0]:
                logging.info(f"Type of item: {type(item)}")
                logging.info(f"Content of item: {item}")
                
                if isinstance(item, dict) and 'id' in item:
                    doc_id = item['id']
                    if isinstance(doc_id, int) and 0 <= doc_id - 1 < len(documents):
                        doc = documents[doc_id - 1]
                        logging.info(f"Similarity: {item}")
                        logging.info(f"Document: {doc}")
                    else:
                        logging.warning(f"Invalid document ID: {doc_id}")
                else:
                    logging.warning(f"Unexpected item structure: {item}")
        else:
            logging.warning("Unexpected similar_documents structure")
    except Exception as e:
        logging.error(f"Error in display_similar_documents: {str(e)}")
        raise

def retrieve_documents(query, method, k, json_output_path):
    """Retrieves documents with caching."""
    cache_key = get_cache_key(query, method, k)
    cache_dir = "retrieval_cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")

    if os.path.exists(cache_file):
        logging.info(f"Cache hit for query: {query}")
        with open(cache_file, 'r') as f:
            return json.load(f)

    logging.info(f"Cache miss for query: {query}")

    try:
        with open(json_output_path, 'r') as file:
            documents = json.load(file)
        
        logging.info(f"Loaded {len(documents)} documents from {json_output_path}")
        logging.info(f"Sample document structure: {documents[0] if documents else 'No documents'}")
        
        similar_documents = execute_retrieval(documents, query, method, k)
        display_similar_documents(documents, similar_documents)

        # Cache the results
        with open(cache_file, 'w') as f:
            json.dump(similar_documents, f)

        return similar_documents

    except FileNotFoundError:
        logging.error(f"File not found: {json_output_path}")
        raise
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in file: {json_output_path}")
        raise
    except TimeoutError:
        logging.error("The retrieval operation timed out")
        raise
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        logging.error(f"Error type: {type(e).__name__}")
        logging.error(f"Error args: {e.args}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Document retrieval.")
    parser.add_argument("query", help="Query for document retrieval.")
    parser.add_argument("method", choices=["bm25", "dpr", "encoder"], help="Retrieval method.")
    parser.add_argument("k", type=int, help="Number of results to retrieve.")
    parser.add_argument("json_output_path", help="Path to the JSON file with documents.")
    args = parser.parse_args()

    if args.json_output_path.startswith("Skipping unsupported file format:"):
        logging.warning(f"Received error message instead of file path: {args.json_output_path}")
        logging.info("No documents to process. Exiting gracefully.")
        sys.exit(0)

    try:
        start_time = time.time()
        
        results = retrieve_documents(args.query, args.method, args.k, args.json_output_path)
        print(json.dumps(results, indent=2))  # Print the results

        end_time = time.time()
        logging.info(f"Total execution time: {end_time - start_time:.2f} seconds")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
