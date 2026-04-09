import chromadb
from sentence_transformers import SentenceTransformer
import uuid



class VectorStore:

    def __init__(self):
        self.client = chromadb.PersistentClient(
    path="./chroma_db")
        self.collection = self.client.get_or_create_collection(
            name="decisions"
        )

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def store(self, text, metadata):
        embedding = self.embedding_model.encode(text).tolist()

        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata],
            ids=[str(uuid.uuid4())]
        )

    def search(self, query):
        embedding = self.embedding_model.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=3
        )

        return results