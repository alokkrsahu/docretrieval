from documentretriever.retrievers.main import retrieve
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main(args):
    """Main function to handle the document retrieval."""
    try:
        results = retrieve(args['processed_docs_path'], args['query'], args['method'], args['k'])
        return results
    except Exception as e:
        logging.error(f"Error in document retrieval: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the document retrieval.")
    parser.add_argument("processed_docs_path", help="Path to the processed documents JSON file.")
    parser.add_argument("query", help="Query for document retrieval.")
    parser.add_argument("method", choices=["bm25", "dpr", "encoder"], help="Retrieval method.")
    parser.add_argument("k", type=int, help="Number of results to retrieve.")
    args = parser.parse_args()
    main(vars(args))
