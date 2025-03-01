import streamlit as st
from openai import OpenAI
from os import environ
import os
import requests
import config as c
import streamlit as st

# Function to download the image and save it locally
def download_image(image_url, container):

    # Define the path where the image will be saved
    image_name = "generated_image.png"
    image_save_path = os.path.join('images', image_name)
    message_placeholder = container.empty()

    response = requests.get(image_url)
    if response.status_code == 200:
        with open(image_save_path, 'wb') as f:
            f.write(response.content)
    else:
        print("Failed to download the image.")
    
    message_placeholder.image(image_save_path)

    return image_save_path


def create_image(prompt, container):

    message_placeholder = container.empty()

    if c.run_mode == "streamlit":
        client = OpenAI(api_key = st.secrets.openai_key)
    else:
        client = OpenAI(api_key = environ.get("openai_key"))
    
    with message_placeholder.status("Skapar bild..."):

        response = client.images.generate(
        model = "dall-e-3",
        prompt = prompt,
        size = "1792x1024",
        quality = "standard",
        n = 1,
        )

        image_url = response.data[0].url

    return image_url
