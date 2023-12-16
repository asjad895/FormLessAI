from flask import Flask, render_template, request,jsonify,json
from networkx import dfs_labeled_edges
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
#_____________________________________________________________________________________________________________________________
open_ai_key = os.environ.get("OPENAI_API_KEY")
app = Flask(__name__)
#__________________________________________________________________________________________________________________________
#Initiation Agent prompt
input1="Write message according to your specilaity. dont include {key} words instead include any engaging words"
#User Data Store
#Step 4. Details to extract: Name, email, phone no, Address, Date of birth, Education.
columns = ['DOB', 'Name', 'Email', 'Mob No', "Batchler's degree", 'Skills']
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
username='Demo'
csv_file_path = f"./extracted_data/user_{username}_{current_time}_data.csv"
df = pd.DataFrame(columns=columns)
# df.to_csv(csv_file_path,index=False)
#________________________________________________________________________________________________________________________________ 
#Step 3.Design a coherent conversation flow where users will easily give the information or convince well to give their info.
# ● If the user is hesitant then initiate small talk and later circle back to the question regarding their personal informatio
def analze_user_input(user_input,key,df):
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
        extract_information(user_input=user_input,key=key,df=df)

def detect_hesitancy(user_input):
    """function to detect hesitancy in user input.
    """
    print("Checking User hesitency.")
    hesitancy_keywords = ["not sure", "maybe", "I don't know", "hesitant","why","who",'dont','no','not',
                          "don't","can u","can","help"]
    return any(keyword in user_input.lower().split() for keyword in hesitancy_keywords)

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
def extract_information(user_input,key,df):
    """
    function to Extract structered information using Extarction agent and saved it..
    """
    # Call the function from your original implementation
    print("Extracting.......(Extraction Agent)")
    inputs=f"{user_input}"+f"is my {key}"
    input_text = f"""Please extract {key} information from the user input description: {inputs}.
    Take your time and ensure accuracy. If the information is not found, politely apologize for any inconvenience.
    """
    ex_out=agent_ex.invoke({'input':input_text,'chat_history':chat_history})
    chat_history.extend([HumanMessage(content=user_input),AIMessage(content=ex_out["output"]),])
    if 'orry' in ex_out["output"] or 'Apoligy' in ex_out["output"]:
        print(ex_out['output'])
    else:
        df[key]=ex_out['output']
        print("key",key)
        print(df.head())
        with open('user_data.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            output_dict = json.loads(ex_out['output'])
            writer.writerow(output_dict.keys())
            writer.writerow(output_dict.values())
            writer.writerow("------------------------------")
            print(output_dict)
            print("Saved.")
            # df.to_csv('user_data.csv',index=False)

def continue_small_talk(user_input):
    """
    function to continue small talk if confidence is not yet built.
    """
    # follow-up small talk response
    #Continue discussing topics related to the user's interests
    user_input = user_input
    print("not going for analyzing,user not in confidence just chatting(Convincing Agent)")
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
    print("got_confidence.......(Taker Agent)")
    input_prompt=f"""Ask information about {key} to give which is not yet obtained.dont assume anything ,here 
    {key} yet not  recived u have to ask to user by your expertises to give this.
    Dont repeat same question."""
    res=agent_taker.invoke({"input": input_prompt,"chat_history":chat_history})
    chat_history.extend([HumanMessage(content=input_prompt),AIMessage(content=res["output"]),])
    return res["output"]
  
#Running InitiationAgent for initiating conversation
# response=agent_ini.invoke({"input":input1,"chat_history": chat_history })
# chat_history.extend([HumanMessage(content=input1),AIMessage(content=response["output"]),])
# print("Going forward.....")
# print(response)
def welcome_ini(agent=agent_ini,chat_history=chat_history):
    """write welcome message by Initiator agent

    Args:
        agent (_type_, optional):Agent. Defaults to agent_ini.
        chat_history (_type_, optional):variable for storing chat_history collaboratively. Defaults to chat_history.

    Returns:
        _type_: str
    """
    print("calling initiater(Initialization Agent)")
    response=agent_ini.invoke({"input":input1,"chat_history": chat_history })
    chat_history.extend([HumanMessage(content=input1),AIMessage(content=response["output"]),])
    print("Going forward.....")
    print(response)
    return response["output"]
    
    
#_______________________________________________________________________________________________________________________
#App Logic,url managemnet,client server mmanagment
@app.route('/', methods=['GET'])
def home():
    response=welcome_ini()
    return render_template('app.html', model_output=response)

i=0
conf=True
@app.route('/Form', methods=['GET', 'POST'])
def FormlessAI(df=df):
    # Initialize variables
    global i
    key = columns[i]
    global conf 
    input_prompt = f"please Ask information about {key} which is not yet obtained,in your expertise"
    
    # Invoke the agent_taker to get a response
    res1 = agent_taker.invoke({"input": input_prompt, "chat_history": chat_history})
    
    # Update chat history with user and AI messages
    chat_history.extend([HumanMessage(content=input_prompt), AIMessage(content=res1["output"]),])
    
    # Check if the request method is POST
    if request.method == 'POST':
        # Get user input from the form
        user_input = request.form['user_input']
        print(user_input)
        
        # Analyze user input and obtain the result
        resa=None
        if conf!=False:
            resa = analze_user_input(user_input=user_input, key=key,df=df)
        time.sleep(25)
        
        # Check if the resa is not None(means hesitating,else agent is able to extract information)
        if resa is not None:
            conf = False
            # Render the template with the model output
            return render_template('form.html', model_output=resa)
        elif conf == False:
            # After small talk, check if confidence is built
            if is_confidence_built(user_input):
                print("confidence.....")
                # Call the function to handle the next information request
                conf = True
                time.sleep(25)
                res = got_confidence(key=key)
                return render_template('form.html', model_output=res)
            else:
                # Continue with more small talk or handle accordingly
                time.sleep(30)
                res = continue_small_talk(user_input=user_input)
                # Render the template with the model output
                return render_template('form.html', model_output=res)
        else:
            # Increment index i to move to the next key/column
            i = i + 1
            print("iteration ",i)
            
            # Check if i is within boundss
            if i <= 5:
                key = columns[i]
            else:
                key = 'Thanks message for giving all information.'
                df.to_csv(csv_file_path, index=False)
                print(df.head())
            
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
    return render_template('form.html', model_output=res1['output'])

print(df.head())
if __name__ == '__main__':
    app.run(debug=False)
