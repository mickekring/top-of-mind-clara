
import streamlit as st
from groq import Groq
from openai import OpenAI
import os
from os import environ

import config as c


def process_text(model, temp, system_prompt, text):

    if c.run_mode == "local":
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
            model=model,
            temperature=temp,
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



def process_text_openai(model, temp, system_prompt, text):

    if c.run_mode == "local":
        client = OpenAI(api_key = st.secrets.openai_key)
    else:
        client = OpenAI(api_key = environ.get("openai_key"))
    
    with st.container(border = True):

            message_placeholder = st.empty()
            full_response = ""

            for response in client.chat.completions.create(
                model=model,
                temperature=temp,
                messages=[
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



def process_text_openai_image_prompt(model, temp, system_prompt, text):

    if c.run_mode == "local":
        client = OpenAI(api_key = st.secrets.openai_key)
    else:
        client = OpenAI(api_key = environ.get("openai_key"))

    message_placeholder = st.empty()
    full_response = ""

    for response in client.chat.completions.create(
        model=model,
        temperature=temp,
        messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
        ],
        stream=True,
        ):
            if response.choices[0].delta.content:
                full_response += str(response.choices[0].delta.content)

    return full_response