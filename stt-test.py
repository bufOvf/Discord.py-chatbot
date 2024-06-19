import os
import time
import speech_recognition as sr
from TTS.api import TTS

model_list = TTS.list_models()
print(model_list)

recognizer = sr.Recognizer()

# Initialize TTS with a pre-trained model
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True, gpu=False)

def llm_response(text):
    # Dummy LLM response function; replace with actual LLM API call
    return f"Response to: {text}"

def listen_and_respond():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)  # Adjust to ambient noise level
        print("Listening...")

        while True:
            try:
                print("Waiting for speech...")
                audio = recognizer.listen(source, timeout=None)
                print("Processing...")

                # Try to recognize the speech in the recording
                text = recognizer.recognize_google(audio)
                print(f"Transcribed: {text}")

                response = llm_response(text)
                print(f"LLM Response: {response}")
                tts_response(response)
            except sr.WaitTimeoutError:
                print("Timeout; waiting for more speech.")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

def tts_response(text):
    tts.tts_to_file(text=text, file_path="response.wav")
    play_audio("response.wav")

def play_audio(filename):
    os.system(f"start {filename}")  # Use "afplay {filename}" on macOS or "aplay {filename}" on Linux

if __name__ == "__main__":
    listen_and_respond()
