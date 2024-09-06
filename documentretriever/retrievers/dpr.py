from cherche import retrieve
from sentence_transformers import SentenceTransformer
import faiss

class DPRRetriever:
    def __init__(self, documents, document_model="facebook-dpr-ctx_encoder-single-nq-base", query_model="facebook-dpr-question_encoder-single-nq-base", device="cpu"):
        """
        Initialize the DPRRetriever with a list of documents and DPR models for both documents and queries.
        
        :param documents: List of documents where each document is a dictionary with an "id", "title", and "article".
        :param document_model: Name of the document encoder model from Sentence Transformers.
        :param query_model: Name of the query encoder model from Sentence Transformers.
        :param device: Device to run the models on ("cpu" or "cuda").
        """
        self.documents = documents
        self.device = device
        
        # Load the document and query encoders
        self.document_encoder = SentenceTransformer(document_model, device=device)
        self.query_encoder = SentenceTransformer(query_model, device=device)
        
        # Get the embedding dimension from the document encoder
        embedding_dim = self.document_encoder.encode("Test document").shape[0]
        
        # Create a Faiss index for storing document embeddings
        if device == "cuda":
            self.index = faiss.IndexFlatL2(embedding_dim)
            self.index = faiss.index_cpu_to_gpu(faiss.StandardGpuResources(), 0, self.index)
        else:
            self.index = faiss.IndexFlatL2(embedding_dim)
        
        # Initialize the retriever with the encoders and index
        self.retriever = retrieve.DPR(
            encoder=self.document_encoder.encode,
            query_encoder=self.query_encoder.encode,
            key="id",
            on=["title", "article"],
            index=self.index,
            normalize=True
        )
        
        # Add documents to the retriever
        self.retriever = self.retriever.add(documents=documents)
    
    def retrieve(self, query, k=10):
        """
        Retrieve the top k documents that are most similar to the query.
        
        :param query: A string or list of strings representing the query/queries.
        :param k: Number of top documents to retrieve.
        :return: List of dictionaries with document IDs and their similarity scores.
        """
        results = self.retriever(query, k=k)
        return results

''' # Example usage
documents = [
    {
        "id": 0,
        "article": "Paris is the capital and most populous city of France",
        "title": "Paris",
        "url": "https://en.wikipedia.org/wiki/Paris"
    },
    {
        "id": 1,
        "article": "Paris has been one of Europe's major centres of finance, diplomacy, commerce, fashion, gastronomy, science, and arts.",
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

# Instantiate the DPR retriever
dpr_retriever = DPRRetriever(documents, device="cpu")

# Retrieve documents similar to the query "paris"
results = dpr_retriever.retrieve("paris", k=3)
print(results)
'''

