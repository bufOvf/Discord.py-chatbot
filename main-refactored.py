from dotenv import load_dotenv
import discord
import os 
import json
from ai import initialise_groq, groq_response, update_ai_config, log


# bot permissions: administrator

# load configs
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)



def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

def load_and_apply_config():
    global channel_id, admin_id, blacklist, asleep
    try:
        config = load_config()
        channel_id = config['CHANNEL_ID']
        admin_id = config['ADMIN_ID']
        blacklist = config.get('blacklist', [])
        asleep = config.get('asleep', False)
        log('Config loaded successfully')
    except Exception as e:
        log(f'Failed to load config: {e}')
        return False
    return True


@client.event
async def on_ready():
    await initialise_groq(GROQ_API_KEY)
    # client.loop.create_task(console_listener())
    if not asleep:
        await client.get_channel(channel_id[1]).send('Mira is back')
    log(f'Discord bot {client.user} has launched')


@client.event
async def on_message(message):
    global channel_id, admin_id, blacklist, asleep
    userAllowed = message.author.id not in blacklist
    userAdmin = message.author.id == admin_id

    if message.channel.id not in channel_id or message.author == client.user or not userAllowed:
        return
    
    if message.content.startswith('$'):
        log(f'{message.author.name} ran command: {message.content}')
        try:    
            await commands[message.content](message)
        except:
            return
    else:
        await send_message(message)

async def command_help(message):
    await message.channel.send('{Commands: $help, $wakeup, $init, $update, $reload, $sleep, $die}')

async def command_wakeup(message):
    global asleep
    asleep = False
    await message.channel.send('{Mira is awake..}')

async def command_init(message):
    log(f'Initialising groq {message.author.name}')
    await initialise_groq(GROQ_API_KEY)

async def command_update(message):
    if await update_ai_config():
        await message.channel.send('AI config updated')

async def command_reload(message):
    await message.channel.send('Reloading discord config')
    load_and_apply_config()
    
async def command_sleep(message):
    global asleep
    asleep = True
    await message.channel.send('{Mira is sleeping..}')

async def command_die(message):
    await message.channel.send('{Mira has left..}')
    log('Discord bot killed')
    await client.close()

async def send_message(message):
    if not asleep:
        await message.channel.send(
            await groq_response(message.author.name, message.content)
            )

async def console_listener():
    while True:
        console_prompt = input('> ')
        if console_prompt == 'exit':
            break
        else:
            response = await groq_response('system', console_prompt)
            print(response)



commands = {
      '$help': command_help,
      '$wakeup': command_wakeup,
      '$init': command_init,
      '$update': command_update,
      '$reload': command_reload,
      '$sleep': command_sleep,
      '$die': command_die
  }

if __name__ == "__main__":

    if not load_and_apply_config():
        log('Failed to load configuration. Exiting...')
    else:
        try:
            client.run(TOKEN)
        except Exception as e:
            log(f'Discord bot failed to launch: \n{e}')


