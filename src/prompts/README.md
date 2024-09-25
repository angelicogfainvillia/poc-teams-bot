# Prompts Directory

### Overview

The `prompts` directory contains text files that define key prompts used by the AI assistant. These prompts play a crucial role in shaping the interaction between the user and the AI. Specifically, the `system_prompt` and `welcome_message` files are essential for setting the tone and context of the conversation.

### Files in this Directory

#### 1. `system_prompt`

- **Purpose**: The `system_prompt` file defines the AI assistant's role and tasks. This prompt sets the initial context for the AI, guiding its behavior and responses throughout the conversation.
  
- **Importance**: The system prompt is critical as it acts as the "personality" and directive of the AI assistant. It instructs the AI on how to behave, what tasks to prioritize, and how to respond to the user's queries. This prompt is not visible to the user but heavily influences the AI's behavior.

- **Example Usage**: A system prompt might instruct the AI to behave as a professional assistant, providing thoughtful and context-aware responses to the user. It could include directives such as:
  - "You are a helpful assistant."
  - "Your goal is to assist users in decision-making and provide insights based on the available data."

#### 2. `welcome_message`

- **Purpose**: The `welcome_message` file contains the first message that the user will receive from the AI assistant when they start a conversation.
  
- **Importance**: The welcome message is the first point of contact between the user and the AI assistant. It sets the tone for the interaction, introduces the AI, and provides any necessary context or instructions for the user.

- **Example Usage**: A welcome message might greet the user warmly and provide an overview of how the AI can assist them. It could include:
  - "Hello! I'm your AI assistant here to help with your tasks and provide insights."
  - "Feel free to ask me anything related to your project or team management."

### Example: "Hello, World!"

To illustrate the use of these files, here is a simple "Hello, World!" example:

#### `system_prompt`
Act as a specialist in the context <CONTEXT>. You are an AI assistant that provides simple, clear, and helpful responses. Your task is to greet the user and offer assistance with basic tasks.


#### `welcome_message`
Hey! I'm your friendly AI assistant. How can I assist you today?
