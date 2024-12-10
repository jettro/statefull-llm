# Stateful LLM
Welcome to this small example project. This project demonstrates the use of a state model with a Large Language Model (LLM) to generate text. The state is used to store information about the context of the text that is being generated. This allows the LLM to generate text that is more coherent and relevant to the context.

# Installation
To install the project, simply clone the repository and install the required dependencies using poetry:

```bash
poetry install
```

You need to create a `.env` file in the root of the project with the following content

```text
OPENAI_API_KEY=<your-openai-api-key>
```

# Usage
To run the project, use the following command:

```bash
poetry run python run.py
```
