# speech_handler.py
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SpeechHandler:
    """Handle speech-to-text and text-to-speech operations"""
    
    def __init__(self):
        self.stt_available = False
        self.tts_available = False
        self.whisper_model = None
        self.tts = None
        
        self.initialize_stt()
        self.initialize_tts()
    
    def initialize_stt(self):
        """Initialize Speech-to-Text using Faster Whisper"""
        try:
            from faster_whisper import WhisperModel
            
            logger.info("Loading Whisper model...")
            self.whisper_model = WhisperModel(
                "base",
                device="cpu",
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
            
            logger.info("Loading TTS model...")
            model_name = "tts_models/en/ljspeech/tacotron2-DDC"
            self.tts = TTS(model_name=model_name, progress_bar=False)
            
            logger.info("Coqui TTS initialized successfully")
            self.tts_available = True
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self.tts_available = False
    
    def speech_to_text(self, audio_path: str) -> str:
        """Convert speech audio to text"""
        
        if not self.stt_available or self.whisper_model is None:
            logger.error("STT not available")
            return ""
        
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return ""
        
        try:
            logger.info(f"Transcribing: {audio_path}")
            
            # Transcribe audio
            segments, info = self.whisper_model.transcribe(
                audio_path,
                beam_size=5,
                language="en",
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Combine all segments
            transcript_parts = []
            for segment in segments:
                transcript_parts.append(segment.text)
                logger.info(f"Segment: {segment.text}")
            
            transcript = " ".join(transcript_parts).strip()
            
            if not transcript:
                logger.warning("Empty transcript")
                return ""
            
            logger.info(f"Transcription complete: {transcript[:100]}...")
            return transcript
            
        except Exception as e:
            logger.error(f"STT error: {e}", exc_info=True)
            return ""
    
    def text_to_speech(self, text: str, output_path: str) -> Optional[str]:
        """Convert text to speech audio"""
        
        if not self.tts_available or self.tts is None:
            logger.error("TTS not available")
            return None
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Clean text
            text = text.strip()
            if not text:
                logger.error("Empty text for TTS")
                return None
            
            logger.info(f"Generating speech for: {text[:50]}...")
            
            # Generate speech
            self.tts.tts_to_file(
                text=text,
                file_path=output_path
            )
            
            if os.path.exists(output_path):
                logger.info(f"Generated audio: {output_path}")
                return output_path
            else:
                logger.error(f"Audio file not created: {output_path}")
                return None
            
        except Exception as e:
            logger.error(f"TTS error: {e}", exc_info=True)
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