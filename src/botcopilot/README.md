# botcopilot Library

### Overview

The `botcopilot` library is designed to provide a robust foundation for building AI assistants that leverage the Retrieval-Augmented Generation (RAG) architecture. This library abstracts the complexities of creating a Q&A system by integrating with LangChain, a powerful framework for managing language models and retrieval mechanisms. The library is modular, making it easy to extend and customize for various use cases.

### Key Modules

The `botcopilot` library is organized into several key modules, each responsible for different aspects of the AI assistant's functionality:

#### 1. **bots**

- **Purpose**: This module contains the core bot implementations that handle interactions with users. 
- **Key Component**:
  - `teams_ai_bot.py`: Implements the AI bot specifically designed for integration with Microsoft Teams. This bot handles user messages, processes inputs through the RAG pipeline, and generates context-aware responses.

#### 2. **clients**

- **Purpose**: The `clients` module manages external service integrations that are essential for the bot's operation.
- **Key Components**:
  - `graph_api_client.py`: Manages interactions with the Microsoft Graph API, enabling the bot to fetch user-specific data, such as AAD object IDs and display names.
  - `storage_account.py`: Handles interactions with Azure Storage, allowing the bot to store and retrieve data such as vector databases and embeddings.

#### 3. **configurations**

- **Purpose**: This module is responsible for managing configuration settings for the entire bot application.
- **Key Component**:
  - `config.py`: Contains configuration settings such as API keys, endpoint URLs, and other environment-specific parameters. It serves as the central place to manage all configurations, ensuring the bot behaves correctly in different environments.

#### 4. **retrievers**

- **Purpose**: The `retrievers` module implements the logic for retrieving relevant documents or information from a vector database based on the user’s query.
- **Key Component**:
  - `vector_retriever.py`: Implements the retrieval mechanism using FAISS, a fast similarity search engine. This component is crucial for the RAG architecture, as it provides the context that the language model needs to generate informed responses.

#### 5. **services**

- **Purpose**: The `services` module provides various utility services that support the bot's core functionalities.
- **Key Components**:
  - `cache_strategy.py`: Implements caching strategies to optimize the bot's performance, reducing the need for repeated calls to external services.
  - **openai/**: This submodule contains classes and methods specifically for interacting with OpenAI's API.
    - `runnable.py`: Manages the execution of tasks using OpenAI’s services, such as generating responses from the language model.
  - `token_cache_strategy.py`: Manages token caching, ensuring that tokens used for authentication with external services are stored and reused efficiently.

### Architecture: Retrieval-Augmented Generation (RAG)

The `botcopilot` library is built around the RAG architecture, which enhances the AI assistant’s ability to provide accurate and contextually relevant answers. The RAG architecture works by:

1. **Retrieving**: Relevant documents or data are retrieved from a vector database based on the user’s query. This is managed by the `vector_retriever.py` module.
  
2. **Augmenting**: The retrieved data is combined with the user’s query to provide additional context.

3. **Generating**: The augmented query is then passed to a language model (e.g., via LangChain) to generate a response that is both accurate and contextually relevant.

### Integration with LangChain

The library leverages LangChain to manage interactions with language models. LangChain provides the necessary tools to handle complex workflows, ensuring that the AI assistant can efficiently process and respond to user queries.

### Customization and Extensibility

The `botcopilot` library is designed to be modular and extensible. Each module can be customized or extended to meet specific needs, making it suitable for a wide range of AI assistant applications. Whether you need to integrate with additional services, modify the retrieval logic, or enhance the generation capabilities, the library’s architecture supports these changes with minimal friction.

### Getting Started

To use the `botcopilot` library, you can include it as a dependency in your project and follow the setup instructions provided in the main `README.md` at the root of the project.

```bash
# Example: Installing the library
pip install -e .
