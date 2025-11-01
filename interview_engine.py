# interview_engine.py
from flask import Blueprint, request, jsonify
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

# ---------------------- Logging Setup ----------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

interview_bp = Blueprint('interview', __name__)

# ---------------------- Lazy Component Init ----------------------
question_gen = None
speech_handler = None
answer_eval = None
audio_analyzer_instance = None
feedback_gen = None

def get_components():
    """Initialize components only once"""
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


# ---------------------- Session Persistence ----------------------
active_sessions = {}
completed_sessions = {}
SESSION_FILE = "session_store.json"

def save_sessions():
    """Persist sessions to disk to survive auto-reloads"""
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(active_sessions, f)
    except Exception as e:
        logger.warning(f"Could not save sessions: {e}")

def load_sessions():
    """Reload saved sessions from disk"""
    global active_sessions
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    active_sessions.update(data)
                    logger.info(f"Loaded {len(active_sessions)} sessions from file")
        except Exception as e:
            logger.warning(f"Failed to load sessions: {e}")

load_sessions()  # Load sessions on startup


# ---------------------- Helper ----------------------
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


# ---------------------- Routes ----------------------

@interview_bp.route('/start_interview', methods=['POST'])
def start_interview():
    """Initialize new interview session"""
    try:
        qgen, speech, _, _, _ = get_components()

        job_role = request.form.get('job_role', 'Software Engineer')
        interview_type = request.form.get('interview_type', 'technical')
        difficulty = request.form.get('difficulty', 'medium')
        duration = int(request.form.get('duration', 20))

        logger.info(f"Starting interview: {job_role}, {interview_type}, {difficulty}")

        resume_file = request.files.get('resume')
        resume_context = None
        if resume_file:
            resume_text = extract_resume_text(resume_file)
            resume_context = resume_text[:500]
            logger.info(f"Resume uploaded, context length: {len(resume_context)}")

        session_id = str(uuid.uuid4())

        # Generate questions
        questions = qgen.generate_questions(
            job_role=job_role,
            interview_type=interview_type,
            difficulty=difficulty,
            num_questions=5,
            resume_context=resume_context
        )

        if not questions:
            questions = ["Let's begin with a simple question: Tell me about yourself."]

        # Store session
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
        save_sessions()

        # Generate first question audio
        first_question = questions[0]
        os.makedirs("static/audio", exist_ok=True)
        audio_filename = f"{session_id}_q1.wav"
        audio_path = os.path.join("static", "audio", audio_filename)

        speech.text_to_speech(first_question, audio_path)
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
    """Return next interview question"""
    try:
        _, speech, _, _, _ = get_components()
        data = request.get_json()
        session_id = data.get('session_id')
        question_number = int(data.get('question_number', 1))

        load_sessions()
        if session_id not in active_sessions:
            logger.error(f"Invalid session: {session_id}")
            return jsonify({'error': 'Invalid session or session expired'}), 400

        session = active_sessions[session_id]
        questions = session['questions']

        if question_number > len(questions):
            return jsonify({'message': 'Interview completed'}), 200

        question = questions[question_number - 1]

        os.makedirs("static/audio", exist_ok=True)
        audio_filename = f"{session_id}_q{question_number}.wav"
        audio_path = os.path.join("static", "audio", audio_filename)
        speech.text_to_speech(question, audio_path)

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
    """Evaluate user answer and prepare next question"""
    try:
        _, speech, evaluator, analyzer, _ = get_components()
        session_id = request.form.get('session_id')
        question_number = int(request.form.get('question_number', 1))
        transcript = request.form.get('transcript', '').strip()
        audio_file = request.files.get('audio')

        logger.info(f"Submitting answer for session {session_id}, Q{question_number}")
        logger.info(f"Transcript length: {len(transcript)}")

        load_sessions()
        if session_id not in active_sessions:
            logger.error(f"Invalid session: {session_id}")
            return jsonify({'error': 'Invalid session or expired'}), 400

        session = active_sessions[session_id]
        question = session['questions'][question_number - 1]

        # Save audio
        audio_path = None
        if audio_file:
            os.makedirs("static/audio", exist_ok=True)
            audio_filename = f"{session_id}_a{question_number}.wav"
            audio_path = os.path.join("static", "audio", audio_filename)
            audio_file.save(audio_path)

            if not transcript:
                transcript = speech.speech_to_text(audio_path)

        if not transcript:
            transcript = "No answer provided"

        evaluation = evaluator.evaluate_answer(
            question=question,
            answer=transcript,
            job_role=session['job_role'],
            interview_type=session['interview_type']
        )

        audio_analysis = {}
        if audio_path and os.path.exists(audio_path):
            audio_analysis = analyzer.analyze_audio(audio_path, transcript)

        # Store answer
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
        save_sessions()

        next_q = question_number + 1 if question_number < len(session['questions']) else None

        return jsonify({
            'transcript': transcript,
            'score': evaluation['score'],
            'feedback': evaluation['feedback'],
            'audio_analysis': audio_analysis,
            'next_question_number': next_q
        }), 200

    except Exception as e:
        logger.error(f"Error submitting answer: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@interview_bp.route('/end_interview', methods=['POST'])
def end_interview():
    """End interview and generate overall feedback"""
    try:
        _, _, _, _, fb_gen = get_components()
        data = request.get_json()
        session_id = data.get('session_id')

        load_sessions()
        if session_id not in active_sessions:
            return jsonify({'error': 'Invalid session'}), 400

        session = active_sessions[session_id]
        session['status'] = 'completed'
        session['end_time'] = datetime.now().isoformat()

        feedback = fb_gen.generate_feedback(session=session, answers=session['answers'])
        completed_sessions[session_id] = {**session, 'feedback': feedback}

        if session_id in active_sessions:
            del active_sessions[session_id]
        save_sessions()

        logger.info(f"Interview completed: {session_id}")
        return jsonify(feedback), 200

    except Exception as e:
        logger.error(f"Error ending interview: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
