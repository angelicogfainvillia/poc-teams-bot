from abc import ABC, abstractmethod


class CacheStrategy(ABC):
    @abstractmethod
    def add_message(self, message: str) -> None:
        """Add a new message to the cache."""

        pass

    @abstractmethod
    def get_context(self) -> str:
        """Get the current context from the cache."""

        pass

    @abstractmethod
    def trim_context(self) -> None:
        """Trim the context to ensure it stays within the token limit."""

        pass
