
### IMPORTS 

# External imports
import streamlit as st
from openai import OpenAI
from supabase import create_client, Client

# Python imports
import os
from os import environ
from datetime import datetime
from sys import platform
import hashlib
import random
import hmac
from concurrent.futures import ThreadPoolExecutor

# Imternal imports
from functions.transcribe import transcribe_with_whisper_openai
from functions.llm import process_text, process_text_openai
from functions.styling_css import page_config, page_styling
from functions.split_audio import split_audio_to_chunks
import prompts as p
import config as c


### INITIAL VARIABLES
os.makedirs("data/audio", exist_ok=True)
os.makedirs("data/audio/audio_chunks", exist_ok=True)


# Initialize Supabase client
if c.run_mode == "streamlit":
    SUPABASE_URL = st.secrets.supabase_db_url
    SUPABASE_KEY = st.secrets.supabase_db_api
else:
    SUPABASE_URL =  environ.get("supabase_db_url")
    SUPABASE_KEY =  environ.get("supabase_db_api")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


dashboard_id = c.dashboard_id


### STYLING - PAGE CONFIG
page_config()
page_styling()


if c.run_mode == "streamlit":
    st.session_state["pwd_on"] = st.secrets.pwd_on
else:
    st.session_state["pwd_on"] = environ.get("pwd_on")

### PASSWORD

if st.session_state["pwd_on"] == "true":

    def check_password():

        if c.run_mode == "streamlit":
            passwd = st.secrets["password"]
        else:
            passwd = environ.get("password")

        def password_entered():

            if hmac.compare_digest(st.session_state["password"], passwd):
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Don't store the password.
            else:
                st.session_state["password_correct"] = False

        if st.session_state.get("password_correct", False):
            return True

        st.text_input("Lösenord", type="password", on_change=password_entered, key="password")
        if "password_correct" in st.session_state:
            st.error("😕 Ooops. Fel lösenord.")
        return False


    if not check_password():
        st.stop()

############


### INITIAL SESSION STATE
# Check and set default values if not set in session_state
# of Streamlit

if "spoken_language" not in st.session_state: # What language source audio is in
    st.session_state["spoken_language"] = "Automatiskt"
if "file_name_converted" not in st.session_state: # Audio file name
    st.session_state["file_name_converted"] = None
if "llm_temperature" not in st.session_state:
    st.session_state["llm_temperature"] = c.llm_temperature
if "llm_chat_model" not in st.session_state:
    st.session_state["llm_chat_model"] = c.llm_model
if "audio_file" not in st.session_state:
    st.session_state["audio_file"] = False
if "feedback_submitted" not in st.session_state:
    st.session_state["feedback_submitted"] = True

