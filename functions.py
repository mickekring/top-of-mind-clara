
### Functions

import streamlit as st
from pydub import AudioSegment
import os


def convert_to_mono_and_compress(uploaded_file, file_name, target_size_MB=23, max_iterations=5):

    print("\nSTART: Converting audio to mp3")

    global file_name_converted

    # Load the audio file once
    try:
        audio = AudioSegment.from_file(uploaded_file)
    except Exception as e:
        print(f"Error loading audio file: {e}")
        return None

    # Convert to mono
    audio = audio.set_channels(1)

    # Calculate initial target bitrate to achieve the desired file size (in bits per second)
    duration_seconds = len(audio) / 1000.0  # pydub works in milliseconds
    target_bitrate = int((target_size_MB * 1024 * 1024 * 8) / duration_seconds)

    # Ensure the bitrate is within a reasonable range
    target_bitrate = max(32, min(target_bitrate, 64))  # Limiting to reasonable MP3 bitrates

    # Function to check the file size
    def get_file_size(file_path):
        return os.path.getsize(file_path) / (1024 * 1024)  # size in MB

    output_path = f"audio/{file_name}.mp3"
    iterations = 0

    # Compress the audio file with iterative bitrate adjustment
    while iterations < max_iterations:
        print(f"Iteration {iterations + 1}: Trying with bitrate {target_bitrate}k")
        try:
            audio.export(output_path, format="mp3", bitrate=f"{target_bitrate}k")
            file_size_MB = get_file_size(output_path)
            print(f"Exported file size: {file_size_MB} MB")
            
            if file_size_MB <= target_size_MB:
                file_name_converted = output_path
                print("DONE: Converting audio to mp3")
                return file_name_converted
            else:
                print(f"File size {file_size_MB} MB exceeds target {target_size_MB} MB, reducing bitrate")
                target_bitrate = int(target_bitrate * (target_size_MB / file_size_MB * 0.9))  # Reduce more significantly
                print(f"New target bitrate: {target_bitrate}k")
                target_bitrate = max(16, target_bitrate)  # Ensure bitrate does not go below 32 kbps

        except Exception as e:
            print(f"Error during audio export: {e}")
            return None
        
        iterations += 1

    print(f"Failed to compress audio to under {target_size_MB} MB after {max_iterations} iterations")
    return None
