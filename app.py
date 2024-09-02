
### IMPORTS 

# External imports
import streamlit as st
from openai import OpenAI
from audiorecorder import audiorecorder


# Python imports
import os
from os import environ
from datetime import datetime
from sys import platform
import hashlib
import random
import hmac

# Imternal imports
from functions import convert_to_mono_and_compress
from transcribe import transcribe_with_whisper_openai
from llm import process_text, process_text_openai
import prompts as p
import config as c
from styling_css import page_config, page_styling


### INITIAL VARIABLES
# Creates folder if they don't exist
os.makedirs("audio", exist_ok=True) # Where audio/video files are stored for transcription
os.makedirs("text", exist_ok=True) # Where transcribed document are beeing stored
os.makedirs("images", exist_ok=True) # Where images are beeing stored


### STYLING - PAGE CONFIG
page_config()
page_styling()


### INITIAL SESSION STATE
# Check and set default values if not set in session_state
# of Streamlit

if "spoken_language" not in st.session_state: # What language source audio is in
    st.session_state["spoken_language"] = "Automatiskt"
if "file_name_converted" not in st.session_state: # Audio file name
    st.session_state["file_name_converted"] = None
if "llm_temperature" not in st.session_state:
    st.session_state["llm_temperature"] = 0.8
if "llm_chat_model" not in st.session_state:
    st.session_state["llm_chat_model"] = "gpt-4o"
if "audio_file" not in st.session_state:
    st.session_state["audio_file"] = False
if "llm_processed" not in st.session_state:
    st.session_state["llm_processed"] = False


# Checking if uploaded or recorded audio file has been transcribed
def compute_file_hash(uploaded_file):

    # Compute the MD5 hash of a file
    hasher = hashlib.md5()
    
    for chunk in iter(lambda: uploaded_file.read(4096), b""):
        hasher.update(chunk)
    uploaded_file.seek(0)  # Reset the file pointer to the beginning
    
    return hasher.hexdigest()


### MAIN APP ###########################