if 'system_prompt' not in st.session_state:
    st.session_state.system_prompt = p.prompt_help_bot


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

    st.sidebar.markdown(f"# {c.app_name}")

    st.sidebar.page_link("app.py", label="Feedback", icon=":material/home:")
    st.sidebar.page_link("pages/10Dashboard.py", label="Dashboard", icon=":material/dashboard:")

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
    topcol1, topcol2 = st.columns([2, 2], gap = "medium")

    with topcol1:

        st.markdown(f"## :material/dashboard: {c.app_name} | Feedback")
              

    # Creating two main columns
    maincol1, maincol2 = st.columns([2, 2], gap="large")

    
    with maincol1:

        with st.expander(":material/lightbulb: Hjälp och tips"):
            st.markdown(f"""__Tack för att du vill dela med dig av vad du tycker, tänker och känner!  
Allt du skickar in är anonymt.__ 
        """)
            
            st.markdown(f"""#### Tips på hur du kan ge feedback
- Försök att vara så specifik som du kan. Om det är något som du gillar eller inte gillar, 
berätta vad det är och varför.  
- Kom gärna med förslag. Om du exempelvis har något som du inte tycker fungerar, kom gärna med ett 
förslag på hur det skulle kunna lösas. Du som jobbar närmast problemet, vet oftast mest och bäst.
""")
            
        
        with st.expander(":material/forum: Chatta med Clara"):

            chat = st.container(height = 400, border = False)

            if st.button("Rensa chat", type="secondary"):
                if "messages" in st.session_state.keys(): # Initialize the chat message history
                    st.session_state.messages = [
                        {"role": "assistant", "content": """
                            Hej! Jag är Clara, en AI-chatbot. Hur kan jag hjälpa dig?
                        """}
                ]

            if "messages" not in st.session_state:
                st.session_state["messages"] = [{"role": "assistant", "content": 
                            """Hej! Jag är Clara, en AI-chatbot. Hur kan jag hjälpa dig?
                            """}
                ]

            for message in st.session_state.messages:
                with chat.chat_message(message["role"]):
                    # Check if the content is an image URL
                    if message["content"].startswith("http"):
                        st.image(message["content"])
                    else:
                        st.markdown(message["content"])

            # Define your system prompt here
            system_prompt = st.session_state.system_prompt

            if prompt := st.chat_input("Vad vill du prata om?"):
                
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat.chat_message("user"):
                    st.markdown(prompt)

                with chat.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""

                    # Preprocess messages to include the system prompt
                    processed_messages = []
                    for m in st.session_state.messages:
                        # Prepend system prompt to the user's message
                        if m["role"] == "user":
                            content_with_prompt = system_prompt + " " + m["content"]
                            processed_messages.append({"role": m["role"], "content": content_with_prompt})
                        else:
                            processed_messages.append(m)

                    if c.run_mode == "streamlit":
                        client = OpenAI(api_key = st.secrets.openai_key)
                    else:
                        client = OpenAI(api_key = environ.get("openai_key"))
            
                    for response in client.chat.completions.create(
                        model = st.session_state["llm_chat_model"],
                        temperature = st.session_state["llm_temperature"],
                        messages = processed_messages,
                        stream = True,
                    ):
                        if response.choices[0].delta.content:
                            full_response += str(response.choices[0].delta.content)
                        message_placeholder.markdown(full_response + "▌")  
                            
                    message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        
        st.markdown("#### :material/dashboard: Lämna feedback")
        
        # Create two tabs for 'Record' and 'Write text'    
        tab1, tab2 = st.tabs(["Tala", "Skriv"])

        # TAB 1 - AUDIO RECORDER

        with tab1:

            st.markdown("Klicka på __mikrofonikonen__ och prata. När du är klar klickar du på __stoppikonen__.")

            audio = st.audio_input("Record a voice message", label_visibility = "collapsed")

            if audio:

                audio_file_number = random.randint(1000000, 9000000)
                current_file_hash = compute_file_hash(audio)

                # If the uploaded file hash is different from the one in session state, reset the state
                if "file_hash" not in st.session_state or st.session_state.file_hash != current_file_hash:
                    st.session_state.file_hash = current_file_hash
                    
                    if "transcribed" in st.session_state:
                        del st.session_state.transcribed

                if "transcribed" not in st.session_state:

                    with st.status('Delar upp ljudfilen i mindre bitar...'):
                        chunk_paths = split_audio_to_chunks(audio_file_number, audio)

                    # Transcribe chunks in parallel
                    with st.status('Transkriberar alla ljudbitar. Det här kan ta ett tag beroende på lång inspelningen är...'):
                        with ThreadPoolExecutor() as executor:
                            # Open each chunk as a file object and pass it to transcribe_with_whisper_openai
                            transcriptions = list(executor.map(
                                lambda chunk: transcribe_with_whisper_openai(open(chunk, "rb"), os.path.basename(chunk)), 
                                chunk_paths
                            )) 
                            # Combine all the transcriptions into one
                            st.session_state.transcribed = "\n".join(transcriptions)
    
                
                with st.container(border = True):
                
                    st.markdown("##### :material/summarize: Du sa:")        
                    st.write(st.session_state.transcribed)


        # TAB 2 - TEXT INPUT AREA

        with tab2:

            st.markdown("Skriv i det grå fältet nedan. När du är klar klickar du på __Skicka__.")

            with st.form("send_feedback"):
                feedback_text = st.text_area("Feedback", label_visibility="collapsed")
                st.form_submit_button(':material/send: Skicka')

                if feedback_text:
                    st.session_state.transcribed = feedback_text
            

    with maincol2:

        with st.container(border=True):

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

                    else:
                        st.error(f'Oooops. Nått gick fel: {response.error.message}')
            


if __name__ == "__main__":
    main()



