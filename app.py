import streamlit as st
import base64
import json
import requests
import os
from pydub import AudioSegment
from io import BytesIO

st.title("Google Speech-to-Text - FLAC/MP3 Uploader")

# Inserisci la tua API Key qui oppure usa una variabile d'ambiente
api_key_input = st.text_input("🔑 Inserisci la tua Google API Key", type="password")

# Upload file
uploaded_file = st.file_uploader("Carica un file audio (.flac o .mp3)", type=["flac", "mp3"])

if uploaded_file is not None:
    # Converti mp3 in flac in memoria
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    if file_extension == "mp3":
        st.info("Convertendo MP3 in FLAC...")
        audio = AudioSegment.from_file(uploaded_file, format="mp3")
    elif file_extension == "flac":
        audio = AudioSegment.from_file(uploaded_file, format="flac")
    else:
        st.error("Formato non supportato.")
        st.stop()

    # Imposta sample rate a 44100 e esporta in memoria come FLAC
    audio = audio.set_frame_rate(44100).set_channels(1)
    flac_buffer = BytesIO()
    audio.export(flac_buffer, format="flac")
    flac_bytes = flac_buffer.getvalue()

    # Codifica in base64
    audio_base64 = base64.b64encode(flac_bytes).decode("utf-8")

    st.success(f"{uploaded_file.name} preparato per l'invio!")

    config = {
        "encoding": "FLAC",
        "sampleRateHertz": 44100,
        "languageCode": "it-IT"  # cambia in en-US se serve
    }

    request_payload = {
        "config": config,
        "audio": {
            "content": audio_base64
        }
    }

    if st.button("Invia a Google Speech-to-Text"):
        try:
            url = f"https://speech.googleapis.com/v1/speech:recognize?key={api_key_input}"
            response = requests.post(url, json=request_payload)
            response.raise_for_status()
            result = response.json()

            with open("result.json", "w") as f:
                json.dump(result, f, indent=2)

            st.success("Risposta ricevuta!")
            st.json(result)

        except requests.exceptions.HTTPError as http_err:
            st.error(f"Errore nella richiesta: {response.status_code} - {response.reason}")
            try:
                st.code(response.json(), language="json")
            except:
                st.text(response.text)
