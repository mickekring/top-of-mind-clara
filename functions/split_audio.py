
from pydub import AudioSegment
import math

def split_audio_to_chunks(audio_file_number, audio_path, max_chunk_length=10*60*1000):
    # Load the audio file
    audio = AudioSegment.from_file(audio_path)

    # Calculate the number of chunks
    num_chunks = math.ceil(len(audio) / max_chunk_length)

    chunk_paths = []

    # Split the audio into fixed-length chunks
    for i in range(num_chunks):
        
        start_time = i * max_chunk_length
        end_time = min((i + 1) * max_chunk_length, len(audio))
        chunk = audio[start_time:end_time]
        
        # Save the chunk as MP3 (instead of WAV)
        output_path = f"data/audio/audio_chunks/{audio_file_number}_output_chunk_{i}.mp3"
        chunk.export(output_path, format="mp3", bitrate="16k")
        #print(f"Saved {output_path} as MP3")
        chunk_paths.append(output_path)

    return chunk_paths

