import streamlit as st
from openai import OpenAI
from llm import process_text_openai
from os import environ
import config as c

def create_image(prompt):

    if c.run_mode == "local":
        client = OpenAI(api_key = st.secrets.openai_key)
    else:
        client = OpenAI(api_key = environ.get("openai_key"))

    response = client.images.generate(
    model = "dall-e-3",
    prompt = prompt,
    size = "1792x1024",
    quality = "standard",
    n = 1,
    )

    image_url = response.data[0].url

    return image_url
