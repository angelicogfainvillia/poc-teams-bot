import tiktoken
from .cache_strategy import CacheStrategy
from botcopilot.configurations.config import DefaultConfig

CONFIG = DefaultConfig()

LIMIT_TOKENS = CONFIG.BOT_PARAMS["limit_context_window_max_tokens"]


class TokenCacheStrategy(CacheStrategy):
    """
    Manages conversation history and keeps the total token count within a limit.
    """

    def __init__(self):
        """
        Initializes with an empty message list and a token encoder.
        """

        self.messages = []
        self.encoder = tiktoken.get_encoding("cl100k_base")

    def add_message(self, message: dict) -> None:
        """
        Adds a new message and trims context to stay within the token limit.

        Args:
            message (dict): A message with 'role' and 'content'.
        """

        self.messages.append(message)
        self.trim_context()

    def get_context(self) -> list:
        """
        Gets the current conversation context.

        Returns:
            list: The current messages.
        """

        return self.messages

    def trim_context(self) -> None:
        """
        Trims the context to ensure the total token count is within the limit.
        """

        total_tokens = self.count_tokens(self.messages)
        while total_tokens > LIMIT_TOKENS and self.messages:
            self.messages.pop(0)
            total_tokens = self.count_tokens(self.messages)

    def count_tokens(self, messages) -> int:
        """
        Counts the total tokens in the messages.

        Args:
            messages (list): The messages to count tokens from.

        Returns:
            int: The total token count.
        """

        messages_text = " ".join([msg["content"] for msg in messages])
        return len(self.encoder.encode(messages_text))
