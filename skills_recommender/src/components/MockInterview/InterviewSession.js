import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './InterviewSession.css';

function InterviewSession() {
  const location = useLocation();
  const navigate = useNavigate();
  const { sessionId, config } = location.state || {};

  const [currentQuestion, setCurrentQuestion] = useState('');
  const [questionNumber, setQuestionNumber] = useState(1);
  const [totalQuestions, setTotalQuestions] = useState(5);
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(config?.duration * 60 || 1200);
  const [answers, setAnswers] = useState([]);
  const [audioUrl, setAudioUrl] = useState('');
  const [isPlayingQuestion, setIsPlayingQuestion] = useState(false);
  const [showHint, setShowHint] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);
  const recognitionRef = useRef(null);
  const streamRef = useRef(null);

  // Initialize speech recognition
  useEffect(() => {
    if (!sessionId) {
      navigate('/mock-interview');
      return;
    }

    // Load first question
    loadNextQuestion();

    // Setup speech recognition (if browser supports it)
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;

      recognitionRef.current.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptPart = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcriptPart + ' ';
          } else {
            interimTranscript += transcriptPart;
          }
        }

        setTranscript(prev => {
          const updated = prev + finalTranscript;
          return finalTranscript ? updated : (prev || interimTranscript);
        });
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        if (event.error === 'no-speech') {
          console.log('No speech detected, continuing...');
        }
      };
    }

    // Timer countdown
    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 0) {
          clearInterval(timer);
          handleEndInterview();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      clearInterval(timer);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          console.log('Recognition already stopped');
        }
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [sessionId]);

  const loadNextQuestion = async () => {
    setIsProcessing(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/api/interview/get_next_question', {
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          question_number: questionNumber
        })
      });

      const data = await response.json();
      setCurrentQuestion(data.question);
      setAudioUrl(data.audio_url);
      setTotalQuestions(data.total_questions);
      
      // Auto-play question audio after a short delay
      setTimeout(() => {
        if (data.audio_url) {
          playQuestionAudio(data.audio_url);
        }
      }, 500);
    } catch (error) {
      console.error('Error loading question:', error);
      // Use fallback question
      setCurrentQuestion('Tell me about your experience and background.');
    } finally {
      setIsProcessing(false);
    }
  };

  const playQuestionAudio = (url) => {
    if (audioRef.current) {
      // Stop any currently playing audio
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      
      // Set new source and play
      const fullUrl = `http://127.0.0.1:5000${url}`;
      audioRef.current.src = fullUrl;
      
      setIsPlayingQuestion(true);
      
      // Use promise to handle play
      const playPromise = audioRef.current.play();
      
      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            console.log('Audio playing successfully');
          })
          .catch(error => {
            console.log('Audio play prevented:', error);
            setIsPlayingQuestion(false);
          });
      }
      
      audioRef.current.onended = () => {
        setIsPlayingQuestion(false);
      };

      audioRef.current.onerror = (e) => {
        console.error('Audio error:', e);
        setIsPlayingQuestion(false);
      };
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setTranscript('');

      // Start speech recognition
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch (e) {
          console.log('Recognition already started or error:', e);
        }
      }
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          console.log('Recognition already stopped');
        }
      }

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await submitAnswer(audioBlob);
        
        // Stop media stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
      };
    }
  };

  const submitAnswer = async (audioBlob) => {
    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'answer.webm');
      formData.append('session_id', sessionId);
      formData.append('question_number', questionNumber);
      formData.append('transcript', transcript);

      const response = await fetch('http://127.0.0.1:5000/api/interview/submit_answer', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      // Store answer with feedback
      setAnswers(prev => [...prev, {
        question: currentQuestion,
        answer: transcript,
        score: data.score,
        feedback: data.feedback
      }]);

      // Move to next question or end
      if (questionNumber < totalQuestions) {
        setQuestionNumber(prev => prev + 1);
        setTranscript('');
        loadNextQuestion();
      } else {
        handleEndInterview();
      }
    } catch (error) {
      console.error('Error submitting answer:', error);
      alert('Failed to submit answer. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const skipQuestion = () => {
    setAnswers(prev => [...prev, {
      question: currentQuestion,
      answer: 'Skipped',
      score: 0,
      feedback: 'Question was skipped'
    }]);

    if (questionNumber < totalQuestions) {
      setQuestionNumber(prev => prev + 1);
      setTranscript('');
      loadNextQuestion();
    } else {
      handleEndInterview();
    }
  };

  const handleEndInterview = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/interview/end_interview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });

      const data = await response.json();
      
      navigate('/interview-feedback', {
        state: {
          sessionId: sessionId,
          results: data
        }
      });
    } catch (error) {
      console.error('Error ending interview:', error);
      // Navigate anyway with local data
      navigate('/interview-feedback', {
        state: {
          sessionId: sessionId,
          results: {
            overall_score: 7.5,
            confidence_score: 7.5,
            clarity_score: 7.5,
            technical_score: 7.5,
            questions_feedback: answers,
            strengths: ['Good communication', 'Technical knowledge'],
            weaknesses: ['Add more examples', 'Practice more'],
            recommendations: []
          }
        }
      });
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!sessionId) {
    return null;
  }

  return (
    <div className="interview-session-container">
      <audio ref={audioRef} style={{ display: 'none' }} preload="auto" />

      {/* Header */}
      <div className="session-header">
        <div className="progress-info">
          <div className="question-counter">
            <span className="current-q">Question {questionNumber}</span>
            <span className="separator">/</span>
            <span className="total-q">{totalQuestions}</span>
          </div>
          <div className="progress-bar-container">
            <div 
              className="progress-bar-fill"
              style={{ width: `${(questionNumber / totalQuestions) * 100}%` }}
            />
          </div>
        </div>

        <div className="timer-display">
          <span className="timer-icon">⏱️</span>
          <span className={`timer-text ${timeRemaining < 300 ? 'warning' : ''}`}>
            {formatTime(timeRemaining)}
          </span>
        </div>
      </div>

      {/* Main Content */}
      <div className="session-content">
        <div className="question-card">
          <div className="question-header">
            <h2 className="question-label">Current Question</h2>
            <button 
              className="replay-button"
              onClick={() => playQuestionAudio(audioUrl)}
              disabled={isPlayingQuestion || !audioUrl}
            >
              {isPlayingQuestion ? '🔊 Playing...' : '🔊 Replay'}
            </button>
          </div>

          <div className="question-text">
            {currentQuestion || 'Loading question...'}
          </div>

          <button 
            className="hint-button"
            onClick={() => setShowHint(!showHint)}
          >
            💡 {showHint ? 'Hide Hint' : 'Show Hint'}
          </button>

          {showHint && (
            <div className="hint-box">
              <p><strong>💡 Tip:</strong> Structure your answer using the STAR method:</p>
              <ul>
                <li><strong>S</strong>ituation - Set the context</li>
                <li><strong>T</strong>ask - Describe the challenge</li>
                <li><strong>A</strong>ction - Explain what you did</li>
                <li><strong>R</strong>esult - Share the outcome</li>
              </ul>
            </div>
          )}
        </div>

        {/* Recording Interface */}
        <div className="recording-interface">
          <div className="microphone-section">
            <button
              className={`mic-button ${isRecording ? 'recording' : ''}`}
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isProcessing || isPlayingQuestion}
            >
              <span className="mic-icon">
                {isRecording ? '⏹️' : '🎤'}
              </span>
              <span className="mic-text">
                {isRecording ? 'Stop Recording' : 'Start Recording'}
              </span>
            </button>

            {isRecording && (
              <div className="recording-indicator">
                <span className="pulse-dot"></span>
                <span>Recording in progress...</span>
              </div>
            )}
          </div>

          {/* Live Transcript */}
          <div className="transcript-box">
            <div className="transcript-header">
              <span className="transcript-icon">📝</span>
              <span className="transcript-label">Your Answer (Live Transcript)</span>
            </div>
            <div className="transcript-content">
              {transcript || 'Your answer will appear here as you speak...'}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="action-buttons">
            <button
              className="skip-button"
              onClick={skipQuestion}
              disabled={isProcessing || isRecording}
            >
              ⏭️ Skip Question
            </button>

            <button
              className="end-button"
              onClick={handleEndInterview}
              disabled={isProcessing || isRecording}
            >
              🏁 End Interview
            </button>
          </div>
        </div>

        {isProcessing && (
          <div className="processing-overlay">
            <div className="spinner-large"></div>
            <p>Analyzing your response...</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default InterviewSession;