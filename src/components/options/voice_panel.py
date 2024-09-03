import streamlit as st

from audio_recorder_streamlit import audio_recorder

from src.services.audio_files import audio_to_text, text_to_audio

sample_rate = 44100

def render_voice_panel():
    st.subheader("Speech to Text", divider=True)
    audio_bytes = audio_recorder(text="Click to record", icon_size="1x", sample_rate=sample_rate)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav", autoplay=True)
        transcript = audio_to_text(audio_bytes, sample_rate)
        st.write(f'**Transcript:** {transcript}') 

        if transcript:
            st.subheader("Text to Speech", divider=True)
            col1, col2 = st.columns([7, 3])
            with col1:
                voice = st.selectbox(label="voice", options=["alloy", "echo", "fable", "onyx", "nova", "shimmer"], label_visibility="collapsed")
            with col2:
                clicked = st.button("go", use_container_width=True)

            if clicked:
                speech = text_to_audio(transcript, voice)
                if speech:
                    st.audio(speech, autoplay=True)





