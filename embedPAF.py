from typing import List, Iterator
import pandas as pd
import numpy as np
import sys

from openai_auth import get_token

# Redis client library for Python
import redis
from redis.commands.search.indexDefinition import (
    IndexDefinition,
    IndexType
)
from redis.commands.search.query import Query
from redis.commands.search.field import (
    TextField,
    VectorField
)

# Constants
REDIS_HOST =  "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = "" # default for passwordless Redis

# Ignore unclosed SSL socket warnings - optional in case you get these errors
import warnings
warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning) 

def main(index, csv_path):

    df = embed_data(csv_path)
    df.info(show_counts=True)
    print(df.keys())
    print (df.head())

    # Connect to Redis
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD
    )

    if redis_client.ping():
        print('Successfully connected to Redis')

        df['vector_id'] = df['vector_id'].apply(str)

        VECTOR_DIM = len(df['content_vector'][1]) 
        VECTOR_NUMBER = len(df)               
        INDEX_NAME = f"{index}-index"           
        PREFIX = index                     
        DISTANCE_METRIC = "COSINE"            

        # Define RediSearch fields for each of the columns in the dataset
        content = TextField(name="content")
        content_embedding = VectorField("content_vector",
            "FLAT", {
                "TYPE": "FLOAT32",
                "DIM": VECTOR_DIM,
                "DISTANCE_METRIC": DISTANCE_METRIC,
                "INITIAL_CAP": VECTOR_NUMBER,
            }
        )
        fields = [content, content_embedding]

        # Check if index exists
        try:
            redis_client.ft(INDEX_NAME).info()
            print("Index already exists")
        except:
            # Create RediSearch Index
            redis_client.ft(INDEX_NAME).create_index(
                fields = fields,
                definition = IndexDefinition(prefix=[PREFIX], index_type=IndexType.HASH)
            )

        index_documents(redis_client, PREFIX, df)
        print(f"Loaded {redis_client.info()['db0']['keys']} documents in Redis search index with name: {INDEX_NAME}")


def get_embedding(text):
    print(f'Generating embedding for {text}')
    text = text.replace("\n", " ")
    deployment_id, gpt_model, embedding_model, openai = get_token()
    return openai.Embedding.create(input = [text], engine=embedding_model)['data'][0]['embedding']


def embed_data(csv_path):
    tdf = pd.read_csv(csv_path)
    
    tdf['content'] = "{" + tdf.apply(lambda row: ', '.join([f'"{col}": "{val}"' for col, val in row.items()]), axis=1) + "}"

    # This is the call to openai
    tdf['content_vector'] = tdf.content.apply(lambda x: get_embedding(x))

    # Just get the relevant columns
    df = tdf[['content','content_vector']]
    df.insert(0, 'vector_id', range(1, len(df) + 1))

    return df


def index_documents(client: redis.Redis, prefix: str, documents: pd.DataFrame):
    records = documents.to_dict("records")
    for doc in records:
        key = f"{prefix}:{str(doc['vector_id'])}"

        # create byte vectors for title and content
        content_embedding = np.array(doc["content_vector"], dtype=np.float32).tobytes()

        # replace list of floats with byte vectors
        doc["content_vector"] = content_embedding

        client.hset(key, mapping = doc)


def pandas_series_to_list(x):
    return x.to_list()





if __name__ == '__main__':
    sys.exit(main("roche-irt", "./documents/csv/Roche IRT questions_Final_Sep2023.csv"))