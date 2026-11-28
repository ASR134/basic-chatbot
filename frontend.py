# on any interaction with app by the user the python script reruns from top to bottom and then executing the block of code under it.
import streamlit as st
import os
st.write("Tracing:", os.getenv("LANGSMITH_TRACING"))
st.write("API key exists:", bool(os.getenv("LANGSMITH_API_KEY")))
st.write("Endpoint:", os.getenv("LANGSMITH_ENDPOINT"))
st.write("Project:", os.getenv("LANGSMITH_PROJECT"))
from main_db import chatbot, retrieve_threads
from langchain_core.messages import HumanMessage
import uuid


# ****************************************** UTILITY FUNCTIONS *******************************************************


def generate_thread_id():
    id = uuid.uuid4()
    return id

def reset_chat():
    thread_id = generate_thread_id()
    add_thread(thread_id)
    st.session_state["session_id"] = thread_id
    st.session_state["message_history"] = []


def add_thread(thread_id):
    st.session_state["chat_threads"].append(thread_id)

def generate(): # generator - special type of iterator. used here for streaming
    for chunk, metadata in chatbot.stream( # this is a generator object
    {
        "messages" : [HumanMessage(user_input)],
    }, # type: ignore
        config=CONFIG, # type: ignore
        stream_mode="messages", # this is for llm tokens. it streams llm tokens.
    ):
        if  chunk.content: # type: ignore
            yield chunk.content[0]["text"] # type: ignore


def load_conversation(thread_id):

    response = chatbot.get_state(config={"configurable" : {"thread_id" : thread_id}})

    return response.values.get("messages",[])




# ********************************* SESSION SETUP *******************************************************


if "message_history" not in st.session_state: # st.session_state preserves data across streamlit reruns.
    st.session_state["message_history"] = [] # list of dict : {"role" : ,"content" :}

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_threads()

if "session_id" not in st.session_state:
    st.session_state["session_id"] = generate_thread_id()
    add_thread(st.session_state["session_id"])


# ****************************************** SIDEBAR ****************************************************

st.sidebar.title("ChatBot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("Past Conversations")

for thread_id in st.session_state["chat_threads"][::-1]:

    if st.sidebar.button(str(thread_id)):
        st.session_state["session_id"] = thread_id # to continue a particular conversation
        messages = load_conversation(thread_id)

        temp = []
        for message in messages:
            if isinstance(message,HumanMessage):
                temp.append({"role" : "user","content" :message.content})
            else:
                role = "assistant"
                temp.append({"role" : "assistant", "content" : message.content[0]["text"]}) 

        st.session_state["message_history"] = temp



# *********************************************************** MAIN UI ***************************************************


for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])


user_input = st.chat_input("Type here")


CONFIG = {
    "configurable" : {
        "thread_id" : st.session_state["session_id"],
    },
    "metadata" : {
        "thread_id" : st.session_state["session_id"],
    },
    "run_name" : "chat_turn",
}

if user_input:

    st.session_state["message_history"].append({"role" : "user", "content" : user_input})
    with st.chat_message("user"):
        st.text(user_input)


    with st.chat_message("assistant"):
        response = st.write_stream(generate()) # write_stream it accepts genrator obj but it will yield everything the generator obj gives. But we need only text so we need to pass a generator obj.
        # which used chatbot.stream() genrator obj to yield only the text.

    st.session_state["message_history"].append({"role" : "assistant", "content" : response})