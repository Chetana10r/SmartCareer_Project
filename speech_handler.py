# speech_handler.py
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SpeechHandler:
    """Handle speech-to-text and text-to-speech operations"""
    
    def __init__(self):
        self.initialize_stt()
        self.initialize_tts()
    
    def initialize_stt(self):
        """Initialize Speech-to-Text using Faster Whisper"""
        try:
            from faster_whisper import WhisperModel
            
            # Use 'base' model for balance between speed and accuracy
            # Options: tiny, base, small, medium, large
            self.whisper_model = WhisperModel(
                "base",
                device="cpu",  # Use "cuda" if GPU available
                compute_type="int8"
            )
            
            logger.info("Whisper STT initialized successfully")
            self.stt_available = True
            
        except Exception as e:
            logger.error(f"Failed to initialize Whisper: {e}")
            self.stt_available = False
    
    def initialize_tts(self):
        """Initialize Text-to-Speech using Coqui TTS"""
        try:
            from TTS.api import TTS
            
            # Use a good quality English model
            model_name = "tts_models/en/ljspeech/tacotron2-DDC"
            self.tts = TTS(model_name=model_name, progress_bar=False)
            
            logger.info("Coqui TTS initialized successfully")
            self.tts_available = True
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self.tts_available = False
    
    def speech_to_text(self, audio_path: str) -> str:
        """Convert speech audio to text"""
        
        if not self.stt_available:
            logger.error("STT not available")
            return ""
        
        try:
            # Transcribe audio
            segments, info = self.whisper_model.transcribe(
                audio_path,
                beam_size=5,
                language="en"
            )
            
            # Combine all segments
            transcript = " ".join([segment.text for segment in segments])
            
            logger.info(f"Transcribed audio: {transcript[:100]}...")
            return transcript.strip()
            
        except Exception as e:
            logger.error(f"STT error: {e}")
            return ""
    
    def text_to_speech(self, text: str, output_path: str) -> Optional[str]:
        """Convert text to speech audio"""
        
        if not self.tts_available:
            logger.error("TTS not available")
            return None
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Generate speech
            self.tts.tts_to_file(
                text=text,
                file_path=output_path
            )
            
            logger.info(f"Generated audio: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file in seconds"""
        try:
            import soundfile as sf
            data, samplerate = sf.read(audio_path)
            duration = len(data) / samplerate
            return duration
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0


# Alternative: Using pyttsx3 for offline TTS (fallback)
class FallbackTTS:
    """Simple offline TTS using pyttsx3"""
    
    def __init__(self):
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # Speed
            self.engine.setProperty('volume', 0.9)
            self.available = True
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            self.available = False
    
    def text_to_speech(self, text: str, output_path: str) -> Optional[str]:
        """Generate speech using pyttsx3"""
        if not self.available:
            return None
        
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            return output_path
        except Exception as e:
            logger.error(f"pyttsx3 TTS error: {e}")
            return None


# Alternative STT using SpeechRecognition library
class FallbackSTT:
    """Fallback STT using SpeechRecognition"""
    
    def __init__(self):
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.available = True
        except Exception as e:
            logger.error(f"Failed to initialize SpeechRecognition: {e}")
            self.available = False
    
    def speech_to_text(self, audio_path: str) -> str:
        """Transcribe using Google Speech Recognition"""
        if not self.available:
            return ""
        
        try:
            import speech_recognition as sr
            
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
            
            # Use Google Speech Recognition (requires internet)
            text = self.recognizer.recognize_google(audio)
            return text
            
        except Exception as e:
            logger.error(f"Fallback STT error: {e}")
            return ""