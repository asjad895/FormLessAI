from re import T
from flask import Flask, render_template, request,jsonify,json
from chat import agent_taker,chat_history,agent_ex,agent_ini,agent_conv
from langchain.chat_models import ChatOpenAI
import csv,time
import pandas as pd
from datetime import datetime
chat_history=[]

from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.messages import AIMessage, HumanMessage
import os
import env
import warnings
open_ai_key = os.environ.get("OPENAI_API_KEY")
app = Flask(__name__)
#__________________________________________________________________________________________________________________________
#Initiation Agent prompt
input1="Write message according to your specilaity."
#User Data Store
#Step 4. Details to extract: Name, email, phone no, Address, Date of birth, Education.
columns = ['DOB', 'Name', 'Email', 'Mob No', "Batchler's degree", 'Skills']
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
username='Demo'
csv_file_path = f"./extracted_data/user_{username}_{current_time}_data.csv"
df = pd.DataFrame(columns=columns)
# df.to_csv(csv_file_path,index=False)
#Running InitiationAgent for initiating conversation
print("calling initiater")
response=agent_ini.invoke({"input":input1,"chat_history": chat_history })
chat_history.extend([HumanMessage(content=input1),AIMessage(content=response["output"]),])
print("Going forward.....")
#________________________________________________________________________________________________________________________________ 
#Step 3.Design a coherent conversation flow where users will easily give the information or convince well to give their info.
# ● If the user is hesitant then initiate small talk and later circle back to the question regarding their personal informatio
def analze_user_input(user_input,key):
    """
    Analyzes user input and decides whether to initiate small talk or proceed with information gathering
    and Extraction
    """
    print("Analyzing.................")
    #Detect hesitancy in user input
    if detect_hesitancy(user_input):
        print("hesitating.")
        # User seems hesitant, initiate small talk
        time.sleep(25)
        small_talk_ini = initiate_small_talk()
        return small_talk_ini
    else:
        # User is ready to share information, directly handle the information request
        extract_information(user_input=user_input,key=key)

def detect_hesitancy(user_input):
    """function to detect hesitancy in user input.
    """
    hesitancy_keywords = ["not sure", "maybe", "I don't know", "hesitant","why","who",'dont']
    return any(keyword in user_input.lower() for keyword in hesitancy_keywords)

def initiate_small_talk():
    """function to initiate small talk usin Convincing Agent.
    """
    #Convince agent wil talk to convince him
    user_input = "Ask user to some intresting question and engage them in chat.rememer your expertise"
    conv_output = agent_conv.invoke({"input": user_input, "chat_history": chat_history})
    chat_history.extend([HumanMessage(content=user_input),AIMessage(content=conv_output["output"]),])
    return conv_output['output']


def is_confidence_built(response):
    """
    function to determine if confidence is built based on the small talk response.
    """
    # Check for positive or engaging responses
    positive_keywords = ["great", "interesting", "fun","wow","sure","happy","always"]
    return any(keyword in response.lower() for keyword in positive_keywords)
# _______________________________________________________________________________________________________________________________
# 8. After gathering user details from agents, format the data appropriately.
# ● You should save the user details as they are obtained and not wait till all the details are
# received.
# 9. Create a CSV file using libraries like pandas in Python.
def extract_information(user_input,key):
    """
    function to Extract structered information using Extarction agent and saved it..
    """
    # Call the function from your original implementation
    print("Extracting.......")
    input=f"Extract {key} as strucured information form {user_input}"
    ex_out=agent_ex.invoke({'input':input,'chat_history':chat_history})
    chat_history.extend([HumanMessage(content=user_input),AIMessage(content=ex_out["output"]),])
    df[key]=ex_out['output']
    print("key",key)
    print(df.head())
    print(ex_out['output'])
    df.to_csv('user_data.csv',index=False)

def continue_small_talk(user_input):
    """
    function to continue small talk if confidence is not yet built.
    """
    # follow-up small talk response
    #Continue discussing topics related to the user's interests
    user_input = user_input
    conv_output = agent_conv.invoke({"input": user_input, "chat_history": chat_history})
    chat_history.extend([HumanMessage(content=user_input),AIMessage(content=conv_output["output"]),])
    return conv_output['output']

def got_confidence(key):
    """_Function to ask user information using Taker Agent._

    Args:
        key (string): _asking key like dob,name etc_

    Returns:
        _AIMessage_: _Agent response_
    """
    print("got_confidence.......")
    input_prompt=f"""Ask information about {key} to give which is not yet obtained.dont assume anything ,here 
    {key} yet not  recived u have to ask to user by your expertises to give this."""
    res=agent_taker.invoke({"input": input_prompt,"chat_history":chat_history})
    chat_history.extend([HumanMessage(content=input_prompt),AIMessage(content=res["output"]),])
    return res["output"]
    
#_______________________________________________________________________________________________________________________
#App Logic,url managemnet,client server mmanagment
@app.route('/', methods=['GET'])
def home():
    return render_template('app.html', model_output=response['output'])

obtained=[]
i=0
@app.route('/Form', methods=['GET', 'POST'])
def FormlessAI(obtained=obtained, i=i):
    # Initialize variables
    conf = True
    key = columns[i]
    input_prompt = f"Ask information about {key} which is not yet obtained, assume obtained as empty if not provided? obtained={obtained}"
    
    # Invoke the agent_taker to get a response
    res = agent_taker.invoke({"input": input_prompt, "chat_history": chat_history})
    
    # Update chat history with user and AI messages
    chat_history.extend([HumanMessage(content=input_prompt), AIMessage(content=res["output"]),])
    
    # Check if the request method is POST
    if request.method == 'POST':
        # Get user input from the form
        user_input = request.form['user_input']
        print(user_input)
        
        # Analyze user input and obtain the result
        resa = analze_user_input(user_input=user_input, key=key)
        time.sleep(25)
        
        # Check if the result is not None
        if resa is not None:
            conf = False
            # Render the template with the model output
            return render_template('form.html', model_output=resa['output'])
        elif conf == False:
            # After small talk, check if confidence is built
            if is_confidence_built(user_input):
                print("confidence.....")
                # Call the function to handle the next information request
                conf = True
                time.sleep(25)
                res = got_confidence(key=key)
            else:
                # Continue with more small talk or handle accordingly
                time.sleep(30)
                res = continue_small_talk(user_input=user_input)
                # Render the template with the model output
                return render_template('form.html', model_output=res['output'])
        else:
            # Increment index i to move to the next key/column
            i = i + 1
            
            # Check if i is within bounds
            if i <= 5:
                key = columns[i]
            else:
                key = 'Thanks message for giving all information.'
                df.to_csv(csv_file_path, index=False)
            
            time.sleep(20)
            
            # Generate a new input prompt for the next key
            input_prompt = f"""Ask information about {key} to give which is not yet obtained. Don't assume anything. Here, {key} has not been received; you have to ask the user by your expertise to provide this."""
            
            # Invoke the agent_taker to get a response for the new prompt
            res = agent_taker.invoke({"input": input_prompt, "chat_history": chat_history})
            
            # Update chat history with new user and AI messages
            chat_history.extend([HumanMessage(content=input_prompt), AIMessage(content=res["output"]),])
            
            print(res)
            # Render the template with the model output
            return render_template('form.html', model_output=res['output'])
    
    # Render the template with the model output
    return render_template('form.html', model_output=res['output'])

print(obtained)
print(df.head())
if __name__ == '__main__':
    app.run(debug=False)
