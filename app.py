import streamlit as st
import tempfile
import os
from typing import Optional
import re
import openai
# You'll need to install these:
# pip install streamlit assemblyai openai python-dotenv

import assemblyai as aai
import tempfile
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def main():
    st.set_page_config(
        page_title="Voice Code Assistant",
        page_icon="🎤",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎤 Voice Code Assistant")
    st.markdown("Upload your code file and ask questions using your voice!")
    
    # Initialize session state
    if 'code_content' not in st.session_state:
        st.session_state.code_content = ""
    if 'file_info' not in st.session_state:
        st.session_state.file_info = {}
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 Upload Code File")
        uploaded_file = st.file_uploader(
            "Choose a code file",
            type=['py', 'js', 'java', 'cpp', 'c', 'html', 'css', 'php', 'rb', 'go'],
            help="Upload a single code file to analyze"
        )
        
        if uploaded_file is not None:
            # Read and store file content
            file_content = uploaded_file.read().decode('utf-8')
            st.session_state.code_content = file_content
            st.session_state.file_info = {
                'name': uploaded_file.name,
                'size': len(file_content),
                'lines': len(file_content.split('\n')),
                'type': uploaded_file.name.split('.')[-1]
            }
            
            # Show file info
            st.success(f"✅ File loaded: {uploaded_file.name}")
            st.info(f"📊 {st.session_state.file_info['lines']} lines, {st.session_state.file_info['size']} characters")
        
        # Quick action buttons
        if st.session_state.code_content:
            st.header("🚀 Quick Questions")
            quick_questions = [
                "Explain the main function",
                "What does this code do?",
                "Are there any bugs?",
                "How can I optimize this?",
                "What are the key variables?",
                "Explain the logic flow"
            ]
            
            for question in quick_questions:
                if st.button(question, key=f"quick_{question}"):
                    process_question(question)
    
    # Main content area
    if not st.session_state.code_content:
        st.info("👆 Please upload a code file from the sidebar to get started!")
        return
    
    # Display code with syntax highlighting
    st.header("📄 Your Code")
    with st.expander("View uploaded code", expanded=False):
        st.code(st.session_state.code_content, language=st.session_state.file_info['type'])
    
    # Voice input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🎙️ Ask Questions")
        
        # Simple file uploader for audio
        st.subheader("🎤 Record and Upload Audio")
        audio_file = st.file_uploader(
            "Upload your voice question (WAV, MP3, M4A)", 
            type=['wav', 'mp3', 'm4a', 'flac'],
            help="Record audio on your phone/computer and upload here"
        )
        
        if audio_file is not None:
            st.audio(audio_file, format='audio/wav')
            
            if st.button("🎧 Transcribe Audio", key="transcribe_btn"):
                with st.spinner("🎧 Transcribing your question with AssemblyAI..."):
                    try:
                        # Save uploaded file to temp location
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.name.split('.')[-1]}") as tmp_file:
                            tmp_file.write(audio_file.read())
                            tmp_file_path = tmp_file.name
                        
                        # Transcribe with AssemblyAI
                        transcriber = aai.Transcriber()
                        transcript = transcriber.transcribe(tmp_file_path)
                        
                        # Clean up temp file
                        os.unlink(tmp_file_path)
                        
                        if transcript.status == aai.TranscriptStatus.error:
                            st.error(f"Transcription error: {transcript.error}")
                        else:
                            transcribed_text = transcript.text
                            st.success(f"🎯 You asked: **{transcribed_text}**")
                            
                            # Process the transcribed question
                            process_question(transcribed_text)
                            
                    except Exception as e:
                        st.error(f"Error processing audio: {str(e)}")
        
        # Alternative: Browser-based recording with JavaScript
        st.subheader("🎙️ Or Record Directly in Browser")
        
        # Add JavaScript for browser recording
        record_html = """
        <div style="margin: 20px 0;">
            <button id="recordBtn" onclick="toggleRecording()" 
                    style="background: #667eea; color: white; border: none; 
                           padding: 15px 30px; border-radius: 8px; font-size: 16px; 
                           cursor: pointer; margin-right: 10px;">
                🎤 Start Recording
            </button>
            <span id="recordStatus" style="color: #666; font-style: italic;"></span>
        </div>
        <div id="recordingInfo" style="background: #f0f2f6; padding: 15px; 
                                       border-radius: 8px; margin: 10px 0; 
                                       min-height: 50px; border: 2px dashed #ccc;">
            Click "Start Recording" to begin. Your audio will be saved and can be uploaded for transcription.
        </div>
        
        <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        
        function toggleRecording() {
            const btn = document.getElementById('recordBtn');
            const status = document.getElementById('recordStatus');
            const info = document.getElementById('recordingInfo');
            
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                alert('Audio recording is not supported in this browser.');
                return;
            }
            
            if (!isRecording) {
                // Start recording
                navigator.mediaDevices.getUserMedia({ audio: true })
                    .then(stream => {
                        mediaRecorder = new MediaRecorder(stream);
                        audioChunks = [];
                        
                        mediaRecorder.ondataavailable = function(event) {
                            audioChunks.push(event.data);
                        };
                        
                        mediaRecorder.onstop = function() {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                            const audioUrl = URL.createObjectURL(audioBlob);
                            
                            info.innerHTML = `
                                <strong>Recording completed!</strong><br>
                                <audio controls src="${audioUrl}" style="margin: 10px 0;"></audio><br>
                                <a href="${audioUrl}" download="voice_question.wav" 
                                   style="background: #48bb78; color: white; padding: 8px 16px; 
                                          text-decoration: none; border-radius: 4px;">
                                    📥 Download Audio File
                                </a><br>
                                <small style="color: #666; margin-top: 10px; display: block;">
                                    Download this file and upload it above for transcription with AssemblyAI
                                </small>
                            `;
                        };
                        
                        mediaRecorder.start();
                        isRecording = true;
                        btn.innerHTML = '⏹️ Stop Recording';
                        btn.style.background = '#e53e3e';
                        status.innerHTML = 'Recording... Click stop when done';
                        info.innerHTML = '<em>🔴 Recording in progress... Speak your question now!</em>';
                    })
                    .catch(err => {
                        console.error('Error accessing microphone:', err);
                        alert('Could not access microphone. Please check permissions.');
                    });
            } else {
                // Stop recording
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
                isRecording = false;
                btn.innerHTML = '🎤 Start Recording';
                btn.style.background = '#667eea';
                status.innerHTML = 'Processing...';
            }
        }
        </script>
        """
        
        st.components.v1.html(record_html, height=300)
        
        # Text input fallback
        st.subheader("💬 Or type your question:")
        question = st.text_input("What would you like to know about your code?", key="question_input")
        if st.button("Ask Question", key="ask_btn") and question:
            process_question(question)
    
    with col2:
        st.header("💡 Tips")
        st.markdown("""
        **Try asking:**
        - "Explain line 25"
        - "What does function_name do?"
        - "Are there any bugs?"
        - "How to optimize this?"
        - "What variables are used?"
        - "Explain the main logic"
        """)
    
    # Conversation history
    if st.session_state.conversation_history:
        st.header("💬 Conversation History")
        for i, (question, answer) in enumerate(st.session_state.conversation_history):
            with st.expander(f"Q{i+1}: {question[:50]}...", expanded=(i == len(st.session_state.conversation_history)-1)):
                st.markdown(f"**❓ Question:** {question}")
                st.markdown(f"**🤖 Answer:** {answer}")

