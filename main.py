# from urllib import response
from dotenv import load_dotenv
import discord
import os 
import json
from ai import initialise_groq, groq_response, reload_ai_config, log, send_system_message
# from ttsmodule import initialise_tts, text_to_speech, reload_tts_config
from datetime import datetime



# bot permissions: administrator

# load configs
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TOKEN = os.getenv("TOKEN")


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
# give bot a nickname



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
    client.user.global_name = 'Mira'
    ready_channel = client.get_channel(channel_id[1])
    await initialise_groq(GROQ_API_KEY)
    # client.loop.create_task(console_listener())

    

    if not asleep:
        await ready_channel.send('{Mira is online... }')
        # messages_context = [message async for message in ready_channel.history(limit=5)]
        # messages_context = [f'[{message.author.nick}: {message.content}],' if message.author.nick else f'[Mira: {message.content}],' for message in messages_context]
        # messages_context = 'PREVIOUS MESSAGES: \n{'+'\n'.join(messages_context)+'}'
        # await send_system_message(messages_context)

    log(f'Discord bot {client.user} has launched')


@client.event
async def on_message(message):
    global channel_id, admin_id, blacklist, asleep
    userAllowed = message.author.id not in blacklist
    userAdmin = message.author.id == admin_id

    if message.channel.id not in channel_id or message.author == client.user or not userAllowed:
        return
    
    if message.content.startswith('!'):
        log(f'{message.author.name} ran command: {message.content}')
        try:    
            await commands[message.content](message)
        except Exception as e:
            log(f'Error in command: {e}')
    else:
        await send_message(message)

async def command_help(message):
    await message.channel.send('`Commands: !help, !wakeup, !init, !reloadai, !reloaddiscord, !reloadtts, !sleep, !die, !join}`')

async def command_wakeup(message):
    global asleep
    asleep = False
    await message.channel.send('`Mira is awake..`')

async def command_init(message):
    log(f'Initialising groq {message.author.name}')
    await initialise_groq(GROQ_API_KEY)

async def command_reloadai(message):
    if await reload_ai_config():
        await message.channel.send('`AI config updated`')

async def command_reloaddiscord(message):
    if await reload_tts_config():
        await message.channel.send('`Discord config updated`')
    load_and_apply_config()
    
async def command_sleep(message):
    global asleep
    asleep = True
    await message.channel.send('`Mira is sleeping..`')

async def command_die(message):
    await message.channel.send('`Mira has left..`')
    log('Discord bot killed')
    await client.close()

async def send_message(message):
    metadata = {
        'time': datetime.now().strftime("%H:%M"),
        'date': datetime.now().strftime("%Y-%m-%d"),       
    }
    if not asleep:
        response = await groq_response(message.author.name, message.content, metadata)
        await message.channel.send(response)
        # if message.author.voice:
        # await text_to_speech(response)

async def console_listener():
    while True:
        console_prompt = input('> ')
        if console_prompt == 'exit':
            break
        else:
            response = await groq_response('system', console_prompt)
            print(response)


# voice channel stuff
async def command_reloadtts(message):
    if await reload_tts_config():
        await message.channel.send('`TTS config updated`')
    else:
        await message.channel.send('`TTS config failed to update`')


async def command_joinvc(message):
    log(f'Joining voice channel "{message.author.voice.channel.name}"')
    await message.author.voice.channel.connect()
    log(f'Joined voice channel "{message.author.voice.channel.name}"')
    await message.channel.send(f'Joined "{message.author.voice.channel.name}"')

async def command_leavevc(message):
    log(f'Leaving voice channel "{message.author.voice.channel.name}"')
    await message.author.voice.channel.disconnect()
    log(f'Left voice channel "{message.author.voice.channel.name}"')
    await message.channel.send(f'Left "{message.author.voice.channel.name}"')

async def play_tts(message):
    # if message.author.voice:
    #     voice = message.guild.voice_client
    #     if voice.is_playing():
    #         voice.stop()
    #     filename = await text_to_speech(message.content)
    #     voice.play(discord.FFmpegPCMAudio(filename))
    pass
    


commands = {
      '!help': command_help,
      '!wakeup': command_wakeup,
      '!init': command_init,
      '!reloadai': command_reloadai,
      '!reloaddiscord': command_reloaddiscord,
      '!reloadtts': command_reloadtts,
      '!sleep': command_sleep,
      '!join': command_joinvc,
      '!leave': command_leavevc,
      '!die': command_die,
  }




if __name__ == "__main__":

    if not load_and_apply_config():
        log('Failed to load configuration. Exiting...')
    else:
        try:
            client.run(TOKEN)
        except Exception as e:
            log(f'Discord bot failed to launch: \n{e}')