def main():

    global translation
    global model_map_transcribe_model


    ### ### ### ### ### ### ### ### ### ### ###
    ### SIDEBAR

    st.sidebar.header("Inställningar")
    st.sidebar.markdown("")

    # Dropdown menu - choose source language of audio for Whisper model
    spoken_language = st.sidebar.selectbox(
            "Välj språk som talas", 
            ["Automatiskt", "Svenska", "Engelska", "Franska", "Tyska", "Spanska"],
            index=["Automatiskt", "Svenska", "Engelska", "Franska", "Tyska", "Spanska"].index(st.session_state["spoken_language"]),
        )

    model_map_spoken_language = {
            "Automatiskt": None,
            "Svenska": "sv",
            "Engelska": "en",
            "Franska": "fr",
            "Tyska": "de",
            "Spanska": "sp"
        }

    # Update the session_state directly
    st.session_state["spoken_language"] = spoken_language

    st.sidebar.markdown(
        "#"
        )


    ### ### ### ### ### ### ### ### ### ### ###
    ### MAIN PAGE
    
    # Creating two main top columns for header with title
    topcol1, topcol2 = st.columns([2, 2], gap="large")

    with topcol1:

        st.markdown(f"""
            # {c.app_name}
            Tryck på knappen __Spela in__ eller __Skriv text__ här under för att ge feedback. När du är 
            klar trycker du på __Stoppa__ eller __Skicka in__.
            """)
        
    with topcol2:

        st.button("Ny feedback")

    # Creating two main columns
    maincol1, maincol2 = st.columns([2, 2], gap="large")


    with maincol1:

        st.markdown("### Lämna feedback")
        
        # Create three tabs for 'Record', 'Write text' and 'Upload'    
        tab1, tab2, tab3 = st.tabs(["Spela in", "Skriv text", "Ladda upp ljudfil"])

        # TAB 1 - AUDIO RECORDER

        with tab1:

            # Creates the audio recorder
            audio = audiorecorder(start_prompt="Spela in", stop_prompt="Stoppa", pause_prompt="", key=None)

            if len(audio) > 0:

                audio_file_number = random.randint(1000000, 9000000)
                print(audio_file_number)

                # To save audio to a file, use pydub export method
                audio.export(f"audio/{audio_file_number}_recording.wav", format="wav")

                # Open the saved audio file and compute its hash
                with open(f"audio/{audio_file_number}_recording.wav", 'rb') as file:
                    current_file_hash = compute_file_hash(file)

                # If the uploaded file hash is different from the one in session state, reset the state
                if "file_hash" not in st.session_state or st.session_state.file_hash != current_file_hash:
                    st.session_state.file_hash = current_file_hash
                    
                    if "transcribed" in st.session_state:
                        del st.session_state.transcribed

                if "transcribed" not in st.session_state:
                
                    with st.spinner('Din ljudfil är lite stor. Jag ska bara komprimera den lite först...'):
                        st.session_state.file_name_converted = convert_to_mono_and_compress(f"audio/{audio_file_number}_recording.wav", f"{audio_file_number}_recording")
                        st.success('Inspelning komprimerad och klar. Startar transkribering.')

                    with st.spinner('Transkriberar. Det här kan ta ett litet tag beroende på hur lång inspelningen är...'):
                        st.session_state.transcribed = transcribe_with_whisper_openai(st.session_state.file_name_converted, 
                            f"{audio_file_number}_recording.mp3",
                            model_map_spoken_language[st.session_state["spoken_language"]]
                            )

                        st.success('Transkribering klar.')

                        st.balloons()
                        
                
                st.markdown("### Transkrinbering")
                
                if st.session_state.file_name_converted is not None:
                    st.audio(st.session_state.file_name_converted, format='audio/wav')
                
                st.write(st.session_state.transcribed)


        # TAB 2 - TEXT INPUT AREA

        with tab2:

            with st.form("send_feedback"):
                feedback_text = st.text_area("Feedback", label_visibility="hidden")
                st.form_submit_button('Skicka feedback')

                if feedback_text:
                    st.session_state.transcribed = feedback_text
        
        
        # TAB 3 - FILE UPLOADER 

        with tab3:
            
            uploaded_file = st.file_uploader(
                "Ladda upp din ljud- eller videofil här",
                type=["mp3", "wav", "flac", "mp4", "m4a", "aifc"],
                help="Max 10GB stora filer", label_visibility="collapsed",
                )


            if uploaded_file:

                # Checks if uploaded file has already been transcribed
                current_file_hash = compute_file_hash(uploaded_file)

                # If the uploaded file hash is different from the one in session state, reset the state
                if "file_hash" not in st.session_state or st.session_state.file_hash != current_file_hash:
                    st.session_state.file_hash = current_file_hash
                    
                    if "transcribed" in st.session_state:
                        del st.session_state.transcribed

                
                # If audio has not been transcribed
                if "transcribed" not in st.session_state: 

                    # Sends audio to be converted to mp3 and compressed
                    with st.spinner('Din ljudfil är lite stor. Jag ska bara komprimera den lite först...'):
                        st.session_state.file_name_converted = convert_to_mono_and_compress(uploaded_file, uploaded_file.name)
                        st.success('Inspelning komprimerad och klar. Startar transkribering.')

                # Transcribes audio with Whisper
                    with st.spinner('Transkriberar. Det här kan ta ett litet tag beroende på hur lång inspelningen är...'):
                        st.session_state.transcribed = transcribe_with_whisper_openai(st.session_state.file_name_converted, 
                            uploaded_file.name,
                            model_map_spoken_language[st.session_state["spoken_language"]])
                        st.success('Transkribering klar.')

                        st.balloons()

                
                st.markdown("### Ladda upp din bikt")
                
                if st.session_state.file_name_converted is not None:
                    st.audio(st.session_state.file_name_converted, format='audio/wav')
                
                st.write(st.session_state.transcribed)

            

    with maincol2:

        st.markdown("### Sammanställning")

        if "transcribed" in st.session_state:

            system_prompt = p.sammanstallning_bikt_1
            full_response = ""

            butcol1, butcol2, butcol3, butcol4 = st.columns(4, gap="small")

            with butcol1:
                with st.popover("Visa prompt"):
                    st.write(system_prompt)
                
            llm_model = st.session_state["llm_chat_model"]
            llm_temp = st.session_state["llm_temperature"]
            
            if "llama" in llm_model:
                full_response = process_text(llm_model, llm_temp, system_prompt, st.session_state.transcribed)
                #st.session_state.llm_processed = True
            else:
                full_response = process_text_openai(llm_model, llm_temp, system_prompt, st.session_state.transcribed)
                #st.session_state.llm_processed = True
                #print(st.session_state.llm_processed)


            with butcol2:
                with st.popover("Redigera"):
                    st.text_area("Redigera", full_response, height=400)


if __name__ == "__main__":
    main()



