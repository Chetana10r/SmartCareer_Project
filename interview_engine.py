# interview_engine.py
from flask import Blueprint, request, jsonify, send_file
import uuid
import os
import json
from datetime import datetime
from question_generator import QuestionGenerator
from speech_handler import SpeechHandler
from answer_evaluator import AnswerEvaluator
from audio_analyzer import AudioAnalyzer
from feedback_generator import FeedbackGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

interview_bp = Blueprint('interview', __name__)

# Initialize components
question_gen = QuestionGenerator()
speech_handler = SpeechHandler()
answer_eval = AnswerEvaluator()
audio_analyzer = AudioAnalyzer()
feedback_gen = FeedbackGenerator()

# In-memory storage (replace with database in production)
active_sessions = {}
completed_sessions = {}

@interview_bp.route('/start_interview', methods=['POST'])
def start_interview():
    """Initialize a new interview session"""
    try:
        # Get configuration
        job_role = request.form.get('job_role', 'Software Engineer')
        interview_type = request.form.get('interview_type', 'technical')
        difficulty = request.form.get('difficulty', 'medium')
        duration = int(request.form.get('duration', 20))
        
        # Optional resume upload
        resume_file = request.files.get('resume')
        resume_context = None
        
        if resume_file:
            resume_text = extract_resume_text(resume_file)
            resume_context = resume_text[:500]  # Use first 500 chars for context
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Generate questions
        questions = question_gen.generate_questions(
            job_role=job_role,
            interview_type=interview_type,
            difficulty=difficulty,
            num_questions=5,
            resume_context=resume_context
        )
        
        # Initialize session
        active_sessions[session_id] = {
            'session_id': session_id,
            'job_role': job_role,
            'interview_type': interview_type,
            'difficulty': difficulty,
            'duration': duration,
            'questions': questions,
            'current_question': 0,
            'answers': [],
            'start_time': datetime.now().isoformat(),
            'status': 'active'
        }
        
        # Get first question
        first_question = questions[0]
        
        # Generate audio for first question
        audio_path = speech_handler.text_to_speech(
            text=first_question,
            output_path=f"static/audio/{session_id}_q1.wav"
        )
        
        logger.info(f"Interview started: {session_id}")
        
        return jsonify({
            'session_id': session_id,
            'question': first_question,
            'audio_url': f'/static/audio/{session_id}_q1.wav',
            'total_questions': len(questions),
            'question_number': 1
        }), 200
        
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        return jsonify({'error': str(e)}), 500


@interview_bp.route('/get_next_question', methods=['POST'])
def get_next_question():
    """Get the next question in the interview"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        question_number = data.get('question_number', 1)
        
        if session_id not in active_sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        session = active_sessions[session_id]
        questions = session['questions']
        
        if question_number > len(questions):
            return jsonify({'error': 'No more questions'}), 400
        
        question = questions[question_number - 1]
        
        # Generate audio
        audio_path = speech_handler.text_to_speech(
            text=question,
            output_path=f"static/audio/{session_id}_q{question_number}.wav"
        )
        
        return jsonify({
            'question': question,
            'audio_url': f'/static/audio/{session_id}_q{question_number}.wav',
            'total_questions': len(questions),
            'question_number': question_number
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting next question: {e}")
        return jsonify({'error': str(e)}), 500


@interview_bp.route('/submit_answer', methods=['POST'])
def submit_answer():
    """Process and evaluate user's answer"""
    try:
        session_id = request.form.get('session_id')
        question_number = int(request.form.get('question_number', 1))
        transcript = request.form.get('transcript', '')
        audio_file = request.files.get('audio')
        
        if session_id not in active_sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        session = active_sessions[session_id]
        question = session['questions'][question_number - 1]
        
        # Save audio file
        audio_path = None
        if audio_file:
            audio_path = f"static/audio/{session_id}_a{question_number}.wav"
            audio_file.save(audio_path)
            
            # If no transcript provided, transcribe audio
            if not transcript:
                transcript = speech_handler.speech_to_text(audio_path)
        
        # Evaluate answer
        evaluation = answer_eval.evaluate_answer(
            question=question,
            answer=transcript,
            job_role=session['job_role'],
            interview_type=session['interview_type']
        )
        
        # Analyze audio quality (confidence, clarity, etc.)
        audio_analysis = {}
        if audio_path and os.path.exists(audio_path):
            audio_analysis = audio_analyzer.analyze_audio(audio_path, transcript)
        
        # Store answer with evaluation
        answer_data = {
            'question_number': question_number,
            'question': question,
            'answer': transcript,
            'score': evaluation['score'],
            'feedback': evaluation['feedback'],
            'audio_analysis': audio_analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        session['answers'].append(answer_data)
        session['current_question'] = question_number
        
        logger.info(f"Answer submitted for session {session_id}, Q{question_number}")
        
        return jsonify({
            'transcript': transcript,
            'score': evaluation['score'],
            'feedback': evaluation['feedback'],
            'audio_analysis': audio_analysis,
            'next_question_number': question_number + 1 if question_number < len(session['questions']) else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        return jsonify({'error': str(e)}), 500


@interview_bp.route('/end_interview', methods=['POST'])
def end_interview():
    """End interview and generate comprehensive feedback"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id not in active_sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        session = active_sessions[session_id]
        session['status'] = 'completed'
        session['end_time'] = datetime.now().isoformat()
        
        # Generate comprehensive feedback
        feedback = feedback_gen.generate_feedback(
            session=session,
            answers=session['answers']
        )
        
        # Move to completed sessions
        completed_sessions[session_id] = {
            **session,
            'feedback': feedback
        }
        
        # Remove from active sessions
        del active_sessions[session_id]
        
        logger.info(f"Interview completed: {session_id}")
        
        return jsonify(feedback), 200
        
    except Exception as e:
        logger.error(f"Error ending interview: {e}")
        return jsonify({'error': str(e)}), 500


@interview_bp.route('/get_feedback', methods=['POST'])
def get_feedback():
    """Retrieve feedback for a completed interview"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id in completed_sessions:
            return jsonify(completed_sessions[session_id]['feedback']), 200
        else:
            return jsonify({'error': 'Session not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting feedback: {e}")
        return jsonify({'error': str(e)}), 500


@interview_bp.route('/get_interview_history', methods=['POST'])
def get_interview_history():
    """Get user's interview history"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'user123')
        
        # Get all completed sessions for user (in production, filter by user_id)
        history = []
        for session_id, session in completed_sessions.items():
            history.append({
                'session_id': session_id,
                'job_role': session['job_role'],
                'interview_type': session['interview_type'],
                'difficulty': session['difficulty'],
                'overall_score': session['feedback']['overall_score'],
                'date': session['start_time'][:10],
                'duration': session['duration'],
                'questions_answered': len(session['answers'])
            })
        
        # Sort by date (newest first)
        history.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({'interviews': history}), 200
        
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({'error': str(e)}), 500


def extract_resume_text(file):
    """Extract text from uploaded resume"""
    try:
        import fitz  # PyMuPDF
        pdf_bytes = file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting resume text: {e}")
        return ""