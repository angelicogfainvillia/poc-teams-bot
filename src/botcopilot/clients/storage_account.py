import os
import pickle  # nosec B403
from io import BytesIO
from azure.storage.blob import BlobServiceClient, BlobType


class StorageAccountClient:
    def __init__(self, account_name: str, account_key: str):
        self.connection_string = (
            f"DefaultEndpointsProtocol=https;AccountName={account_name};"
            f"AccountKey={account_key};EndpointSuffix=core.windows.net"
        )
        self.blob_service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )

    def upload_pickle(self, container, blob_name, obj):
        blob_client = self.blob_service_client.get_blob_client(
            container=container, blob=blob_name
        )
        with BytesIO() as buffer:
            pickle.dump(obj, buffer)
            buffer.seek(0)
            blob_client.upload_blob(buffer, blob_type=BlobType.BlockBlob)

    def download_directory(
        self, container: str, remote_directory: str, local_directory: str
    ):
        container_client = self.blob_service_client.get_container_client(container)
        blobs = list(container_client.list_blobs(name_starts_with=remote_directory))
        if not blobs:
            print(f"No blobs found in {remote_directory}")
            return False

        os.makedirs(local_directory, exist_ok=True)  # Ensure the base directory exists
        for blob in blobs:
            blob_client = container_client.get_blob_client(blob)
            # Correctly calculate the local path for each blob based on its name in the storage

            # Relative path from the remote_directory
            relative_path = os.path.relpath(blob.name, remote_directory)

            # Construct the full local path
            path_to_file = os.path.join(local_directory, relative_path)
            os.makedirs(os.path.dirname(path_to_file), exist_ok=True)

            # Ensure the directory for this file exists
            with open(path_to_file, "wb") as file_stream:
                data = blob_client.download_blob().readall()
                file_stream.write(data)
        return True
