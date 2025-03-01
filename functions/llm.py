
# External imports
import streamlit as st
from groq import Groq
from openai import OpenAI

# Python imports
import os
from os import environ

# Internal imports
import config as c


def process_text(system_prompt, text):

    if c.run_mode == "streamlit":
        client = Groq(api_key = st.secrets.groq_key)
    else:
        client = Groq(api_key = environ.get("groq_key"))

    with st.container(border = True):
        message_placeholder = st.empty()
        full_response = ""

        
        stream = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            model = c.llm_model,
            temperature = c.llm_temperature,
            max_tokens=2048,
            top_p=1,
            stop=None,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_response += str(chunk.choices[0].delta.content)
            message_placeholder.markdown(full_response + "▌")
            
        message_placeholder.markdown(full_response)

        return full_response



def process_text_openai(system_prompt, text):

    if c.run_mode == "streamlit":
        client = OpenAI(api_key = st.secrets.openai_key)
    else:
        client = OpenAI(api_key = environ.get("openai_key"))
    
    with st.container(border = False):

        message_placeholder = st.empty()
        full_response = ""

        for response in client.chat.completions.create(
            model = c.llm_model,
            temperature = c.llm_temperature,
            messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
            ],
            stream=True,
            ):
                if response.choices[0].delta.content:
                    full_response += str(response.choices[0].delta.content)
                message_placeholder.markdown(full_response + "▌") 
                
        message_placeholder.markdown(full_response)
        
        return full_response
    

def process_text_openai_recommendation(system_prompt, text):

    if c.run_mode == "streamlit":
        client = OpenAI(api_key = st.secrets.openai_key)
    else:
        client = OpenAI(api_key = environ.get("openai_key"))
    
    with st.container(border = True):

        message_placeholder = st.empty()
        full_response = ""

        for response in client.chat.completions.create(
            model = c.llm_model,
            temperature = c.llm_temperature,
            messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
            ],
            stream=True,
            ):
                if response.choices[0].delta.content:
                    full_response += str(response.choices[0].delta.content)
                message_placeholder.markdown(full_response + "▌") 
                
        message_placeholder.markdown(full_response)
        
        return full_response
    

def stream_text_openai(system_prompt, text, container):

    if c.run_mode == "streamlit":
        client = OpenAI(api_key=st.secrets.openai_key)
    else:
        client = OpenAI(api_key=environ.get("openai_key"))

    # Use the container to create a placeholder for streaming content
    message_placeholder = container.empty()
    full_response = ""

    for response in client.chat.completions.create(
        model = c.llm_model,
        temperature = c.llm_temperature,
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        stream = True,
        ):
        if response.choices[0].delta.content:
            full_response += str(response.choices[0].delta.content)
        message_placeholder.write(full_response + "▌")  # Update the placeholder with the current content

    message_placeholder.write(full_response)  # Final update to remove the cursor

    return full_response



def process_text_openai_image_prompt(system_prompt, text, container):

    if c.run_mode == "streamlit":
        client = OpenAI(api_key = st.secrets.openai_key)
    else:
        client = OpenAI(api_key = environ.get("openai_key"))

    message_placeholder = container.empty()
    full_response = ""

    for response in client.chat.completions.create(
        model = c.llm_model,
        temperature = 0.8,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        stream=True,
        ):

        with message_placeholder.status("Skapar prompt till bild..."):
            if response.choices[0].delta.content:
                full_response += str(response.choices[0].delta.content)
            st.write(full_response + "▌")  # Update the placeholder with the current content

    return full_response