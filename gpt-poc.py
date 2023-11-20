import redis
import numpy as np
import sys
from redis.commands.search.query import Query

from openai_auth import get_token

# Constants
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = ""
INDEX_NAME = "paf-index"  # Ensure this matches the name used during index creation
VECTOR_FIELD = "embedding"  # The name of the vector field in Redis

def connect_to_redis():
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
    if redis_client.ping():
        return redis_client
    else:
        raise Exception('Unable to connect to Redis')

def get_embedding(text: str) -> np.ndarray:
    text = text.replace("\n", " ")
    _, _, embedding_model, openai = get_token()
    response = openai.Embedding.create(input=[text], engine=embedding_model)
    return np.array(response['data'][0]['embedding'], dtype=np.float32)

def search_redis(client: redis.Redis, input_embedding: np.ndarray, k: int = 5):
    # Convert the embedding to a byte string
    byte_embedding = input_embedding.tobytes()

    # Construct the query string for vector search
    # We'll use a simpler query format to ensure compatibility
    query = f"*=>[KNN {k} @{VECTOR_FIELD} $vec as score]"
    params = {"vec": byte_embedding}

    # Execute the search query
    try:
        results = client.ft(INDEX_NAME).search(query, query_params=params)
        return results.docs  # Returns a list of Document objects
    except Exception as e:
        print(f"Error during Redis search: {e}")
        return []



def gpt_call(openai, gpt_model, deployment_id, results, question):
    # Format the results for the GPT prompt
    formatted_results = "\n".join([f"{idx + 1}. {doc.text}" for idx, doc in enumerate(results)])

    prompt = f"The below content gives information about an XML framework named PAF. Use that information to create the PAF code for the user query. Only return the PAF code.\n{formatted_results}"

    response = openai.ChatCompletion.create(
        deployment_id=deployment_id,
        model=gpt_model,
        temperature=0,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ],
    )

    return response

def main(question):
    deployment_id, gpt_model, embedding_model, openai = get_token()
    input_embedding = get_embedding(question)

    redis_client = connect_to_redis()
    search_results = search_redis(redis_client, input_embedding)

    formatted_response = gpt_call(openai, gpt_model, deployment_id, search_results, question)
    print(formatted_response.choices)
    return formatted_response

if __name__ == '__main__':
    sys.exit(main("click xpath='//button[@id='continue']'"))
