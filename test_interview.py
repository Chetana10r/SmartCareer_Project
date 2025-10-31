# test_interview.py
import os
import sys

print("Testing Interview Components...")

# Test 1: Question Generator
print("\n1. Testing Question Generator...")
try:
    from question_generator import QuestionGenerator
    qgen = QuestionGenerator()
    questions = qgen.generate_questions("Data Scientist", "technical", "medium", 3)
    print(f"✅ Generated {len(questions)} questions")
    for i, q in enumerate(questions, 1):
        print(f"   Q{i}: {q[:60]}...")
except Exception as e:
    print(f"❌ Question Generator failed: {e}")

# Test 2: Speech Handler
print("\n2. Testing Speech Handler...")
try:
    from speech_handler import SpeechHandler
    speech = SpeechHandler()
    
    # Test TTS
    test_text = "This is a test question."
    os.makedirs("static/audio", exist_ok=True)
    output = speech.text_to_speech(test_text, "static/audio/test.wav")
    
    if output and os.path.exists(output):
        print(f"✅ TTS working: {output}")
        
        # Test STT
        transcript = speech.speech_to_text(output)
        print(f"✅ STT working: {transcript}")
    else:
        print("❌ TTS failed")
except Exception as e:
    print(f"❌ Speech Handler failed: {e}")

# Test 3: Answer Evaluator
print("\n3. Testing Answer Evaluator...")
try:
    from answer_evaluator import AnswerEvaluator
    evaluator = AnswerEvaluator()
    
    result = evaluator.evaluate_answer(
        question="What is machine learning?",
        answer="Machine learning is a branch of AI that enables systems to learn from data and improve over time without explicit programming.",
        job_role="Data Scientist",
        interview_type="technical"
    )
    
    print(f"✅ Evaluation working")
    print(f"   Score: {result['score']}")
    print(f"   Feedback: {result['feedback'][:100]}...")
except Exception as e:
    print(f"❌ Answer Evaluator failed: {e}")

# Test 4: Audio Analyzer
print("\n4. Testing Audio Analyzer...")
try:
    from audio_analyzer import AudioAnalyzer
    analyzer = AudioAnalyzer()
    
    if os.path.exists("static/audio/test.wav"):
        analysis = analyzer.analyze_audio(
            "static/audio/test.wav",
            "This is a test question"
        )
        print(f"✅ Audio Analyzer working")
        print(f"   Confidence: {analysis.get('confidence_score', 0)}")
    else:
        print("⚠️  No test audio file found")
except Exception as e:
    print(f"❌ Audio Analyzer failed: {e}")

# Test 5: Feedback Generator
print("\n5. Testing Feedback Generator...")
try:
    from feedback_generator import FeedbackGenerator
    fb_gen = FeedbackGenerator()
    
    mock_session = {
        'job_role': 'Data Scientist',
        'interview_type': 'technical',
        'start_time': '2025-10-31'
    }
    
    mock_answers = [
        {
            'question': 'Test question',
            'answer': 'Test answer',
            'score': 7.5,
            'feedback': 'Good answer',
            'audio_analysis': {'confidence_score': 7.5, 'clarity_score': 8.0}
        }
    ]
    
    feedback = fb_gen.generate_feedback(mock_session, mock_answers)
    print(f"✅ Feedback Generator working")
    print(f"   Overall Score: {feedback['overall_score']}")
except Exception as e:
    print(f"❌ Feedback Generator failed: {e}")

print("\n✅ All tests complete!")