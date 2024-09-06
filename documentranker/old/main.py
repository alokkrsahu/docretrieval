# main.py

import sys
from ranker import DocumentRanker

def main():
    if len(sys.argv) < 2:
        print("Usage: main.py <method> [<query>...]")
        sys.exit(1)

    method = sys.argv[1].lower()
    queries = sys.argv[2:]

    documents = [
        {
            "id": 0,
            "article": "Paris is the capital and most populous city of France",
            "title": "Paris",
            "url": "https://en.wikipedia.org/wiki/Paris"
        },
        {
            "id": 1,
            "article": "Paris has been one of Europe major centres of finance, diplomacy, commerce, fashion, gastronomy, science, and arts.",
            "title": "Paris",
            "url": "https://en.wikipedia.org/wiki/Paris"
        },
        {
            "id": 2,
            "article": "The City of Paris is the centre and seat of government of the region and province of Île-de-France.",
            "title": "Paris",
            "url": "https://en.wikipedia.org/wiki/Paris"
        }
    ]

    ranker = DocumentRanker(documents)

    if method == "encoder":
        results = ranker.rank_encoder(queries)
    elif method == "dpr":
        results = ranker.rank_dpr(queries)
    elif method == "cross_encoder":
        results = ranker.rank_cross_encoder(queries)
    elif method == "embedding":
        results = ranker.rank_embedding(queries)
    else:
        print("Invalid method. Choose from 'encoder', 'dpr', 'cross_encoder', or 'embedding'.")
        sys.exit(1)

    for query_result in results:
        for result in query_result:
            print(f"ID: {result['id']}, Similarity: {result['similarity']}")

if __name__ == "__main__":
    main()
