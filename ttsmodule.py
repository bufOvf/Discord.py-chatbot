import glob
import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import json

load_dotenv()

# Set up the subscription info for the Speech Service:
subscription_key = os.getenv("AZURE_KEY")
service_region = os.getenv("AZURE_REGION")

speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)


def get_config():
    with open('tts-config.json', 'r') as f:
        config = json.load(f)
    return config

async def reload_tts_config(): 
    global voice_name, pitch, rate, volume, voice_style
    try:
        config = get_config()
        voice_name = config['voice_name']
        pitch = config['pitch']
        rate = config['rate']
        volume = config['volume']
        voice_style = config['voice_style']
        return True
    except Exception as e:
        print(f"Error reloading config: {e}")
        return False

async def initialise_tts():
    await reload_tts_config()
    return True

async def text_to_speech(text):
    speech_config.speech_synthesis_voice_name = voice_name
    
    ssml_string = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang='en-US'>
        <voice name='en-US-AriaNeural'>
            <mstts:express-as style="{voice_style}">
            <prosody pitch='{pitch}' rate='{rate}' volume='{volume}'>
                {text}
            </prosody>
            </mstts:express-as>
        </voice>
    </speak>
    """
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, 
        audio_config=audio_config)
    
    result = speech_synthesizer.speak_ssml_async(ssml_string).get()

    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized: [{text}]")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")