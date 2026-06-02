import os
from uuid import uuid4
from functools import lru_cache
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from pinecone.errors.exceptions import PineconeException
from sentence_transformers import SentenceTransformer

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "jaz-memory")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
HF_EMBEDDING_MODEL = os.getenv(
    "HF_EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)
HF_TOKEN = os.getenv("HF_TOKEN")

EMBEDDING_DIMENSION = 384

@lru_cache(maxsize=1)
def get_embedding_model():
    kwargs = {}
    if HF_TOKEN:
        kwargs["token"] = HF_TOKEN

    return SentenceTransformer(HF_EMBEDDING_MODEL, **kwargs)


@lru_cache(maxsize=1)
def get_pinecone_client():
    if not PINECONE_API_KEY:
        raise RuntimeError("PINECONE_API_KEY is not set. Add it to jaz-backend/.env.")

    return Pinecone(api_key=PINECONE_API_KEY)


@lru_cache(maxsize=1)
def get_index():
    pc = get_pinecone_client()
    existing_indexes = [index["name"] for index in pc.list_indexes()]

    if PINECONE_INDEX_NAME not in existing_indexes:
        try:
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=PINECONE_CLOUD,
                    region=PINECONE_REGION
                )
            )
        except PineconeException as exc:
            raise RuntimeError(
                f"Pinecone index '{PINECONE_INDEX_NAME}' does not exist and could "
                "not be created. Set PINECONE_INDEX_NAME to an existing index, "
                "delete an unused Pinecone index, or upgrade the Pinecone plan."
            ) from exc

    return pc.Index(PINECONE_INDEX_NAME)


def embed_text(text: str):
    return get_embedding_model().encode(text).tolist()


def save_child_memory(
    child_id: int,
    text: str,
    memory_type: str = "learning",
    metadata: dict | None = None
):
    vector = embed_text(text)

    record_id = f"child-{child_id}-{uuid4()}"

    payload = {
        "child_id": child_id,
        "text": text,
        "memory_type": memory_type,
        **(metadata or {})
    }

    try:
        get_index().upsert(
            vectors=[
                {
                    "id": record_id,
                    "values": vector,
                    "metadata": payload
                }
            ],
            namespace=f"child-{child_id}"
        )
    except PineconeException as exc:
        raise RuntimeError("Could not save child memory to Pinecone.") from exc

    return record_id


def search_child_memory(child_id: int, query: str, top_k: int = 5):
    vector = embed_text(query)

    try:
        results = get_index().query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            namespace=f"child-{child_id}"
        )
    except PineconeException as exc:
        raise RuntimeError("Could not search child memory in Pinecone.") from exc

    return [
        {
            "score": match["score"],
            "text": match["metadata"].get("text"),
            "memory_type": match["metadata"].get("memory_type")
        }
        for match in results["matches"]
    ]
