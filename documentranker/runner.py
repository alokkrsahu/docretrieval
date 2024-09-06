# runner.py
import subprocess, sys
import json

def run_main(method, queries, documents, key, on):
    # Convert lists and dicts to JSON strings for command-line arguments
    queries_str = json.dumps(queries)
    documents_str = json.dumps(documents)
    on_str = json.dumps(on)  # This is a list, so no need for special formatting

    # Construct the command
    command = [
        "python", "main.py",
        method,
        queries_str,
        documents_str,
        key,
        on_str
    ]

    # Call main.py
    result = subprocess.run(command, capture_output=True, text=True)
    
    # Print the output from main.py
    if result.stdout:
        try:
            output = json.loads(result.stdout)
            method = output.get("method")
            data = output.get("data", [])

            for entry in data:
                print(f"Results for {method} query: {entry['query']}")
                for doc in entry['results']:
                    print(f"ID: {doc['id']}, Similarity: {doc['similarity']}")
                print("-" * 40)  # Separator between results for different queries
        except json.JSONDecodeError:
            print("Failed to parse JSON output from main.py")
    if result.stderr:
        print(result.stderr, file=sys.stderr)

if __name__ == "__main__":
    # Example usage
    method = "encoder"  # or "dpr", "cross_encoder", "embedding"
    queries = ["paris", "art", "fashion"]
    documents = [
        {"id": 0, "article": "Paris is the capital and most populous city of France", "title": "Paris", "url": "https://en.wikipedia.org/wiki/Paris"},
        {"id": 1, "article": "Paris has been one of Europe major centres of finance, diplomacy, commerce, fashion, gastronomy, science, and arts.", "title": "Paris", "url": "https://en.wikipedia.org/wiki/Paris"},
        {"id": 2, "article": "The City of Paris is the centre and seat of government of the region and province of Île-de-France.", "title": "Paris", "url": "https://en.wikipedia.org/wiki/Paris"}
    ]
    key = "id"
    on = ["title", "article"]

    run_main(method, queries, documents, key, on)
