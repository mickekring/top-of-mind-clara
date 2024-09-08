
### IMPORTS 

# External imports
import streamlit as st
from openai import OpenAI
from audiorecorder import audiorecorder
from supabase import create_client, Client

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
os.makedirs("images", exist_ok=True) # Where images are beeing stored

# Initialize Supabase client
if c.run_mode == "local":
    SUPABASE_URL = st.secrets.supabase_db_url
    SUPABASE_KEY = st.secrets.supabase_db_api
else:
    SUPABASE_URL =  environ.get("supabase_db_url")
    SUPABASE_KEY =  environ.get("supabase_db_api")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Temp variables - to be removed

dashboard_id = c.dashboard_id


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
if "feedback_submitted" not in st.session_state:
    st.session_state["feedback_submitted"] = True


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

    # MENU

    st.sidebar.markdown("## FeedbackFabriken")

    st.sidebar.page_link("app.py", label="Feedback", icon=":material/home:")
    st.sidebar.page_link("pages/10Dashboard.py", label="Dashboard", icon=":material/dashboard:")

    st.sidebar.markdown("# ")
    st.sidebar.markdown("# ")
    st.sidebar.markdown("# ")
    st.sidebar.markdown("### :material/settings: Inställningar")
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
    
    st.sidebar.markdown(f"""
            __Version:__ {c.app_version}  
            __Senast uppdaterad:__ {c.app_updated_date}       
                        """)


    ### ### ### ### ### ### ### ### ### ### ###
    ### MAIN PAGE
    
    # Creating two main top columns for header with title
    topcol1, topcol2 = st.columns([2, 2], gap="large")

    with topcol1:

        st.title(":material/dashboard: FeedbackFabriken")
              

    # Creating two main columns
    maincol1, maincol2 = st.columns([2, 2], gap="large")

    
    with maincol1:

        with st.container(border = True):

            st.markdown(f"""Tack för att du vill dela med dig av vad du tycker, tänker och känner!  
                    Allt du skickar in är anonymt.  
            """)
            st.markdown(f"""  
            Välj om du vill __Tala__ eller __Skriva__ här under för att ge feedback.
            """)

        with st.expander("Hjälp och tips"):
            st.markdown(f"""#### Tips på hur du kan ge feedback
- Försök att vara så specifik som du kan. Om det är något som du gillar eller inte gillar, 
berätta vad det är och varför.  
- Kom gärna med förslag. Om du exempelvis har något som du inte tycker fungerar, kom gärna med ett 
förslag på hur det skulle kunna lösas. Du som jobbar närmast problemet, vet oftast mest och bäst.
""")

        with st.container(border = True):

            st.markdown("#### :material/send: Lämna feedback")
            
            # Create three tabs for 'Record' and 'Write text'    
            tab1, tab2 = st.tabs([":material/mic: Tala", ":material/keyboard: Skriv"])

            # TAB 1 - AUDIO RECORDER

            with tab1:

                st.markdown("Klicka på knappen __Spela in__ och prata. När du är klar klickar du på __Stoppa__.")

                # Creates the audio recorder
                audio = audiorecorder(start_prompt="Spela in", stop_prompt="Stoppa", pause_prompt="", key=None)

                if len(audio) > 0:

                    audio_file_number = random.randint(1000000, 9000000)

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

                            # Delete both the original WAV file and the compressed MP3 file after transcription
                            original_wav_file = f"audio/{audio_file_number}_recording.wav"
                            compressed_mp3_file = st.session_state.file_name_converted

                            if os.path.exists(original_wav_file):
                                os.remove(original_wav_file)

                            if os.path.exists(compressed_mp3_file):
                                os.remove(compressed_mp3_file)
                            
                    
                    st.markdown("#### :material/summarize: Du sa:")
                    
                    st.write(st.session_state.transcribed)


            # TAB 2 - TEXT INPUT AREA

            with tab2:

                st.markdown("Skriv i det gråa fältet nedan. När du är klar klickar du på __Skicka__.")

                with st.form("send_feedback"):
                    feedback_text = st.text_area("Feedback", label_visibility="hidden")
                    st.form_submit_button('Skicka')

                    if feedback_text:
                        st.session_state.transcribed = feedback_text
            

    with maincol2:

        full_response = ""

        st.markdown("#### :material/summarize: Sammanställning")

        if "transcribed" in st.session_state:

            if "processed_feedback" not in st.session_state:

                system_prompt = p.feedback_prompt_1
                full_response = ""

                butcol1, butcol2, butcol3, butcol4 = st.columns(4, gap="small")

                with butcol1:
                    with st.popover("Visa prompt"):
                        st.write(system_prompt)
                    
                llm_model = st.session_state["llm_chat_model"]
                llm_temp = st.session_state["llm_temperature"]
                
                if "llama" in llm_model:
                    full_response = process_text(llm_model, llm_temp, system_prompt, st.session_state.transcribed)

                else:
                    full_response = process_text_openai(system_prompt, st.session_state.transcribed)
                
                # Store the processed feedback in session state
                st.session_state["processed_feedback"] = full_response
                st.session_state["feedback_submitted"] = False
            
            else:
                full_response = st.session_state["processed_feedback"]

        else:
            st.write("När du talat eller skrivit in din feedback kommer du få en sammanställning här...")
        

        # Send result to Supabase database
        if st.session_state["feedback_submitted"] == False:
           
            if st.button('Skicka feedback', type='primary'):
                data = {
                    'dashboard_id': int(dashboard_id),
                    'processed_text': st.session_state["processed_feedback"]
                }
                response = supabase.table('feedback').insert(data).execute()
                
                if response.data:
                    st.session_state["feedback_submitted"] = True  # Mark feedback as submitted
                    st.success('Dina tankar är delade med oss nu... Ladda om sidan om du vill skicka in ny feedback.', icon = ":material/thumb_up:")
                    st.balloons()
                    #st.rerun(scope="app")

                else:
                    st.error(f'Oooops. Nått gick fel: {response.error.message}')
            


if __name__ == "__main__":
    main()