def process_question(question: str):
    """Process a question about the code"""
    if not st.session_state.code_content:
        st.error("No code file uploaded!")
        return
    
    with st.spinner("🤔 Analyzing your code..."):
        # Here you'll implement the actual code analysis
        answer = analyze_code_question(question, st.session_state.code_content)
        
        # Add to conversation history
        st.session_state.conversation_history.append((question, answer))
        
        # Display the answer
        st.success("🎯 Here's what I found:")
        st.markdown(answer)

def analyze_code_question(question: str, code: str) -> str:
    """
    Analyze the question using OpenAI GPT
    """
    try:
        # Create a focused prompt for code analysis
        prompt = f"""You are an expert code assistant. Analyze the following code and answer the user's question clearly and concisely.

Code:
```{st.session_state.file_info.get('type', 'text')}
{code}
```

User Question: {question}

Please provide:
1. A direct answer to their question
2. Relevant code snippets or line references if applicable
3. Any helpful suggestions or improvements

Keep your response conversational and helpful, as if explaining to a colleague."""

        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # More cost-effective than gpt-4
            messages=[
                {"role": "system", "content": "You are a helpful code analysis assistant that provides clear, practical explanations about code."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.3  # Lower temperature for more focused responses
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Sorry, I encountered an error analyzing your code: {str(e)}. Please check your OpenAI API key and try again."

# Additional helper functions you'll implement:

def setup_assemblyai():
    """Set up AssemblyAI client"""
    # You'll add your AssemblyAI API key here
    pass

def transcribe_audio(audio_bytes):
    """Transcribe audio using AssemblyAI"""
    # Implementation for AssemblyAI transcription
    pass

if __name__ == "__main__":
    main()