from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END, add_messages
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver


load_dotenv()


model = ChatGoogleGenerativeAI(
    model = "gemini-3.6-flash"
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

# stream = chatbot.stream( # returns a generator object
#     {
#         "messages" : [HumanMessage('hello how are you?')],
#     }, # type: ignore
#     {
#         "configurable" : {
#             "thread_id" : "1",
#         }
#     },
#     stream_mode="messages", # this is for llm tokens. it streams llm tokens.
# )

# for chunk, metadata in stream:
#     if chunk.content:
#         print(chunk.content[0]["text"],end = " ",flush=True)

# for update in stream:# use when stream_mode = "updates".
#     print(update)