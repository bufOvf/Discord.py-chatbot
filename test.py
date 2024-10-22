import os
import pygame

def test_audio_playback():
    # Set the path to the audio file
    audio_file = "./tts_outputs/output.mp3"
    
    # Check if the file exists
    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found at {audio_file}")
        return

    print(f"Audio file found at: {os.path.abspath(audio_file)}")

    try:
        # Initialize pygame mixer
        pygame.mixer.init()

        # Load the audio file
        pygame.mixer.music.load(audio_file)

        # Play the audio
        print("Attempting to play audio...")
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        print("Audio playback completed successfully")

    except Exception as e:
        print(f"Error during audio playback: {e}")

    finally:
        # Clean up
        pygame.mixer.quit()

if __name__ == "__main__":
    test_audio_playback()