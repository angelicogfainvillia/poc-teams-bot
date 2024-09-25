import os
from tqdm import tqdm
from openai import AzureOpenAI
from langchain_community.vectorstores import FAISS
from botcopilot.clients.storage_account import StorageAccountClient
from botcopilot.configurations.config import DefaultConfig as config


class CustomEmbeddings:
    def __init__(self, azure_client, deployment_id, precomputed_embeddings=None):
        self.azure_client = azure_client
        self.deployment_id = deployment_id
        self.precomputed_embeddings = (
            precomputed_embeddings if precomputed_embeddings is not None else {}
        )

    def clear_embeddings(self):
        """Clear all precomputed embeddings to prevent data leakage between datasets."""
        self.precomputed_embeddings.clear()

    def set_precomputed_embeddings(self, embeddings):
        """Update precomputed embeddings with a new set, ensuring they are in the correct format."""
        if isinstance(embeddings, dict):
            self.precomputed_embeddings.update(embeddings)
        else:
            raise ValueError(
                "Embeddings must be provided as a dictionary mapping texts to vector embeddings."
            )

    def embed_query(self, text):
        """Generate an embedding for a single piece of text, using precomputed embeddings if available."""
        if not text:
            raise ValueError("Input text must be a non-empty string.")
        if text in self.precomputed_embeddings:
            return self.precomputed_embeddings[text]
        return self.fetch_embedding_from_azure(text)

    def fetch_embedding_from_azure(self, text):
        """Fetch embedding from Azure OpenAI API."""
        try:
            response = self.azure_client.embeddings.create(
                model=self.deployment_id, input=text
            )
            embedding = response.data[0].embedding
            self.precomputed_embeddings[text] = (
                embedding  # Optionally cache this embedding
            )
            return embedding
        except Exception as e:
            raise ConnectionError(f"Failed to fetch embedding from Azure: {str(e)}")

    def embed_documents(self, texts):
        """Generate embeddings for a list of documents."""
        return [
            self.embed_query(text) for text in tqdm(texts, desc="Embedding documents")
        ]

    def __call__(self, text):
        """Allow the embeddings object to be callable."""
        return self.embed_query(text)


class AzureVectorStoreRetriever:
    def __init__(
        self, azure_api_key, azure_endpoint, azure_openai_deployment_id, aad_object_id
    ):
        self.azure_client = AzureOpenAI(
            api_key=azure_api_key,
            api_version="2024-02-15-preview",
            base_url=f"{azure_endpoint}/openai/deployments/{azure_openai_deployment_id}/",
        )
        self.storage_client = StorageAccountClient(
            account_name=config.AZURE_STORAGE_ACCOUNT_NAME,
            account_key=config.AZURE_STORAGE_ACCOUNT_KEY,
        )
        self.azure_sa_container_path = config.AZURE_SA_ARTIFACTS_PATH
        self.deployment_id = azure_openai_deployment_id
        self.aad_object_id = aad_object_id
        self.azure_sa_vector_store_path = (
            config.AZURE_SA_VECTOR_STORE_PATH_TEMPLATE.format(
                aad_object_id=aad_object_id
            )
        )
        self.azure_sa_embeddings_path = config.AZURE_SA_EMBEDDINGS_PATH_TEMPLATE.format(
            aad_object_id=aad_object_id
        )
        self.local_vector_store_folder_path = (
            config.LOCAL_VECTOR_STORE_FOLDER_PATH_TEMPLATE.format(
                aad_object_id=aad_object_id
            )
        )
        self.local_embeddings_folder_path = (
            config.LOCAL_EMBEDDINGS_FOLDER_PATH_TEMPLATE.format(
                aad_object_id=aad_object_id
            )
        )

        self.embeddings = CustomEmbeddings(self.azure_client, self.deployment_id)
        self.indexes = self.initialize_indexes()

    def initialize_indexes(self):
        """
        Initialize indexes by checking if local vector store exists. If not, download from Azure.

        Returns:
            dict: A dictionary of index names and their corresponding FAISS index.
        """

        # those are the index names - you need to get the most recent ones for production version
        indexes_names = config.VECTOR_STORE_INDEX_NAMES

        indexes = {}
        for index_name in indexes_names:
            local_vector_store_path = os.path.join(
                self.local_vector_store_folder_path, f"{index_name}.faiss"
            )
            local_vector_store_directory = self.local_vector_store_folder_path

            # Check if the local vector store directory exists
            if not os.path.exists(local_vector_store_directory):
                os.makedirs(local_vector_store_directory, exist_ok=True)

            # Check if the local vector store file exists, if not, download it
            if not os.path.exists(local_vector_store_path):
                self.download_and_prepare_directory(local_vector_store_directory)

            # Load the index
            index = self.load_index(local_vector_store_directory, index_name)
            indexes[index_name] = index
        return indexes

    def download_and_prepare_directory(self, local_vector_store_directory):
        """
        Download the necessary files for the index from Azure Storage if they do not exist locally.

        Args:
            local_vector_store_directory (str): Local directory path to save the downloaded files.
        """
        container_name = self.azure_sa_container_path
        remote_vector_store_directory = (
            f"{self.aad_object_id}/text-embedding-ada-002/vectordb"
        )
        success = self.storage_client.download_directory(
            container_name, remote_vector_store_directory, local_vector_store_directory
        )
        if not success:
            raise Exception(
                f"Failed to download necessary files for index from {remote_vector_store_directory}"
            )

    def load_index(self, local_vector_store_directory, index_name):
        """
        Load the FAISS index from the local directory.

        Args:
            local_vector_store_directory (str): Local directory containing the FAISS index.
            index_name (str): Name of the index to load.

        Returns:
            FAISS: Loaded FAISS index.
        """
        # Assuming the FAISS database is located directly in the provided directory
        return FAISS.load_local(
            local_vector_store_directory,
            self.embeddings,
            index_name=index_name,
            allow_dangerous_deserialization=True,
        )

    def retrieve(self, query):
        """
        Retrieve documents relevant to the query from all vector stores using similarity search.

        Args:
            query (str): The query string for which relevant documents are to be retrieved.

        Returns:
            all_results (list): A list of documents that are most relevant to the query.
        """
        all_results = []
        try:
            for index_name, vector_store in self.indexes.items():
                # Assume the vector_store has a method 'similarity_search_with_score' that takes a query and returns a list of tuples (document, score)
                results = vector_store.similarity_search_with_score(query, k=3)

                # Extract only the documents from the results, ignoring the scores
                documents = [doc for doc, _ in results]

                # Extend the collective results with the documents from this index
                all_results.extend(documents)

        except Exception as e:
            print(f"An error occurred during document retrieval: {str(e)}")

        return all_results
