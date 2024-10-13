
### Transcribe

import streamlit as st
from openai import OpenAI
from os import environ
import config as c

if c.run_mode == "local":
	client = OpenAI(api_key = st.secrets.openai_key)
else:
	client = OpenAI(api_key = environ.get("openai_key"))


# Whisper OpenAI

def transcribe_with_whisper_openai(file, file_name):

	#audio_file = open(file, "rb")
	transcription = client.audio.transcriptions.create(
		model = "whisper-1", 
		file = file, 
		response_format = "text",
		prompt = ""
	)

	transcribed_content = transcription

	with open('text/' + file_name + '.txt', 'w') as file:
		# Write the string to the file
		file.write(transcribed_content)

	return transcribed_content
