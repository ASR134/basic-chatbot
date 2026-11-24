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


if user_input:

    st.session_state["message_history"].append({"role" : "user", "content" : user_input})
    with st.chat_message("user"):
        st.text(user_input)

    response = chatbot.invoke(
        {
            "messages" : [HumanMessage(content=user_input)],
        },
        config = CONFIG,
    )

    response = response["messages"][-1].content[0]["text"]

    st.session_state["message_history"].append({"role" : "assistant", "content" : response})
    with st.chat_message("assistant"):
        st.text(response)