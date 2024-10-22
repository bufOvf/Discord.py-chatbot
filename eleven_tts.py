from dotenv import load_dotenv
import os
import json
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def load_tts_config():
    try:
        with open('tts_config.json', 'r') as config_file:
            return json.load(config_file)
    except Exception as e:
        print(f"load_tts_config: Error loading config: \n{e}")
        return None

def reload_tts_config():
    global voice_id, model_id
    try:
        config = load_tts_config()
        voice_id = config['voice_id_mira']
        model_id = config['model_id']
        print('TTS config loaded successfully')
        return True
    except Exception as e:
        print(f'Failed to load TTS config: {e}')
        return False

def text_to_speech_file(text):
    try:
        response = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            optimize_streaming_latency="3",
            output_format="mp3_44100_64",
            voice_settings=VoiceSettings(
                stability=0.3,
                similarity_boost=0.5,
            ),
        )
        save_file_path = "./tts_outputs/output.mp3"
        with open(save_file_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)
        print(f"{save_file_path}: A new audio file was saved successfully!")
        return save_file_path
    except Exception as e:
        print(f"Error in text_to_speech_file: {e}")
        return None

# Load configuration at startup
if not reload_tts_config():
    raise ValueError("Failed to load TTS configuration. Check tts_config.json file.")

# # Console input TTS
# while True:
#     text = input("Enter text: ")
#     os.system(f"start {text_to_speech_file(text)}")