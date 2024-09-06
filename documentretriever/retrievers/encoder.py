from cherche import retrieve
from sentence_transformers import SentenceTransformer
import faiss

class DocumentRetriever:
    def __init__(self, documents, model_name="sentence-transformers/all-mpnet-base-v2", device="cpu"):
        """
        Initialize the DocumentRetriever with a list of documents and a sentence transformer model.
        
        :param documents: List of documents where each document is a dictionary with an "id", "title", and "article".
        :param model_name: Name of the model from Sentence Transformers.
        :param device: Device to run the model on ("cpu" or "cuda").
        """
        self.documents = documents
        self.device = device
        self.model = SentenceTransformer(model_name, device=device)
        
        # Get the embedding dimension from the model
        embedding_dim = self.model.encode("Test sentence").shape[0]
        
        # Create a Faiss index for storing embeddings
        if device == "cuda":
            self.index = faiss.IndexFlatL2(embedding_dim)
            self.index = faiss.index_cpu_to_gpu(faiss.StandardGpuResources(), 0, self.index)
        else:
            self.index = faiss.IndexFlatL2(embedding_dim)
        
        # Initialize the retriever with the encoder and index
        self.retriever = retrieve.Encoder(
            key="id",
            on=["title", "article"],
            encoder=self.model.encode,
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

'''
# Example usage
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

# Instantiate the retriever
retriever = DocumentRetriever(documents, device="cpu")

# Retrieve documents similar to the query "paris"
results = retriever.retrieve("paris", k=3)
print(results)
'''
