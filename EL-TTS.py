
from dotenv import load_dotenv
import os
import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import os


load_dotenv()
voice_id = "7Wpkz223u8UDqBgBSbeZ"
model_id = "eleven_turbo_v2"
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)
def text_to_speech_file(text):
    # Calling the text_to_speech conversion API with detailed parameters
    response = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        optimize_streaming_latency="0",
        output_format="mp3_44100_32",
        voice_settings=VoiceSettings(
            stability=0.3,
            similarity_boost=0.5,
        ),
    )

    save_file_path = "./tts_outputs/output.mp3"

    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{save_file_path}: A new audio file was saved successfully!")
    
    # Return the path of the saved audio file
    return save_file_path


# console input tts
while True:
    text = input("Enter text: ")
    
    os.system(f"start {text_to_speech_file(text)}")
