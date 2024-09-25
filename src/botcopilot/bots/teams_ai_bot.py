import uuid
import asyncio
from typing import List
from openai import AzureOpenAI
from botcopilot.services.cache_strategy import CacheStrategy
from botcopilot.clients.graph_api_client import GraphApiClient
from botcopilot.services.openai.runnable import AzureOpenAIRunnable
from botcopilot.configurations.config import DefaultConfig as config
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes
from botcopilot.services.token_cache_strategy import TokenCacheStrategy
from botcopilot.retrievers.vector_retriever import AzureVectorStoreRetriever
from botbuilder.core import (
    ActivityHandler,
    MessageFactory,
    TurnContext,
    ConversationState,
    StatePropertyAccessor,
    UserState,
)


class TeamsAIBot(ActivityHandler):
    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        if not conversation_state:
            raise Exception("ConversationState must be provided.")
        if not user_state:
            raise Exception("UserState must be provided.")

        self.conversation_state = conversation_state
        self.user_state = user_state
        self.user_state_accessor: StatePropertyAccessor = (
            self.user_state.create_property("UserState")
        )
        self.cache_strategy: CacheStrategy = TokenCacheStrategy()
        self.session_ids = {}
        self.user_artifact_paths = {}

        # Initialize Azure OpenAI client with configuration details for GPT-4
        self.azure_openai_client = AzureOpenAI(
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version="2024-02-15-preview",
            base_url=f"{config.AZURE_OPENAI_ENDPOINT}/openai/deployments/{config.AZURE_OPENAI_DEPLOYMENT_ID}/",
        )

        self.azure_client = self.azure_openai_client

        # Create an instance of the runnable for processing chat with GPT-4
        self.azure_runnable = AzureOpenAIRunnable(self.azure_client)

        # Initialize AzureVectorStoreRetriever for document retrieval
        self.retriever = None  # This will be initialized later based on user ID

        # Initialize conversation history with system prompt
        self.cache_strategy.add_message(
            {"role": "system", "content": config.BOT_PARAMS["system_prompt"]}
        )

        # Initialize Graph API Client
        self.graph_api_client = GraphApiClient()

    async def on_members_added_activity(
        self, members_added: List[ChannelAccount], turn_context: TurnContext
    ):
        # Welcome message for new users
        for member in members_added:
            if (
                member.id != turn_context.activity.recipient.id
            ):  # Avoid sending welcome to the bot itself
                # Fetch AAD object ID
                user_id = member.id
                aad_object_id = member.aad_object_id

                try:
                    # Fetch user display name from Graph API
                    user_name = self.graph_api_client.get_user_display_name(
                        aad_object_id
                    )

                except Exception as e:
                    error_message = f"Failed to get user display name for user ID <{user_id}>, aad_obkect_id:{aad_object_id}. error: {str(e)}"
                    print(error_message)
                    await turn_context.send_activity(
                        "The bot encountered an error or bug."
                    )
                    await turn_context.send_activity(
                        f"Error details: {error_message}\nTo continue to run this bot, please fix the bot source code."
                    )
                    return

                welcome_text = config.BOT_PARAMS["welcome_text"]
                personalized_welcome = f"Olá, {user_name}. " + welcome_text
                await turn_context.send_activity(
                    MessageFactory.text(personalized_welcome)
                )

                # Set the user's artifact path and save user state
                self.user_artifact_paths[member.id] = (
                    aad_object_id,
                    f"{config.LOCAL_ARTIFACTS_BASE_FOLDER_PATH}/{aad_object_id}/text-embedding-ada-002",
                )
                await self.user_state_accessor.set(
                    turn_context, {"aad_object_id": aad_object_id}
                )
                await self.user_state.save_changes(turn_context, force=True)
                await self.initialize_retriever(turn_context, member.id, aad_object_id)

    async def on_message_activity(self, turn_context: TurnContext):
        user_id = turn_context.activity.from_property.id

        # Send typing indicator
        await self._send_typing_indicator(turn_context)

        # Generate or retrieve session ID for the user
        if user_id not in self.session_ids:
            self.session_ids[user_id] = str(uuid.uuid4())

        user_input = turn_context.activity.text.strip()
        self.cache_strategy.add_message({"role": "user", "content": user_input})

        # Retrieve relevant documents based on user input
        if self.retriever is None:
            user_state = await self.user_state_accessor.get(turn_context, None)
            if user_state is None or "aad_object_id" not in user_state:
                # Simulate the member being added to trigger the welcome message flow
                await self.on_members_added_activity(
                    [turn_context.activity.from_property], turn_context
                )
                return

            aad_object_id = user_state["aad_object_id"]
            await self.initialize_retriever(turn_context, user_id, aad_object_id)

        retrieval_results = await self._retrieve_documents(turn_context, user_input)
        if retrieval_results:
            context_documents = " ".join(
                [doc.page_content for doc in retrieval_results]
            )
        else:
            context_documents = "No relevant documents found."

        # Update the conversation with context and query
        prompt_with_context = f"{context_documents}\n{user_input}"
        self.cache_strategy.add_message(
            {"role": "system", "content": prompt_with_context}
        )

        # Invoke the chat chain with updated conversation history
        context = self.cache_strategy.get_context()
        response = await self._invoke_chat_model(turn_context, context)

        # Send the processed response back to the user
        await turn_context.send_activity(MessageFactory.text(response))

        # Append bot's response to conversation history
        self.cache_strategy.add_message({"role": "assistant", "content": response})

        # Save conversation state
        await self.conversation_state.save_changes(turn_context, force=False)

    async def _send_typing_indicator(self, turn_context: TurnContext):
        typing_activity = Activity(
            type=ActivityTypes.typing,
            relates_to=turn_context.activity.relates_to,
        )
        await turn_context.send_activity(typing_activity)

    async def _retrieve_documents(self, turn_context: TurnContext, query: str):
        # Send typing indicators periodically until documents are retrieved
        interval = 1  # seconds
        send_typing_task = asyncio.create_task(
            self._send_typing_periodically(turn_context, interval)
        )

        try:
            results = self.retriever.retrieve(query)
        finally:
            send_typing_task.cancel()
            try:
                await send_typing_task
            except asyncio.CancelledError:
                pass

        return results

    async def _invoke_chat_model(self, turn_context: TurnContext, context):
        # Send typing indicators periodically until chat model invocation is complete
        interval = 1  # seconds
        send_typing_task = asyncio.create_task(
            self._send_typing_periodically(turn_context, interval)
        )

        try:
            response = self.azure_runnable.invoke(context)
        finally:
            send_typing_task.cancel()
            try:
                await send_typing_task
            except asyncio.CancelledError:
                pass

        return response

    async def _send_typing_periodically(self, turn_context: TurnContext, interval: int):
        try:
            while True:
                await self._send_typing_indicator(turn_context)
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            pass

    async def initialize_retriever(
        self, turn_context: TurnContext, user_id, aad_object_id
    ):
        artifact_path = self.user_artifact_paths.get(user_id)[1]
        if artifact_path:
            self.retriever = AzureVectorStoreRetriever(
                azure_api_key=config.AZURE_OPENAI_API_KEY,
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
                azure_openai_deployment_id="text-embedding-ada-002",
                aad_object_id=aad_object_id,
            )
        await self.conversation_state.save_changes(turn_context, force=False)
