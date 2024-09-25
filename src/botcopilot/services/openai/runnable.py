from botcopilot.configurations.config import DefaultConfig as config
from langchain_core.runnables import Runnable


class AzureOpenAIRunnable(Runnable):
    def __init__(self, azure_client):
        self.azure_client = azure_client

    def invoke(self, conversation_history, context=None):
        try:
            # convert the conversation history into the required messages format
            formatted_messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in conversation_history
            ]

            # fetch model parameters from configuration
            model_params = config.BOT_PARAMS["model_params"]

            # call Azure OpenAI with formatted conversation history and model parameters
            response = self.azure_client.chat.completions.create(
                messages=formatted_messages, **model_params
            )

            # return the AI's response if available; otherwise, provide a default message
            return (
                response.choices[0].message.content
                if response.choices
                else "Desculpe, não tenho uma resposta para a sua última mensagem."
            )

        except Exception as e:
            # Handle unexpected errors
            return f"An error occurred: {str(e)}"
