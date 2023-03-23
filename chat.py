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

def ask_ai():
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    is_running = True
    retry_count = 0
    
    #Restrict the user tries to max. 2 round and then send the message to our support team
    while is_running: 
        query = input("What do you want to ask? ")        
        bot = index.query(query, response_mode="compact")
        
        is_bot_asking_question = "?" in bot.response
        
        if is_bot_asking_question:
            print(bot.response)
            continue
        
        # Get the current date and time
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        print(f'{bot.response}\n\nWas this answer helpful? If yes, please enter "yes" else "no"')    
        
        is_helpful_answer = "yes" in input("Was this answer helpful?: ").lower()
        if is_helpful_answer:
            is_running = False
            retry_count = 0
        else:
            retry_count += 1
        if retry_count >= 2:
            contact_data = input("Please, enter your contact data Name, email:")   
            print("I will send your request to our support team! We will contact you.")

            #Add the input and output to the qa_data list
            qa_data = {'contact_data': contact_data, 'input': query, 'output': bot.response, 'time': now}
            
            # Write the list to a JSON file after the user is done interacting with the AI
            with open("qa_data.json", "w") as f:
                json.dump(qa_data, f)
        
            is_running = False
  
os.environ["OPENAI_API_KEY"] = ""

construct_index("context_data/data")

ask_ai()