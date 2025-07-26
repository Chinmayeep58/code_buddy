import assemblyai as aai
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def transcribe_audio(audio_bytes):
    """Transcribe audio bytes to text using AssemblyAI"""
    try:
        # Save audio bytes to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        # Transcribe using AssemblyAI
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(tmp_file_path)
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        if transcript.status == aai.TranscriptStatus.error:
            return f"Transcription error: {transcript.error}"
        else:
            return transcript.text
            
    except Exception as e:
        return f"Error: {str(e)}"