# audio_analyzer.py
import logging
import numpy as np
from typing import Dict
import re

logger = logging.getLogger(__name__)

class AudioAnalyzer:
    """Analyze audio quality, confidence, and speech patterns"""
    
    def __init__(self):
        self.initialize_audio_tools()
    
    def initialize_audio_tools(self):
        """Initialize audio analysis libraries"""
        try:
            import librosa
            self.librosa = librosa
            self.librosa_available = True
            logger.info("Librosa initialized for audio analysis")
        except Exception as e:
            logger.warning(f"Librosa not available: {e}")
            self.librosa_available = False
    
    def analyze_audio(self, audio_path: str, transcript: str) -> Dict:
        """Comprehensive audio analysis"""
        
        analysis = {
            'confidence_score': 0.0,
            'clarity_score': 0.0,
            'pace_score': 0.0,
            'filler_words_count': 0,
            'speaking_rate': 0.0,
            'pauses_detected': 0,
            'volume_consistency': 0.0
        }
        
        # Analyze transcript for soft skills
        transcript_analysis = self.analyze_transcript(transcript)
        analysis.update(transcript_analysis)
        
        # Analyze audio file
        if self.librosa_available:
            audio_analysis = self.analyze_audio_features(audio_path)
            analysis.update(audio_analysis)
        else:
            # Use transcript-based heuristics
            analysis['confidence_score'] = self.estimate_confidence_from_text(transcript)
            analysis['clarity_score'] = self.estimate_clarity_from_text(transcript)
            analysis['pace_score'] = 7.0  # Default
        
        return analysis
    
    def analyze_transcript(self, transcript: str) -> Dict:
        """Analyze transcript for speech patterns"""
        
        # Count filler words
        filler_words = ['um', 'uh', 'like', 'you know', 'i mean', 'actually', 
                       'basically', 'literally', 'so', 'well']
        
        transcript_lower = transcript.lower()
        filler_count = sum(transcript_lower.count(filler) for filler in filler_words)
        
        # Calculate speaking rate (words per minute estimate)
        words = transcript.split()
        word_count = len(words)
        
        # Detect repetitions
        repetitions = self.detect_repetitions(words)
        
        # Detect incomplete sentences
        incomplete_sentences = transcript.count('...') + transcript.count(' - ')
        
        # Vocabulary richness
        unique_words = len(set(words))
        vocab_richness = unique_words / max(word_count, 1)
        
        return {
            'filler_words_count': filler_count,
            'word_count': word_count,
            'repetitions': repetitions,
            'incomplete_sentences': incomplete_sentences,
            'vocabulary_richness': vocab_richness,
            'speaking_rate': word_count  # Will be adjusted with audio duration
        }
    
    def analyze_audio_features(self, audio_path: str) -> Dict:
        """Analyze audio file for acoustic features"""
        
        try:
            # Load audio
            y, sr = self.librosa.load(audio_path, sr=None)
            duration = len(y) / sr
            
            # Extract features
            features = {}
            
            # 1. Pitch analysis (confidence indicator)
            pitches, magnitudes = self.librosa.piptrack(y=y, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if pitch_values:
                pitch_std = np.std(pitch_values)
                pitch_range = np.max(pitch_values) - np.min(pitch_values)
                
                # More variation in pitch = more confident/engaging
                features['confidence_score'] = min(10.0, 5.0 + (pitch_std / 20))
            else:
                features['confidence_score'] = 5.0
            
            # 2. Energy/Volume analysis
            rms = self.librosa.feature.rms(y=y)[0]
            energy_mean = np.mean(rms)
            energy_std = np.std(rms)
            
            # Consistent volume = better clarity
            volume_consistency = 10.0 - (energy_std / energy_mean) * 10
            features['volume_consistency'] = max(0.0, min(10.0, volume_consistency))
            
            # 3. Speaking rate
            # Detect speech/silence segments
            non_silent = self.librosa.effects.split(y, top_db=20)
            speech_duration = sum((end - start) / sr for start, end in non_silent)
            
            # Silence ratio
            silence_ratio = (duration - speech_duration) / max(duration, 0.001)
            features['pauses_detected'] = len(non_silent) - 1
            
            # Ideal speaking rate: 140-160 words per minute
            # We'll use word_count from transcript
            features['speech_duration'] = speech_duration
            
            # 4. Clarity score based on zero-crossing rate
            zcr = self.librosa.feature.zero_crossing_rate(y)[0]
            zcr_mean = np.mean(zcr)
            
            # Higher ZCR can indicate clearer articulation
            features['clarity_score'] = min(10.0, 3.0 + zcr_mean * 100)
            
            # 5. Pace score
            if silence_ratio > 0.4:
                pace_score = 6.0  # Too many pauses
            elif silence_ratio < 0.1:
                pace_score = 6.5  # Speaking too fast
            else:
                pace_score = 8.5  # Good pace
            
            features['pace_score'] = pace_score
            
            return features
            
        except Exception as e:
            logger.error(f"Audio feature extraction error: {e}")
            return {
                'confidence_score': 7.0,
                'clarity_score': 7.0,
                'pace_score': 7.0,
                'volume_consistency': 7.0,
                'pauses_detected': 0
            }
    
    def estimate_confidence_from_text(self, transcript: str) -> float:
        """Estimate confidence from transcript patterns"""
        
        score = 7.0  # Base score
        
        # Positive indicators
        confident_phrases = ['i believe', 'i am confident', 'clearly', 'definitely',
                           'certainly', 'absolutely', 'my experience shows']
        
        uncertain_phrases = ['maybe', 'perhaps', 'i think', 'i guess', 'not sure',
                           'might be', 'could be', 'possibly']
        
        transcript_lower = transcript.lower()
        
        confident_count = sum(1 for phrase in confident_phrases if phrase in transcript_lower)
        uncertain_count = sum(1 for phrase in uncertain_phrases if phrase in transcript_lower)
        
        score += (confident_count * 0.5)
        score -= (uncertain_count * 0.3)
        
        # Check for strong statements
        if '!' in transcript:
            score += 0.3
        
        return max(0.0, min(10.0, score))
    
    def estimate_clarity_from_text(self, transcript: str) -> float:
        """Estimate clarity from transcript quality"""
        
        score = 7.0
        
        # Check sentence structure
        sentences = [s.strip() for s in transcript.split('.') if s.strip()]
        avg_sentence_length = np.mean([len(s.split()) for s in sentences]) if sentences else 0
        
        # Ideal sentence length: 15-20 words
        if 12 <= avg_sentence_length <= 25:
            score += 1.5
        elif avg_sentence_length < 8 or avg_sentence_length > 30:
            score -= 1.0
        
        # Check for proper punctuation
        if transcript.count(',') > len(transcript) / 100:  # Good use of commas
            score += 0.5
        
        return max(0.0, min(10.0, score))
    
    def detect_repetitions(self, words: list) -> int:
        """Detect word repetitions (stammering indicator)"""
        repetitions = 0
        for i in range(len(words) - 1):
            if words[i].lower() == words[i + 1].lower():
                repetitions += 1
        return repetitions
    
    def calculate_soft_skills_score(self, analysis: Dict) -> Dict:
        """Calculate soft skills metrics"""
        
        # Confidence (based on audio + transcript)
        confidence = analysis.get('confidence_score', 7.0)
        
        # Communication clarity
        clarity = analysis.get('clarity_score', 7.0)
        filler_penalty = min(2.0, analysis.get('filler_words_count', 0) * 0.2)
        clarity = max(0.0, clarity - filler_penalty)
        
        # Professional delivery
        pace = analysis.get('pace_score', 7.0)
        consistency = analysis.get('volume_consistency', 7.0)
        delivery = (pace + consistency) / 2
        
        # Articulation
        repetition_penalty = min(1.5, analysis.get('repetitions', 0) * 0.3)
        articulation = max(0.0, 8.0 - repetition_penalty)
        
        return {
            'confidence': round(confidence, 1),
            'clarity': round(clarity, 1),
            'delivery': round(delivery, 1),
            'articulation': round(articulation, 1),
            'overall_soft_skills': round((confidence + clarity + delivery + articulation) / 4, 1)
        }