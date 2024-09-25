import msal
import requests
from botcopilot.configurations.config import DefaultConfig as config


class GraphApiClient:
    def __init__(self):
        self.client_id = config.GRAPH_API_CLIENT_ID
        self.client_secret = config.GRAPH_API_CLIENT_SECRET
        self.tenant_id = config.GRAPH_API_TENANT_ID
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]
        self.msal_app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret,
        )

    def get_access_token(self):
        result = self.msal_app.acquire_token_for_client(scopes=self.scope)
        if "access_token" in result:
            return result["access_token"]
        else:
            raise Exception("Could not obtain access token")

    def get_user_aad_object_id(self, user_principal_name):
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        endpoint = f"https://graph.microsoft.com/v1.0/users/{user_principal_name}"
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        user_data = response.json()
        return user_data.get("id")

    def get_user_display_name(self, user_id):
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        endpoint = f"https://graph.microsoft.com/v1.0/users/{user_id}"
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        user_data = response.json()
        return user_data.get("displayName")
