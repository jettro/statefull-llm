import logging
import openlit

import streamlit as st
from openai import OpenAI

from change_state import set_nested_value
from model import StateChanges, LLMState, Job, Experience
from dotenv import load_dotenv

system_message_extract = f"""You are a CV writing assistant. You need specific information to help me write a my CV. You keep track of the information I provide you in a state object. 
You can ask me questions to get more information. I can ask you to remove items from the state. Your goal is to gather as much information from me as possible. You tell me 
the change you made to the state. Focus on one topic at the time. Start with completing the vacancy before moving on to the experience. 
If no change is made you return {StateChanges().model_dump_json(indent=None)}. Else the change is a json document with the structure: 
{StateChanges.model_json_schema()}.

The format of the state has the next schema:

{LLMState.model_json_schema()}
"""

system_message = """You are a CV writing assistant. You need specific information to help me write my CV. All the current information about the vacancy and my experience is available in the state object. 
Ask me a question about the vacancy or my experience to add required information for the vacancy and my experience. If you have enough information to write the CV, tell me you are ready.
"""


def extract_state_change(client: OpenAI, state: LLMState, user_message: str) -> StateChanges:
    """
    Uses the LLM to extract the state changes from the user message.

    :param client: The OpenAI client.
    :param state: The current state of the LLM.
    :param user_message: The  user message to extract the change from
    :return: The changes extracted from the user message.
    """
    chat_completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message_extract},
            {"role": "user", "content": f"{user_message}\nstate: {state.model_dump_json()}"},
        ],
        response_format=StateChanges,
    )
    response_format = chat_completion.choices[0].message.parsed
    logger.info(response_format)
    return response_format


def ask_for_next_step(client: OpenAI, state: LLMState) -> str:
    """
    With the updated state, ask the LLM for the next step in information gathering.
    :param client: The OpenAI client.
    :param state:  The updated state.
    :return: The message from the LLM containing the next step for the user.
    """
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"state: {state.model_dump_json()}"},
        ]
    )
    response_format = chat_completion.choices[0].message.content
    logger.info(response_format)
    return response_format


def main_loop(client: OpenAI, state: LLMState, historic_changes: StateChanges, user_message: str) -> str:
    """
    The main loop of the application. Extracts the state changes from the user message, updates the state,
    and asks for the next step.

    :param client: The OpenAI client.
    :param state: The current state of the LLM.
    :param historic_changes:  The historic changes made to the state.
    :param user_message: The user message to extract the changes from.
    :return: The next step for the user.
    """
    changes = extract_state_change(client, state, user_message)

    for change in changes.changes:
        logger.info(f"Change: {change.change}, field: {change.field}, value: {change.value}")
        historic_changes.add_change(change)
        set_nested_value(state, change)

    logging.info(state)

    next_step = ask_for_next_step(client, state)

    logging.info(next_step)
    return next_step


def init_session():
    if "openai_client" not in st.session_state:
        st.session_state.openai_client = OpenAI()
    if "llm_state" not in st.session_state:
        st.session_state.llm_state = LLMState(vacancy=Job(), experience=Experience())
    if "historic_changes" not in st.session_state:
        st.session_state.historic_changes = StateChanges()
    if "messages" not in st.session_state:
        st.session_state.messages = []


def main():
    logger.info("Welcome to Stateful LLMs!")
    init_session()

    client = st.session_state.openai_client
    starting_state = st.session_state.llm_state
    historic_changes = st.session_state.historic_changes

    st.title("Stateful LLMs")
    main_col, status_col = st.columns([2, 1])

    with main_col:
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # React to user input
        if prompt := st.chat_input("What is up?"):
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            response = main_loop(client, starting_state, historic_changes, prompt)
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
    with status_col:
        st.subheader("Vacancy")
        st.write(f"Title: {starting_state.vacancy.title}")
        st.write(f"Company: {starting_state.vacancy.company}")
        st.write("Wishes: ")
        for wish in starting_state.vacancy.wishes:
            st.write(f"- {wish}")

        st.subheader("Experience")
        st.write(f"Years: {starting_state.experience.years}")
        st.write(f"Current employer: {starting_state.experience.current}")
        st.write(f"Previous Employers: {','.join(starting_state.experience.previous_employers)}")
        st.write("Previous Roles: ")
        for role in starting_state.experience.previous_roles:
            st.write(f"- {role.title} at {role.company} for {role.years} years.")
            st.write(f"{role.description}")
            st.write("---")

        st.subheader("Historic Changes")
        if historic_changes and historic_changes.changes:
            for change in reversed(historic_changes.changes[-10:]):
                st.write(f"{change.change} - {change.field} - {change.value}")


load_dotenv()

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

openlit.init(otlp_endpoint="http://127.0.0.1:4318")

st.set_page_config(page_title='Stateful LLMs', page_icon='🧠', layout='wide')
main()
