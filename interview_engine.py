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

# Initialize components (lazy loading to avoid reload issues)
question_gen = None
speech_handler = None
answer_eval = None
audio_analyzer_instance = None
feedback_gen = None

def get_components():
    """Lazy initialization of components"""
    global question_gen, speech_handler, answer_eval, audio_analyzer_instance, feedback_gen
    
    if question_gen is None:
        question_gen = QuestionGenerator()
    if speech_handler is None:
        speech_handler = SpeechHandler()
    if answer_eval is None:
        answer_eval = AnswerEvaluator()
    if audio_analyzer_instance is None:
        audio_analyzer_instance = AudioAnalyzer()
    if feedback_gen is None:
        feedback_gen = FeedbackGenerator()
    
    return question_gen, speech_handler, answer_eval, audio_analyzer_instance, feedback_gen

# In-memory storage
active_sessions = {}
completed_sessions = {}

@interview_bp.route('/start_interview', methods=['POST'])
def start_interview():
    """Initialize a new interview session"""
    try:
        qgen, speech, _, _, _ = get_components()
        
        # Get configuration
        job_role = request.form.get('job_role', 'Software Engineer')
        interview_type = request.form.get('interview_type', 'technical')
        difficulty = request.form.get('difficulty', 'medium')
        duration = int(request.form.get('duration', 20))
        
        logger.info(f"Starting interview: {job_role}, {interview_type}, {difficulty}")
        
        # Optional resume upload
        resume_file = request.files.get('resume')
        resume_context = None
        
        if resume_file:
            resume_text = extract_resume_text(resume_file)
            resume_context = resume_text[:500]
            logger.info(f"Resume uploaded, context length: {len(resume_context)}")
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Generate questions
        questions = qgen.generate_questions(
            job_role=job_role,
            interview_type=interview_type,
            difficulty=difficulty,
            num_questions=5,
            resume_context=resume_context
        )
        
        logger.info(f"Generated {len(questions)} questions")
        
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
        audio_filename = f"{session_id}_q1.wav"
        audio_path = os.path.join("static", "audio", audio_filename)
        
        speech.text_to_speech(
            text=first_question,
            output_path=audio_path
        )
        
        logger.info(f"Interview started: {session_id}")
        
        return jsonify({
            'session_id': session_id,
            'question': first_question,
            'audio_url': f'/static/audio/{audio_filename}',
            'total_questions': len(questions),
            'question_number': 1
        }), 200
        
    except Exception as e:
        logger.error(f"Error starting interview: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@interview_bp.route('/get_next_question', methods=['POST'])
def get_next_question():
    """Get the next question in the interview"""
    try:
        _, speech, _, _, _ = get_components()
        
        data = request.get_json()
        session_id = data.get('session_id')
        question_number = data.get('question_number', 1)
        
        logger.info(f"Getting question {question_number} for session {session_id}")
        
        if session_id not in active_sessions:
            logger.error(f"Invalid session: {session_id}")
            return jsonify({'error': 'Invalid session'}), 400
        
        session = active_sessions[session_id]
        questions = session['questions']
        
        if question_number > len(questions):
            logger.error(f"Question number {question_number} exceeds total {len(questions)}")
            return jsonify({'error': 'No more questions'}), 400
        
        question = questions[question_number - 1]
        
        # Generate audio
        audio_filename = f"{session_id}_q{question_number}.wav"
        audio_path = os.path.join("static", "audio", audio_filename)
        
        speech.text_to_speech(
            text=question,
            output_path=audio_path
        )
        
        return jsonify({
            'question': question,
            'audio_url': f'/static/audio/{audio_filename}',
            'total_questions': len(questions),
            'question_number': question_number
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting next question: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@interview_bp.route('/submit_answer', methods=['POST'])
def submit_answer():
    """Process and evaluate user's answer"""
    try:
        _, speech, evaluator, analyzer, _ = get_components()
        
        session_id = request.form.get('session_id')
        question_number = int(request.form.get('question_number', 1))
        transcript = request.form.get('transcript', '').strip()
        audio_file = request.files.get('audio')
        
        logger.info(f"Submitting answer for session {session_id}, Q{question_number}")
        logger.info(f"Transcript length: {len(transcript)}")
        
        if session_id not in active_sessions:
            logger.error(f"Invalid session: {session_id}")
            return jsonify({'error': 'Invalid session'}), 400
        
        session = active_sessions[session_id]
        question = session['questions'][question_number - 1]
        
        # Save audio file
        audio_path = None
        if audio_file:
            audio_filename = f"{session_id}_a{question_number}.wav"
            audio_path = os.path.join("static", "audio", audio_filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
            audio_file.save(audio_path)
            logger.info(f"Audio saved: {audio_path}")
            
            # If no transcript provided, transcribe audio
            if not transcript:
                logger.info("No transcript provided, transcribing audio...")
                transcript = speech.speech_to_text(audio_path)
                logger.info(f"Transcribed: {transcript[:100]}...")
        
        # If still no transcript, use placeholder
        if not transcript:
            transcript = "No answer provided"
            logger.warning("No transcript available")
        
        # Evaluate answer
        logger.info("Evaluating answer...")
        evaluation = evaluator.evaluate_answer(
            question=question,
            answer=transcript,
            job_role=session['job_role'],
            interview_type=session['interview_type']
        )
        
        logger.info(f"Score: {evaluation['score']}")
        
        # Analyze audio quality
        audio_analysis = {}
        if audio_path and os.path.exists(audio_path):
            logger.info("Analyzing audio...")
            audio_analysis = analyzer.analyze_audio(audio_path, transcript)
            logger.info(f"Audio analysis complete: {audio_analysis.get('confidence_score', 0)}")
        
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
        
        logger.info(f"Answer stored. Total answers: {len(session['answers'])}")
        
        return jsonify({
            'transcript': transcript,
            'score': evaluation['score'],
            'feedback': evaluation['feedback'],
            'audio_analysis': audio_analysis,
            'next_question_number': question_number + 1 if question_number < len(session['questions']) else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error submitting answer: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@interview_bp.route('/end_interview', methods=['POST'])
def end_interview():
    """End interview and generate comprehensive feedback"""
    try:
        _, _, _, _, fb_gen = get_components()
        
        data = request.get_json()
        session_id = data.get('session_id')
        
        logger.info(f"Ending interview: {session_id}")
        
        if session_id not in active_sessions:
            logger.error(f"Invalid session: {session_id}")
            return jsonify({'error': 'Invalid session'}), 400
        
        session = active_sessions[session_id]
        session['status'] = 'completed'
        session['end_time'] = datetime.now().isoformat()
        
        logger.info(f"Generating feedback for {len(session['answers'])} answers")
        
        # Generate comprehensive feedback
        feedback = fb_gen.generate_feedback(
            session=session,
            answers=session['answers']
        )
        
        logger.info(f"Feedback generated. Overall score: {feedback.get('overall_score', 0)}")
        
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
        logger.error(f"Error ending interview: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@interview_bp.route('/get_feedback', methods=['POST'])
def get_feedback():
    """Retrieve feedback for a completed interview"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        logger.info(f"Getting feedback for session: {session_id}")
        
        if session_id in completed_sessions:
            return jsonify(completed_sessions[session_id]['feedback']), 200
        else:
            logger.error(f"Session not found: {session_id}")
            return jsonify({'error': 'Session not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting feedback: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@interview_bp.route('/get_interview_history', methods=['POST'])
def get_interview_history():
    """Get user's interview history"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'user123')
        
        logger.info(f"Getting history for user: {user_id}")
        
        # Get all completed sessions for user
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
        
        logger.info(f"Found {len(history)} interviews")
        
        return jsonify({'interviews': history}), 200
        
    except Exception as e:
        logger.error(f"Error getting history: {e}", exc_info=True)
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