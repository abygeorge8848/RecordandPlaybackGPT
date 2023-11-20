import os
from dotenv import load_dotenv
load_dotenv(override=True)

# openai
import openai

def get_token():

    running_as = os.getenv('RUNNING_AS')

    if running_as == 'IQVIA':
        # Azure
        from azure.identity import DefaultAzureCredential
        deployment_id = os.getenv('DEPLOYMENT_ID')
        gpt_model = os.getenv('GPT_MODEL')
        embedding_model = os.getenv('EMBEDDING_MODEL')
        ad_programmatic_scope = os.getenv('AD_PROGRAMMATIC_SCOPE')
        openai.api_type = os.getenv('OPENAI_API_TYPE')
        openai.api_base = os.getenv('OPENAI_API_BASE')
        openai.api_version = os.getenv('OPENAI_API_VERSION')
        credentials = DefaultAzureCredential()
        token = credentials.get_token(ad_programmatic_scope)
        openai.api_key = token.token
        return deployment_id, gpt_model, embedding_model, openai
    else:
        openai.api_key = os.getenv('OPENAI_API_KEY')
        gpt_model = os.getenv('GPT_MODEL')
        embedding_model = os.getenv('EMBEDDING_MODEL')
        deployment_id = None
        return deployment_id, gpt_model, embedding_model, openai

