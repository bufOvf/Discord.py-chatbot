from dotenv import load_dotenv
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


def log(message: str):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {message}')

def load_ai_config():
    try:
        with open('config.json', 'r') as config_file:
            return json.load(config_file)
    except Exception as e:  
        log(f'load_ai_config: Error loading config: \n{e}')

async def update_ai_config():
    global system_message, verbose
    try: 
        config = load_ai_config()
        system_message = config['system_message']
        verbose = config['verbose']
        log(f'update_ai_config: Updated config: {config["system_message"], config["verbose"]}')
    except Exception as e:
        log(f'update_ai_config: Error updating config: \n{e}')

async def initialise_groq(GROQ_API_KEY): #init groq/reload config
    log('debug: initialise_groq: Initialising groq')
    global system_message, memory_length, groq_client, chat_history, memory, verbose

    # load initial ai config
    config = load_ai_config()
    
    system_message = config['system_message']
    model = config['model']
    temperature = config['temperature']
    top_p = config['top_p']
    memory_length = config['memory_length']
    verbose = config['verbose']
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
    )
    chat_history = [system_prompt]

    memory = ConversationBufferWindowMemory(k=memory_length, memory_key="chat_history", return_messages=True)
    print('Groq client initialised')

async def groq_response(username, user_message):
    log(f'{username} said {user_message}')
    if user_message:
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
            human_input= username + " said " + user_message
        )
        log(f'Mira said: {response}')
        return response
    except Exception as e:
        print('Error: ', e)
        response = '{response failed}'
        return response