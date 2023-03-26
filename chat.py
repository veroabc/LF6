import json
from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI
import sys
import os
from IPython.display import Markdown, display
from datetime import datetime

import send_rq


def construct_index(directory_path):
    # set maximum input size
    max_input_size = 4096
    # set number of output tokens
    num_outputs = 2000
    # set maximum chunk overlap
    max_chunk_overlap = 20
    # set chunk size limit
    chunk_size_limit = 600 

    # define LLM
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.5, model_name="text-davinci-003", max_tokens=num_outputs))
    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)
 
    documents = SimpleDirectoryReader(directory_path).load_data()
    
    index = GPTSimpleVectorIndex(
        documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper
    )

    index.save_to_disk('index.json')

    return index

# Definition of date, content and source to place tha data in json file
# Represents a chat message in our json.
def format_log(message: str, is_bot: bool = False):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    source = "BOT" if is_bot else "USER"
    return {
        'sent': now,
        'content': message,
        'source': source
    }
    
# Connection with open_ai
def ask_ai():
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    is_running = True
    
    # Holds our chat logs to be later dumpped into our .json file.
    log_json = {
        'messages': [],
        'contact_data': None  # Retrieving that data later.
    }
    
    # Use this method to get the user input. 
    # This way we ensure all input is getting written to our chat log.
    def get_user_input(display_text = ""):
        user_input = input(display_text)
        log_json["messages"].append(format_log(user_input))
        return user_input
    
    def display_bot_response(text):
        print(text)
        log_json["messages"].append(format_log(text, is_bot=True))
    
    while is_running: 
        query = get_user_input("What do you want to ask? ")        

        bot = index.query(query, response_mode="compact")
        
        # Checking this, because the following flow would not make sense
        # otherwise.
        is_bot_asking_question = "?" in bot.response
        
        if is_bot_asking_question:
            display_bot_response(bot.response)
            continue
        
        display_bot_response(f'{bot.response}\n\Was the problem solved? If yes, please enter "yes" and you exit, else "no". ')
        
        # Get the responce from user if it is "yes" -> exit or "no" -> continue   
        is_helpful_answer = "yes" in get_user_input("Was this answer helpful?:").lower()
        if is_helpful_answer:
            is_running = False
            continue
        
        # Get more information about the problem
        problem_description = get_user_input("Describe the problem further:")
        bot = index.query(problem_description, response_mode="compact")
        display_bot_response(f'{bot.response}\n\Was the problem solved? If yes, please enter "yes" and you exit, else "no" and I will send the problem to our support team. ')
        
        user_input = get_user_input("Was this answer helpful?:")
        
        # Guessing that user did not understand our instructions and asking him again to answer with yes or no.
        if len(user_input) > 10:
            display_bot_response("This seems like a long response. Was this answer helpful? Type 'yes' or 'no'.")
            user_input = get_user_input("Was this answer helpful?:")
            
        is_helpful_answer = "yes" in user_input.lower()
        if is_helpful_answer:
            is_running = False
            continue
    
        contact_data = get_user_input("Please, enter your contact data: Name, Email: ")
        display_bot_response("I will send your request to our support team! We will contact you as soon as possible.")

        # Add the input and output to the qa_data list and send the same date using gmail accout(in the extended version it could be a server  or vm.)
        log_json["contact_data"] = contact_data
    
        send_rq.send_email(subject="Support request from Chatbot", body="New support request:" + json.dumps(log_json, indent = 4))
        is_running = False
        
# Write our chatlog to jsan file
    with open("qa_data.json", "w") as f:
        json.dump(log_json, f)

#the data will be stored in separated file to secure the user data  
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

construct_index("context_data/data")

ask_ai()