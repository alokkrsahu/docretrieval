# documentretriever/retrievers/main.py

import json
import logging
from typing import List, Dict, Any

# Import specific retriever implementations
from .encoder import DocumentRetriever as EncoderDocumentRetriever
from .dpr import DPRRetriever
from .golden import DocumentRetriever as GoldenDocumentRetriever

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_documents(file_path: str) -> List[Dict[str, Any]]:
    """Load documents from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading documents from {file_path}: {e}")
        raise

def retrieve_golden(documents: List[Dict[str, Any]], query: str, method: str, k: int) -> List[Dict[str, Any]]:
    """Retrieve documents using the Golden retriever with specified method."""
    try:
        retriever = GoldenDocumentRetriever(
            method=method,
            documents=documents,
            on=["text"],  # Adjust this based on your document structure
            use_gpu=False  # Set to True if you want to use GPU
        )
        results = retriever.retrieve(query, k=k)
        return results
    except Exception as e:
        logging.error(f"Error in Golden retrieval with method {method}: {e}")
        raise

def retrieve(processed_docs_path: str, query: str, method: str, k: int) -> List[Dict[str, Any]]:
    """
    Main function to perform document retrieval.
    
    Args:
    processed_docs_path (str): Path to the processed documents JSON file.
    query (str): The query string for retrieval.
    method (str): The retrieval method to use (e.g., "bm25", "dpr", "encoder", "tfidf", "flash", "lunr", "fuzz", "embedding").
    k (int): The number of top results to retrieve.
    
    Returns:
    list: A list of retrieved documents.
    """
    logging.info(f"Retrieving documents for query: {query}")
    logging.info(f"Using method: {method}")
    logging.info(f"Number of results: {k}")
    logging.info(f"Processed docs path: {processed_docs_path}")

    try:
        documents = load_documents(processed_docs_path)
        
        if method in ["bm25", "tfidf", "flash", "lunr", "fuzz", "embedding"]:
            return retrieve_golden(documents, query, method, k)
        elif method == "encoder":
            encoder_retriever = EncoderDocumentRetriever(documents)
            return encoder_retriever.retrieve(query, k=k)
        elif method == "dpr":
            dpr_retriever = DPRRetriever(documents)
            return dpr_retriever.retrieve(query, k=k)
        else:
            raise ValueError(f"Unsupported retrieval method: {method}")

    except Exception as e:
        logging.error(f"Error in document retrieval: {e}")
        return []

if __name__ == "__main__":
    # This block is for testing purposes
    import sys
    if len(sys.argv) != 5:
        print("Usage: python main.py <processed_docs_path> <query> <method> <k>")
        sys.exit(1)
    
    docs_path, query, method, k = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    results = retrieve(docs_path, query, method, k)
    print(json.dumps(results, indent=2))
