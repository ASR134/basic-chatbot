from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END, add_messages
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver


load_dotenv()


model = ChatGoogleGenerativeAI(
    model = "gemini-3.1-flash-lite"
)


# define state
class ChatState(TypedDict):

    messages : Annotated[list[BaseMessage],add_messages]



def chat_node(state: ChatState):

    messages = state['messages']

    response = model.invoke(messages)

    return {"messages" : [response]}



# define graph
graph = StateGraph(ChatState)


# add nodes
graph.add_node("chat_node",chat_node)


# add edge
graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

checkpointer = MemorySaver()

# compile graph
chatbot = graph.compile(checkpointer=checkpointer)

# testing
# response = chatbot.invoke(
#     {
#         "messages" : [HumanMessage("who am i")],
#     },
#     config={
#         "configurable" : {
#             "thread_id" : '1',
#         },
#     },
# )

# print(response)