from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.messages import AIMessage, HumanMessage
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain.schema import HumanMessage, SystemMessage
from langchain.tools.render import format_tool_to_openai_function
import os,re
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import env
import warnings
from langchain.agents import tool

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# print(variable_to_export)


# Set up GPT-3.5
llm = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0.7,model="gpt-3.5-turbo-1106")

#Agent Information Taker
#tool for tracking asked information step 4. Details to extract: Name, email, phone no, Address, Date of birth, Education.
@tool
def list_personal_info(key):
    """useful when u have to ask user to give information .Asks the user for personal information .you will get {key} as prameter.
    this {key} will be a required variable.
    you have ask user to give this {key} personal information according to your expertise as an assitant."""
@tool
def ini():
    """useful when you have to initiate conversation in a professional way dont use any other tools"""
# Custom tool for handlng information asking   
tools = [list_personal_info,ini]
#Adding memory for remembering previous conversation so that it will be in loop
#until we got full information
MEMORY_KEY = "chat_history"
#________________________________________________________________________________________________________________
#Initiation Agnet that will write welcome message
prompt_ini = ChatPromptTemplate.from_messages(
    [
        (
            "system","""You are very powerful.now you have to write welcome mesage for user who comes on website
            we are taking thier peronal information to give personalised srevice
            write message n short,professionally,not more than 3 lines.include emoji . make it engaging which
            attracts user to give information.
            """,
        ),
        MessagesPlaceholder(variable_name=MEMORY_KEY),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
ini_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools]) # type: ignore
chat_history = []
agenti = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_function_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | prompt_ini| ini_with_tools| OpenAIFunctionsAgentOutputParser()
)
agent_ini = AgentExecutor(agent=agenti, tools=tools, verbose=True) # type: ignore
#_____________________________________________________________________________________________________________________________________
#Taker Agent: that will ask user to give information.

prompt_taker = ChatPromptTemplate.from_messages(
    [
        (
            "system","""You are very powerful assistant, but you always have to check which information you have to ask each time.
            Ask in professionally by convincing him how can this will help him to personalize servives.
            Ask in some time funny way/creative way because you are powerful.
            dont ask in more than 3 lines.
            Now u have memory of previous chat if user already given any information thanks them for giving in your next question. 
            Be mindful not to repeat questions, stay on topic, and guide the user smoothly through the interaction. 
            If the user provides information, acknowledge it, and ask follow-up questions. If the user asks unrelated questions,
            gently guide them back to the main topic. Ensure a natural and consistent chat flow.
            Assume that obtained information is empty if not provided.
            always ask which key u got from input.
            """,
        ),
        MessagesPlaceholder(variable_name=MEMORY_KEY),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
taker_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools]) # type: ignore
agentt = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_function_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | prompt_taker| taker_with_tools| OpenAIFunctionsAgentOutputParser()
)
agent_taker = AgentExecutor(agent=agentt, tools=tools, verbose=True) # type: ignore
input1 = "how much information u want to ask and why"
# res1=agent_taker.invoke({"input": input1
#                         ,"chat_history": chat_history
#                         })
# chat_history.extend([HumanMessage(content=input1),AIMessage(content=res1["output"]),])
# res=agent_taker.invoke({"input": "Ask information what u want assume now i did not obtained anything? obtained=['DOB']"
#                         ,"chat_history": chat_history
#                         })
# print(res['output'])
#_____________________________________________________________________________________________________________________________
# Extraction Agent:that will extract structered information from user response
extraction_agent_template=ChatPromptTemplate.from_messages(
    [
        (
            "system","""You are very powerful assistant,Who will help in extracting structered information from user input.
            please remember you are powerful the information can be in any format.you have to read carefylly
            and extract asked information.
            please dont check always same information.focus on key u will get from user_input and extract it can be anything from 
            thism['DOB','Name','Email','Mob No',"Batchler's degree",'Skills']
            If you are not able to get any information then dont do nything just return information is not correct.
            if input is out of context in your response you must add  sorry word.
            if asked key is in input must return only structred information.
            """,
        ),
        MessagesPlaceholder(variable_name=MEMORY_KEY),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
extract_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools]) # type: ignore
extraction_agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_function_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | extraction_agent_template|extract_with_tools| OpenAIFunctionsAgentOutputParser()
)
agent_ex = AgentExecutor(agent=extraction_agent, tools=tools, verbose=True) # type: ignore

# Usage
user_input = "who are u"
# extraction_output = agent.invoke({"input": user_input, "chat_history": chat_history})
# chat_history.extend(extraction_output["output"])
# print(">>>>>.",extraction_output)
#________________________________________________________________________________________________________________
#Agent Convincing :that will convince user to share info if hesitant,etc.
Convincing_agent_template=ChatPromptTemplate.from_messages(
    [
        (
            "system","""you are convincing agent,powerful assistant,you know how to convince people.
            your ultimate goal is to take user confidence to give information.
            ist you always start with some question related to enjoyment,like ,movie,place,anything that makes user to engagein chat.
            after positive response of 2 to 3 times you hav eto guide on topic why we rae taking information.
            if user ask any out of contextlike sex,abuse,adultry dont reply just say you cant do this.
            Be mindful not to repeat questions, stay on topic, and guide the user smoothly through the interaction. 
            If the user provides information, acknowledge it, and ask follow-up questions. If the user asks unrelated questions,
            gently guide them back to the main topic. Ensure a natural and consistent chat flow.
            Assume that obtained information is empty if not provided.
            please reply if he ask any question.
            """,
        ),
        MessagesPlaceholder(variable_name=MEMORY_KEY),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
conv_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools]) # type: ignore
conv_agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_function_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | Convincing_agent_template|conv_with_tools| OpenAIFunctionsAgentOutputParser()
)
agent_conv = AgentExecutor(agent=conv_agent, tools=tools, verbose=True) # type: ignore

# Usage
# user_input = "are u convincing agent"
# conv_output = agent_conv.invoke({"input": user_input, "chat_history": chat_history})
# chat_history.extend(conv_output["output"])
# print(">>>>>.",conv_output['output'])
#_________________________________________Done___________________________________________________________________________
print("_______________________________________________Thankyou_________________________________________________________")
print("for testing each agent uncomment each agent corresponding usage")

