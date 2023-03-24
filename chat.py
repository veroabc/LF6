import json
from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI
import sys
import os
from IPython.display import Markdown, display
from datetime import datetime


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


def format_log(message: str, is_bot: bool = False):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    source = "BOT" if is_bot else "USER"
    return {
        'sent': now,
        'content': message,
        'source': source
    }

def ask_ai():
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    is_running = True
    retry_count = 0
    
    log_json = {
        'messages': [],
        'contact_data': None
    }
    
    #Restrict the user tries to max. 2 round and then send the message to our support team
    while is_running: 
        query = input("What do you want to ask? ")        
        log_json["messages"].append(format_log(query))

        bot = index.query(query, response_mode="compact")
        
        is_bot_asking_question = "?" in bot.response
        
        if is_bot_asking_question:
            print(bot.response)
            log_json["messages"].append(format_log(bot.response, True))
            continue
        
        # Get the current date and time
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = f'{bot.response}\n\nWas this answer helpful? If yes, please enter "yes" and you exit, else "no" or "send" to send the request to our support team'
        
        print(response)
        log_json["messages"].append(format_log(bot.response, True))  
        
        #buid some kind of function "send the question to support"
        is_helpful_answer = "send"
        is_helpful_answer = "yes" in input("Was this answer helpful?: ").lower()
        if is_helpful_answer:
            is_running = False
            retry_count = 0
        else:
            retry_count += 1
        if retry_count >= 2:
            contact_data = input("Please, enter your contact data Name, Email:")
            bot_contact_text = "I will send your request to our support team! We will contact you as soon as possible."
            print(bot_contact_text)

            #Add the input and output to the qa_data list
            log_json["contact_data"] = contact_data
        
            is_running = False

    with open("qa_data.json", "w") as f:
        json.dump(log_json, f)
  
os.environ["OPENAI_API_KEY"] = ""

construct_index("context_data/data")

ask_ai()