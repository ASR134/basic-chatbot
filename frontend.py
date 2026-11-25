# on pressing enter when user types in chat_input the code code is executed from top again.
import streamlit as st
from main import chatbot
from langchain_core.messages import HumanMessage


CONFIG = {
    "configurable" : {
        "thread_id" : "1",
    },
}


if "message_history" not in st.session_state: # st.session_state preserves data across streamlit reruns.
    st.session_state["message_history"] = [] # list of dict : {"role" : ,"content" :}


for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])


user_input = st.chat_input("Type here")


def generate(): # generator - special type of iterator
    for chunk, metadata in chatbot.stream( # this is a generator object
    {
        "messages" : [HumanMessage(user_input)],
    }, # type: ignore
        config=CONFIG, # type: ignore
        stream_mode="messages", # this is for llm tokens. it streams llm tokens.
    ):
        if  chunk.content: # type: ignore
            yield chunk.content[0]["text"] # type: ignore


if user_input:

    st.session_state["message_history"].append({"role" : "user", "content" : user_input})
    with st.chat_message("user"):
        st.text(user_input)


    with st.chat_message("assistant"):
        reponse = st.write_stream(generate()) # write_stream it accepts genrator obj but it will yield everything the generator obj gives. But we need only text so we need to pass a generator obj.
        # which used chatbot.stream() genrator obj to yield only the text.

    st.session_state["message_history"].append({"role" : "assistant", "content" : reponse})