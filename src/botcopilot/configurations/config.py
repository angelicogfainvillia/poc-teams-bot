import os
from dotenv import load_dotenv


def read_prompt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "Default prompt not found."


""" Bot Configuration """
load_dotenv()


class DefaultConfig:
    """Bot Configuration"""

    HOST = os.environ.get("APP_HOST", "localhost")
    PORT = int(os.environ.get("APP_PORT", 3978))
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_TYPE = os.environ.get("MicrosoftAppType", "")
    APP_TENANT_ID = os.environ.get("MicrosoftAppTenantId", "")

    # Azure OpenAI configuration
    AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_DEPLOYMENT_ID = os.environ.get("AZURE_OPENAI_DEPLOYMENT_ID", "")

    # Azure Storage Account configuration
    AZURE_STORAGE_ACCOUNT_NAME = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME", "")
    AZURE_STORAGE_ACCOUNT_KEY = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY", "")
    AZURE_SA_ARTIFACTS_PATH = "artifacts"  # Base path for artifacts in Azure Storage
    AZURE_SA_VECTOR_STORE_PATH_TEMPLATE = (
        "{aad_object_id}/text-embedding-ada-002/vectordb"
    )
    VECTOR_STORE_INDEX_NAMES = os.environ.get("VECTOR_STORE_INDEX_NAMES", "").split(",")

    AZURE_SA_EMBEDDINGS_PATH_TEMPLATE = (
        "{aad_object_id}/text-embedding-ada-002/embeddings"
    )

    # Microsoft Graph API
    GRAPH_API_CLIENT_ID = os.getenv("GRAPH_API_CLIENT_ID")
    GRAPH_API_CLIENT_SECRET = os.getenv("GRAPH_API_CLIENT_SECRET")
    GRAPH_API_TENANT_ID = os.getenv("GRAPH_API_TENANT_ID")

    # Directory paths
    DATA_FOLDER_PATH = "./data"  # Local data folder
    LOCAL_ARTIFACTS_BASE_FOLDER_PATH = (
        "./artifacts"  # "./src/artifacts"  # Local artifacts base folder
    )
    LOCAL_VECTOR_STORE_FOLDER_PATH_TEMPLATE = "./artifacts/{aad_object_id}/text-embedding-ada-002/vectordb"  # local: "./src/artifacts/{aad_object_id}/text-embedding-ada-002/vectordb"
    LOCAL_EMBEDDINGS_FOLDER_PATH_TEMPLATE = "./artifacts/{aad_object_id}/text-embedding-ada-002/embeddings"  # local: "./src/artifacts/{aad_object_id}/text-embedding-ada-002/embeddings"
    PROMPTS_FOLDER_PATH = "./prompts"  # IF local ./src/prompts

    # TEST Variables
    SYSTEM_PROMPT = read_prompt(f"{PROMPTS_FOLDER_PATH}/system_prompt")
    WELCOME_TEXT = read_prompt(f"{PROMPTS_FOLDER_PATH}/welcome_message")
    BOT_PARAMS = {
        "system_prompt": SYSTEM_PROMPT,
        "welcome_text": WELCOME_TEXT,
        "limit_context_window_max_tokens": 40000,
        "model_params": {
            "model": os.environ.get("AZURE_OPENAI_DEPLOYMENT_ID"),
            "max_tokens": 700,
            "temperature": 0.7,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None,
        },
    }
