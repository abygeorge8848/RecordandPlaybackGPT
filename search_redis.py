import numpy as np
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

from openai_auth import get_token

REDIS_HOST =  "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = "" # default for passwordless Redis



def connect_to_redis():
        # Connect to Redis
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD
    )
    if redis_client.ping():
        return redis_client
    else:
        raise Exception('Unable to connect to Redis')


def search_redis(
    redis_client: redis.Redis,
    embedded_query: object,
    index_name: str,
    vector_field: str,
    return_fields: list,
    hybrid_fields = "*",
    k: int = 10,
    pprint = True,
): 

    # Prepare the Query
    base_query = f'{hybrid_fields}=>[KNN {k} @{vector_field} $vector AS vector_score]'
    query = (
        Query(base_query)
         .return_fields(*return_fields)
         .sort_by("vector_score")
         .paging(0, k)
         .dialect(2)
    )
    params_dict = {"vector": np.array(embedded_query).astype(dtype=np.float32).tobytes()}

    # perform vector search
    results = redis_client.ft(index_name).search(query, params_dict)
    if pprint: 
        for i, article in enumerate(results.docs):
            score = 1 - float(article.vector_score)
    return results.docs



def search(question):

    deployment_id, gpt_model, embedding_model, openai = get_token()
    response = openai.Embedding.create(input=question, engine = embedding_model)
    embedded_query = response["data"][0]['embedding']

    redis_client = connect_to_redis()

    index_name = "paf-dict-index"
    vector_field = "content_vector"
    return_fields = ["content", "vector_score"]

    results = search_redis(redis_client, embedded_query, index_name, vector_field, return_fields, k=5, pprint=False)

    if results is not None:
        return results
    else:
        print("No search results from redis")
        return