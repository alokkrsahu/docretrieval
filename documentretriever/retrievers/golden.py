from cherche import retrieve
from sentence_transformers import SentenceTransformer
import faiss
from rapidfuzz import fuzz
from lenlp import sparse

class DocumentRetriever:
    def __init__(self, method, documents, on, key="id", use_gpu=False, **kwargs):
        self.method = method.lower()
        self.documents = documents
        self.key = key
        self.on = on
        self.use_gpu = use_gpu
        self.kwargs = kwargs
        self.retriever = None
        self.encoder_model = None  # Ensuring it's defined for encoder methods
        self.query_encoder = None  # Ensuring it's defined for DPR method

        if self.method == "bm25":
            self.retriever = self._init_bm25()
        elif self.method == "tfidf":
            self.retriever = self._init_tfidf()
        elif self.method == "flash":
            self.retriever = self._init_flash()
        elif self.method == "lunr":
            self.retriever = self._init_lunr()
        elif self.method == "fuzz":
            self.retriever = self._init_fuzz()
        elif self.method == "embedding":
            self.retriever = self._init_embedding()

    def _filter_kwargs(self, valid_params):
        return {k: v for k, v in self.kwargs.items() if k in valid_params}

    def _init_bm25(self):
        valid_params = ['k']
        filtered_kwargs = self._filter_kwargs(valid_params)
        return retrieve.BM25(key=self.key, on=self.on, documents=self.documents, **filtered_kwargs)

    def _init_tfidf(self):
        valid_params = ['vectorizer_params']
        filtered_kwargs = self._filter_kwargs(valid_params)
        count_vectorizer = sparse.TfidfVectorizer(**filtered_kwargs.get("vectorizer_params", {}))
        return retrieve.TfIdf(key=self.key, on=self.on, documents=self.documents, tfidf=count_vectorizer)

    def _init_flash(self):
        retriever = retrieve.Flash(key=self.key, on=self.on)
        retriever.add(self.documents)
        return retriever

    def _init_lunr(self):
        return retrieve.Lunr(key=self.key, on=self.on, documents=self.documents)

    def _init_fuzz(self):
        valid_params = ['fuzzer']
        filtered_kwargs = self._filter_kwargs(valid_params)
        fuzzer = filtered_kwargs.get("fuzzer", fuzz.partial_ratio)
        retriever = retrieve.Fuzz(key=self.key, on=self.on, fuzzer=fuzzer)
        retriever.add(self.documents)
        return retriever
    '''
# List of available scoring function
>>> scoring = [
...     fuzz.ratio,
...     fuzz.partial_ratio,
...     fuzz.token_set_ratio,
...     fuzz.partial_token_set_ratio,
...     fuzz.token_sort_ratio,
...     fuzz.partial_token_sort_ratio,
...     fuzz.token_ratio,
...     fuzz.partial_token_ratio,
...     fuzz.WRatio,
...     fuzz.QRatio,
... ]

    '''



    def _init_embedding(self):
        valid_params = ['model_name']
        filtered_kwargs = self._filter_kwargs(valid_params)
        model_name = filtered_kwargs.get("model_name", "sentence-transformers/all-mpnet-base-v2")
        self.encoder_model = SentenceTransformer(model_name, device="cuda" if self.use_gpu else "cpu")
        encoder = self.encoder_model.encode

        def wrapped_encoder(texts):
            if isinstance(texts, str):
                texts = [texts]
            return encoder(texts)
        d = wrapped_encoder(["This is a sample document."])[0].shape[0] # Leave it here to calculate the embedding size.
        index = faiss.IndexFlatL2(d)
        if self.use_gpu:
            index = faiss.index_cpu_to_gpu(faiss.StandardGpuResources(), 0, index)

        retriever = retrieve.Embedding(key=self.key, index=index)
        embeddings_documents = wrapped_encoder([doc["text"] for doc in self.documents])
        retriever.add(documents=self.documents, embeddings_documents=embeddings_documents)
        return retriever

    def retrieve(self, query, k=10, batch_size=64):
        if isinstance(query, str):
            query = [query]

        if self.method in ["encoder", "embedding"]:
            query_embeddings = self.encoder_model.encode(query)
            return self.retriever(q=query_embeddings, k=k)
        elif self.method == "dpr":
            query_embeddings = self.query_encoder(query)
            return self.retriever(q=query_embeddings, k=k)
        elif self.method == "flash":
            return self.retriever(query)
        else:
            return self.retriever(query, k=k)


'''
# Example Usage
documents = [
    {"id": 0, "content": "Paris is the capital and most populous city of France"},
    {"id": 1, "content": "Paris has been one of Europe major centres of finance, diplomacy , commerce , fashion , gastronomy , science , and arts."},
    {"id": 2, "content": "The City of Paris is the centre and seat of government of the region and province of Île-de-France ."}
]

methods = ["bm25","tfidf","flash","lunr","fuzz","embedding"]

for each in methods:
    print(each)
    try:
        retriever = DocumentRetriever(
            method=each,
            documents=documents,
            on=["content"],
            use_gpu=False,
            model_name="sentence-transformers/all-mpnet-base-v2"
        )

        results = retriever.retrieve("fashion", k=2)
        print(results)
    except Exception as e:
        print("ERROR")
        print(e)
        continue
'''
