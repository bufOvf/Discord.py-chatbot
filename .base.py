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
    if not asleep:
        await client.get_channel(channel_id).send('Mira is awake')
    log(f'Discord bot {client.user} has launched')


@client.event
async def on_message(message):
    global channel_id, admin_id, blacklist, asleep
    if message.channel.id != channel_id or message.author == client.user:
        return
    
    userAllowed = message.author.id not in blacklist
    userAdmin = message.author.id == admin_id
    print(userAllowed, userAdmin)

    if message.content.startswith('$'):

        log(f'Command run: {message.content}')

        if userAllowed:
            if message.content.startswith('$help') and not userAdmin:
                # await message.channel.send('Commands: $help')
                return
        
        if userAdmin: # admin only commands
            # if message.content.startswith('$help'):
            #     await message.channel.send('Commands: $help, $wakeup, $die, $init, $sleep, $update, $reload')

            if message.content.startswith('$wakeup'):
                asleep = False
                await message.channel.send(
                    "{Mira is awake..}"
                )
                log('Mira has been woken up')

            elif message.content.startswith('$init'): #init ai config (new convo and config)
                await initialise_groq(GROQ_API_KEY)   
            
            elif message.content.startswith('$update'): #reload ai config
                try:
                    await update_ai_config()
                except:
                    await message.channel.send('Failed to update AI config')

            elif message.content.startswith('$reload'): #reload discord config
                try:
                    load_and_apply_config()
                except:
                    await message.channel.send('Failed to reload discord config')

            elif message.content.startswith('$sleep'):
                asleep = True
                await message.channel.send('zzzZZ')
                log('Mira has gone to sleep')

            elif message.content.startswith('$die'):
                await message.channel.send('*dies. . .*')
                log('Mira has been killed')
                await client.close()
        else:
            log(f'User ran unknown command: {message.content}')
            # await message.channel.send('Command not found')

    elif not asleep:
        log(f'{message.author.name} said: {message.content}')
        response = await groq_response(message.author.name, message.content)
        await message.channel.send(f'{response}')
        log(f'Mira said: {response}')



if __name__ == "__main__":
    if not load_and_apply_config():
        log('Failed to load configuration. Exiting...')
    else:
        try:
            client.run(TOKEN)
        except Exception as e:
            log(f'Discord bot failed to launch: \n{e}')