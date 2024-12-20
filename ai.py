from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
import json
from datetime import datetime
import logging
import asyncio


def log(message: str):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {message}')

def load_ai_config():
    try:
        with open('config.json', 'r') as config_file:
            return json.load(config_file)
    except Exception as e:  
        log(f'load_ai_config: Error loading config: \n{e}')

async def reload_ai_config():
    global system_message, verbose
    try: 
        config = load_ai_config()
        system_message = config['system_message']
        verbose = config['verbose']
        log(f'reload_ai_config: Updated config: {config["system_message"], config["verbose"]}')
        return True
    except Exception as e:
        log(f'reload_ai_config: Error updating config: \n{e}')
        return False

async def initialise_groq(GROQ_API_KEY): #init groq/reload config
    log('debug: initialise_groq: Initialising groq')
    global system_message, memory_length, groq_client, chat_history, memory, verbose, max_tokens

    # load initial ai config
    config = load_ai_config()
    
    system_message = config['system_message']
    model = config['model']
    temperature = config['temperature']
    top_p = config['top_p']
    memory_length = config['memory_length']
    verbose = config['verbose']
    max_tokens = config['max_tokens']
    log(f'debug: loaded config')
    # init system prompt
    system_prompt = {
        "role": "system",
        "content": system_message
    }
    # print(f'initialise_groq: "{GROQ_API_KEY[:5]}..."')

    groq_client = ChatGroq(
        api_key=GROQ_API_KEY,
        model=model,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
    )

    chat_history = [system_prompt]
    memory = ConversationBufferWindowMemory(
        k=memory_length, 
        memory_key="chat_history", 
        return_messages=True,
    )

    print('Groq client initialised')

async def groq_response(username, message, metadata):
    log(f'{username} said {message}')
    if message:
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=system_message
                ),
                MessagesPlaceholder(
                    variable_name="chat_history"
                ),
                HumanMessagePromptTemplate.from_template(
                    "{human_input}"
                ),
                SystemMessage(
                    content=f'Metadata: {json.dumps(metadata)}'
                ),
            ]
        )
    
    # Conversation chain
    conversation = LLMChain(
        llm=groq_client,
        prompt=prompt,
        verbose=verbose,
        memory=memory,
    )
    try:
        response = conversation.predict(
            human_input=f'{username} said {message}',
        )
        log(f'Mira said: {response}')
        
    except Exception as e:
        print('Error: ', e)
        response = '{response failed}'
    
    asyncio.create_task(memory_to_file(response))
    return response

async def send_system_message(message):
    log(f'sending system message: {message}')
    if message:
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=system_message
                ),
                MessagesPlaceholder(
                    variable_name="chat_history"
                ),
                SystemMessage(
                    content=message
                ),
            ]
        )
        
    conversation = LLMChain(
        llm=groq_client,
        prompt=prompt,
        verbose=verbose,
        memory=memory,
        )  
     
    try:
        response = conversation.predict()
        log(f'Mira said: {response}')
        return response
    except Exception as e:
        print('Error: ', e)
        response = '{response failed}'
    
async def memory_to_file(response): # prototype implementation of saving memory
    if '<|start_memory|>' in response:
        memory = response.split('<|start_memory|>')[1].split('<|end_memory|>')[0]
        with open('ignore/memory.txt', 'a') as memory_file:
            memory_file.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M")}: {memory}\n')
    else:
        return None