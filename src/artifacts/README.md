# Artifacts Directory

### Overview

The `artifacts` directory within this project is responsible for storing FAISS database artifacts, which are crucial for the bot's ability to perform fast and accurate similarity searches. These artifacts are generated and maintained for each tenant (user within the organization) and are used to support knowledge retrieval based on the user's specific context.

### Structure and Contents

Each tenant within the organization has a dedicated subdirectory in this folder. Within these subdirectories, you will find the following artifacts:

- **.faiss Files**: These are the core FAISS database files used for performing similarity searches. They contain the vector indexes that enable the bot to quickly find and retrieve relevant information from the knowledge base.

- **.pkl Files**: These files contain metadata associated with the FAISS databases, including mappings and any additional data necessary for proper operation.

### Tenant-Based Structure

The `artifacts` directory is structured to separate data by tenant. This allows the bot to tailor its responses and interactions based on the specific knowledge base associated with each tenant. For example, a subdirectory named after a tenant might look like this:

