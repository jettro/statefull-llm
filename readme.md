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

The code includes monitoring the LLM usage using OpenLit. To use this feature, you need to have an OpenLit Docker container running. You can find the OpenLit installation instructions [here](https://docs.openlit.io/latest/quickstart-observability/). You only need the Docker compose part of the installation.
If you do not want to use OpenLit, you can comment out the `openlit` import in the `main.py` file, and comment the following line in the same file `openlit.init(otlp_endpoint="http://127.0.0.1:4318")`.


# Usage
To run the project, use the following command:

```bash
poetry run python run.py
```
