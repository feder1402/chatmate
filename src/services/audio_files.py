import wave

from openai import OpenAI

client = OpenAI()

def buffer_to_wav_file(audio_buffer, output_filename, sample_rate = 44100):
  """Converts an in-memory audio buffer to a WAV file.

  Args:
    audio_buffer: The audio data in bytes.
    output_filename: The path to save the output WAV file.
    sample_rate: The sample rated in Herz used during the audio capture. 
      Value will be between 8,000 and 96,000. Default is 44,100.
  """
  with wave.open(output_filename, 'wb') as wf:
    wf.setnchannels(2)  # Stereo audio
    wf.setsampwidth(2)  # 2 bytes per sample (16-bit)
    wf.setframerate(sample_rate)  # Sample rate
    wf.writeframes(audio_buffer)
    wf.close()

def audio_to_text(audio_bytes, sample_rate):
  """Transcribes an audio buffer in wav format.

  Args:
    audio_buffer: The audio data in bytes.

  returns:
    The transcribed text. 
  """
  buffer_to_wav_file(audio_bytes, 'file.wav', sample_rate)
  audio_file = open('file.wav', 'rb')
  transcription = client.audio.transcriptions.create(
      model="whisper-1", 
      file=audio_file
  )
  return transcription.text

def text_to_audio(input, voice):
  response = client.audio.speech.create(
    model="tts-1",
    voice=voice,
    response_format="wav",
    input=input
  )

  response.write_to_file("speech.wav")
  audio = open("speech.wav", "rb")
  
  return audio
  