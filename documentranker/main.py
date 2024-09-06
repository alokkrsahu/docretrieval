# main.py
import sys
import ast
import json
import numpy as np
from ranker import DocumentRanker

def convert_to_serializable(obj):
    """Convert numpy types to standard Python types."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(i) for i in obj]
    else:
        return obj

def get_results(method, queries, results):
    # Ensure results and queries match in length
    assert len(queries) == len(results), "Mismatch between queries and results length"

    output = []
    for query, result in zip(queries, results):
        result_entry = {
            "query": query,
            "results": [{"id": doc['id'], "similarity": convert_to_serializable(doc['similarity'])} for doc in result]
        }
        output.append(result_entry)
    
    return json.dumps({"method": method, "data": output}, indent=2)

def main():
    if len(sys.argv) < 5:
        print("Usage: python main.py <method> <queries> <documents> <key> <on>")
        sys.exit(1)

    method = sys.argv[1]
    queries_str = sys.argv[2]
    documents_str = sys.argv[3]
    key = sys.argv[4]
    on_str = sys.argv[5]

    # Convert JSON strings to Python objects
    try:
        queries = json.loads(queries_str)
        documents = json.loads(documents_str)
        on = ast.literal_eval(on_str)
        if not isinstance(on, list):
            raise ValueError("The 'on' argument should be a list.")
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing arguments: {e}")
        sys.exit(1)

    ranker = DocumentRanker(documents, key=key, on=on)

    if method == "encoder":
        results = ranker.rank_encoder(queries)
    elif method == "dpr":
        results = ranker.rank_dpr(queries)
    elif method == "cross_encoder":
        results = ranker.rank_cross_encoder(queries)
    elif method == "embedding":
        results = ranker.rank_embedding(queries)
    else:
        print(f"Unknown method: {method}")
        sys.exit(1)

    # Output results as JSON
    print(get_results(method, queries, results))

if __name__ == "__main__":
    main()
