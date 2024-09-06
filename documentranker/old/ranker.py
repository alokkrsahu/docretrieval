# ranker.py

from cherche import retrieve, rank
from sentence_transformers import SentenceTransformer, CrossEncoder

class DocumentRanker:
    def __init__(self, documents):
        self.documents = documents
        self.retriever = retrieve.TfIdf(key="id", on=["title", "article"], documents=documents)
        self.encoder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
        self.dpr_encoder = SentenceTransformer('facebook-dpr-ctx_encoder-single-nq-base')
        self.dpr_query_encoder = SentenceTransformer('facebook-dpr-question_encoder-single-nq-base')
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def rank_encoder(self, queries, k=30):
        ranker = rank.Encoder(
            key="id",
            on=["title", "article"],
            encoder=self.encoder.encode,
            normalize=True,
        )
        ranker.add(self.documents, batch_size=64)
        matches = self.retriever(queries, k=100)
        return ranker(queries, documents=matches, k=k)

    def rank_dpr(self, queries, k=30):
        ranker = rank.DPR(
            key="id",
            on=["title", "article"],
            encoder=self.dpr_encoder.encode,
            query_encoder=self.dpr_query_encoder.encode,
            normalize=True,
        )
        ranker.add(self.documents, batch_size=64)
        matches = self.retriever(queries, k=100)
        return ranker(queries, documents=matches, k=k)

    def rank_cross_encoder(self, queries, k=30):
        self.retriever += self.documents
        ranker = rank.CrossEncoder(
            on=["title", "article"],
            encoder=self.cross_encoder.predict,
        )
        matches = self.retriever(queries, k=100)
        return ranker(queries, documents=matches, k=k)

    def rank_embedding(self, queries, k=30):
        embeddings_documents = self.encoder.encode([doc["article"] for doc in self.documents])
        embeddings_queries = self.encoder.encode(queries)
        ranker = rank.Embedding(
            key="id",
            normalize=True,
        )
        ranker.add(documents=self.documents, embeddings_documents=embeddings_documents)
        matches = self.retriever(queries, k=100)
        return ranker(q=embeddings_queries, documents=matches, k=k)
