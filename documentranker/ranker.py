# ranker.py
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, message="`clean_up_tokenization_spaces` was not set")

from cherche import retrieve, rank
from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np

class DocumentRanker:
    def __init__(self, documents, key="id", on=["title", "article"]):
        self.documents = documents
        self.key = key
        self.on = on
        self.retriever = retrieve.TfIdf(key=self.key, on=self.on, documents=documents)
        self.encoder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
        self.dpr_encoder = SentenceTransformer('facebook-dpr-ctx_encoder-single-nq-base')
        self.dpr_query_encoder = SentenceTransformer('facebook-dpr-question_encoder-single-nq-base')
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def rank_encoder(self, queries):
        embeddings_documents = self.encoder.encode([doc["article"] for doc in self.documents])
        embeddings_queries = self.encoder.encode(queries)
        self.retriever += self.documents
        ranker = rank.Embedding(key=self.key, normalize=True)
        ranker = ranker.add(documents=self.documents, embeddings_documents=embeddings_documents)
        match = self.retriever(queries, k=100)
        results = ranker(q=embeddings_queries, documents=match, k=30)
        return results

    def rank_dpr(self, queries):
        ranker = rank.DPR(
            key=self.key,
            on=self.on,
            encoder=self.dpr_encoder.encode,
            query_encoder=self.dpr_query_encoder.encode,
            normalize=True
        )
        ranker.add(self.documents, batch_size=64)
        match = self.retriever(queries, k=100)
        results = ranker(queries, documents=match, k=30)
        return results

    def rank_cross_encoder(self, queries):
        self.retriever += self.documents
        ranker = rank.CrossEncoder(
            on=self.on,
            encoder=self.cross_encoder.predict
        )
        match = self.retriever(queries, k=100)
        results = ranker(queries, documents=match, k=30)
        return results

    def rank_embedding(self, queries):
        embeddings_documents = self.encoder.encode([doc["article"] for doc in self.documents])
        embeddings_queries = self.encoder.encode(queries)
        ranker = rank.Embedding(key=self.key, normalize=True)
        ranker = ranker.add(documents=self.documents, embeddings_documents=embeddings_documents)
        match = self.retriever(queries, k=100)
        results = ranker(q=embeddings_queries, documents=match, k=30)
        return results
