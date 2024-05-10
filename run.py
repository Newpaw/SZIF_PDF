import os
import streamlit as st
from openai import OpenAI, AssistantEventHandler
from dotenv import load_dotenv
from typing_extensions import override

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
assistent_id = os.getenv("ASSISTANT_ID")
vectore_storage_id = os.getenv("VS_STORAGE")

client = OpenAI(api_key=openai_api_key)


def ensure_single_thread_id():
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
    return st.session_state.thread_id

def upload_and_create_thread(file):
    if file is not None:
        message_file = client.files.create(
            file=file,
            purpose="assistants"
        )
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": "Prosím, analyzuj přiložený dokument.",
                    "attachments":[{"file_id": message_file.id, "tools": [{"type": "file_search"}]}]
                }
            ]
        )
        return thread

def stream_generator(prompt, thread_id):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        assistent_id=assistent_id,
        content=prompt
    )
    with st.spinner("Wait... Generating response..."):
        stream = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistent_id=assistent_id,
            stream=True
        )
        for event in stream:
            if event.data.object == "thread.message.delta":
                for content in event.data.delta.content:
                    if content.type == "text":
                        yield content.text.values
            else:
                pass

st.set_page_config(page_icon=":speech_balloon:")
st.title("Chatbot")
st.caption("Streamlit + OpenAI")

with st.sidebar:
    upload_file = st.file_uploader("Upload file")
    if upload_file is not None:
        thread = upload_and_create_thread(upload_file)
        if thread:
            st.session_state.thread_id = thread.id
            st.success("Thread created")
            print(thread.tool_resources.file_search)

if "message" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Enter your message")
if prompt:
    thread_id = ensure_single_thread_id()
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response = st.write_stream(stream_generator(prompt, thread_id))
    st.session_state.messages.append({"role": "assistant", "content": response})
