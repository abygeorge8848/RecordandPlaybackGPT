from typing import Tuple
import fitz  # PyMuPDF
import json
import redis
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
import numpy as np
import openai  # Make sure to install openai Python client and set up your API key

from openai_auth import get_token

# Constants
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = ""
INDEX_NAME = "paf-index"
PREFIX = "paf"
VECTOR_DIM = 768  # Assuming the dimension of embeddings
DISTANCE_METRIC = "COSINE"

def extract_text(pdf_path: str) -> str:
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def get_embedding(text: str) -> np.ndarray:
    text = text.replace("\n", " ")
    deployment_id, gpt_model, embedding_model, openai = get_token()
    response = openai.Embedding.create(input=[text], engine=embedding_model)
    return np.array(response['data'][0]['embedding'], dtype=np.float32)

def embed_data(pdf_path: str) -> Tuple[str, np.ndarray]:
    text = extract_text(pdf_path)
    embedding = get_embedding(text)
    return text, embedding

def main():
    pdf_path = "./PAF_User_Manual.pdf"
    text, embedding = embed_data(pdf_path)

    # Connect to Redis
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

    # Ensure connection is successful
    if not client.ping():
        print('Failed to connect to Redis')
        return

    # Create Redis Search Index
    try:
        client.ft(INDEX_NAME).info()
    except redis.exceptions.ResponseError:
        fields = [TextField("text"), VectorField("embedding", type="FLOAT32", dim=VECTOR_DIM, metric=DISTANCE_METRIC)]
        client.ft(INDEX_NAME).create_index(fields, definition=IndexDefinition(prefix=[PREFIX], index_type=IndexType.HASH))

    # Index document
    doc_id = f"{PREFIX}:1"
    client.hset(doc_id, mapping={'text': text, 'embedding': embedding.tobytes()})

    print(f"Document indexed with ID: {doc_id}")

if __name__ == '__main__':
    main()
