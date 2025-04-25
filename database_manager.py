from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import Qdrant
from langchain_qdrant import QdrantVectorStore


class DatabaseManager:
    def __init__(self, model_name: str, device: str, encode_kwargs: dict, qdrant_url: str, collection_name: str):
        self.model_name = model_name
        self.device = device
        self.encode_kwargs = encode_kwargs
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name

        print(f"Initializing Ollama embeddings with model: {self.model_name}")
        self.embeddings = OllamaEmbeddings(model=self.model_name)

        # Check embedding dimensions
        embedding = self.embeddings.embed_documents(["test"])
        print(f"Embedding dimension: {len(embedding[0])}")
        if len(embedding[0]) != 4096:
            print(f"Warning: The embedding dimension is {len(embedding[0])}. Expected 4096.")

        # Connect to Qdrant
        print(f"Connecting to Qdrant at {self.qdrant_url}")
        self.client = QdrantClient(url=self.qdrant_url, prefer_grpc=False)

        # Ensure collection exists
        if not self._collection_exists():
            print(f"Collection '{self.collection_name}' not found. Creating a new collection...")
            self._create_collection()

        self.db = Qdrant(client=self.client, embeddings=self.embeddings, collection_name=self.collection_name)

    def add_documents(self, texts: list):
        """Add documents to the vector store."""
        if texts:
            print(f"Adding {len(texts)} text chunks to the vector store...")
            self.db.add_texts(texts)
        else:
            print("No texts provided to add to the vector store.")

    def _collection_exists(self) -> bool:
        """Check if the collection exists."""
        try:
            collections = self.client.get_collections().collections
            return any(collection.name == self.collection_name for collection in collections)
        except Exception as e:
            print(f"Error checking collection existence: {e}")
            return False

    def _create_collection(self):
        """Create the Qdrant collection."""
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=4096, distance="Cosine")
            )
            print(f"Created collection '{self.collection_name}'.")
        except Exception as e:
            print(f"Error creating collection: {e}")

    def get_db(self):
        return self.db
