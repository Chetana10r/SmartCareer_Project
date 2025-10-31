# feedback_generator.py
import logging
from typing import Dict, List
import numpy as np

logger = logging.getLogger(__name__)

class FeedbackGenerator:
    """Generate comprehensive interview feedback and recommendations"""
    
    def __init__(self):
        self.load_recommendation_templates()
    
    def load_recommendation_templates(self):
        """Load recommendation resources"""
        self.resources = {
            'technical': {
                'algorithms': {
                    'title': 'Master Data Structures & Algorithms',
                    'description': 'Strengthen your problem-solving with advanced algorithms',
                    'link': 'https://www.geeksforgeeks.org/data-structures/'
                },
                'system_design': {
                    'title': 'System Design Fundamentals',
                    'description': 'Learn to design scalable distributed systems',
                    'link': 'https://github.com/donnemartin/system-design-primer'
                },
                'coding_practice': {
                    'title': 'Practice Coding Problems',
                    'description': 'Improve coding skills with daily practice',
                    'link': 'https://leetcode.com/'
                }
            },
            'communication': {
                'star_method': {
                    'title': 'STAR Interview Method',
                    'description': 'Structure answers using Situation, Task, Action, Result',
                    'link': 'https://www.themuse.com/advice/star-interview-method'
                },
                'public_speaking': {
                    'title': 'Communication Skills Course',
                    'description': 'Improve clarity and reduce filler words',
                    'link': 'https://www.coursera.org/learn/communication-skills'
                }
            },
            'confidence': {
                'mock_interviews': {
                    'title': 'Practice Mock Interviews',
                    'description': 'Build confidence through regular practice',
                    'link': 'https://www.pramp.com/'
                }
            }
        }
    
    def generate_feedback(self, session: Dict, answers: List[Dict]) -> Dict:
        """Generate comprehensive feedback report"""
        
        if not answers:
            return {
                'overall_score': 0.0,
                'message': 'No answers were provided during the interview.'
            }
        
        # Calculate scores
        scores = self.calculate_overall_scores(answers)
        
        # Analyze strengths and weaknesses
        strengths = self.identify_strengths(scores, answers)
        weaknesses = self.identify_weaknesses(scores, answers)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(scores, weaknesses)
        
        # Create question-wise feedback
        questions_feedback = [
            {
                'question': ans['question'],
                'answer': ans['answer'],
                'score': ans['score'],
                'feedback': ans['feedback']
            }
            for ans in answers
        ]
        
        # Calculate soft skills scores
        soft_skills = self.calculate_soft_skills(answers)
        
        # Question scores for chart
        question_scores = [ans['score'] for ans in answers]
        
        feedback_report = {
            'overall_score': scores['overall'],
            'confidence_score': scores['confidence'],
            'clarity_score': scores['clarity'],
            'technical_score': scores['technical'],
            'questions_feedback': questions_feedback,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'recommendations': recommendations,
            'soft_skills': soft_skills,
            'question_scores': question_scores,
            'session_summary': {
                'job_role': session['job_role'],
                'interview_type': session['interview_type'],
                'difficulty': session['difficulty'],
                'questions_answered': len(answers),
                'date': session['start_time'][:10]
            }
        }
        
        return feedback_report
    
    def calculate_overall_scores(self, answers: List[Dict]) -> Dict:
        """Calculate aggregated scores from all answers"""
        
        if not answers:
            return {
                'overall': 0.0,
                'confidence': 0.0,
                'clarity': 0.0,
                'technical': 0.0
            }
        
        # Extract scores
        answer_scores = [ans['score'] for ans in answers]
        overall_score = np.mean(answer_scores)
        
        # Calculate confidence from audio analysis
        confidence_scores = []
        clarity_scores = []
        
        for ans in answers:
            audio_analysis = ans.get('audio_analysis', {})
            confidence_scores.append(audio_analysis.get('confidence_score', 7.0))
            clarity_scores.append(audio_analysis.get('clarity_score', 7.0))
        
        confidence_score = np.mean(confidence_scores) if confidence_scores else 7.0
        clarity_score = np.mean(clarity_scores) if clarity_scores else 7.0
        
        # Technical score is same as answer content quality
        technical_score = overall_score
        
        return {
            'overall': round(overall_score, 1),
            'confidence': round(confidence_score, 1),
            'clarity': round(clarity_score, 1),
            'technical': round(technical_score, 1)
        }
    
    def identify_strengths(self, scores: Dict, answers: List[Dict]) -> List[str]:
        """Identify key strengths from performance"""
        
        strengths = []
        
        # Score-based strengths
        if scores['overall'] >= 8.0:
            strengths.append("Excellent overall performance with strong technical knowledge")
        elif scores['overall'] >= 7.0:
            strengths.append("Good understanding of core concepts")
        
        if scores['confidence'] >= 8.0:
            strengths.append("High confidence in responses with strong vocal delivery")
        
        if scores['clarity'] >= 8.0:
            strengths.append("Clear and articulate communication style")
        
        # Answer-based strengths
        high_score_count = sum(1 for ans in answers if ans['score'] >= 8.0)
        if high_score_count >= len(answers) * 0.6:
            strengths.append("Consistently strong answers across multiple questions")
        
        # Analyze answer characteristics
        total_words = sum(len(ans['answer'].split()) for ans in answers)
        avg_words = total_words / len(answers)
        
        if avg_words >= 60:
            strengths.append("Detailed and comprehensive responses")
        
        # Check for examples
        examples_used = sum(1 for ans in answers 
                          if 'example' in ans['answer'].lower() or 'instance' in ans['answer'].lower())
        
        if examples_used >= len(answers) * 0.5:
            strengths.append("Good use of examples to illustrate points")
        
        # Check for structure
        structured_answers = sum(1 for ans in answers 
                                if any(word in ans['answer'].lower() 
                                      for word in ['first', 'second', 'finally', 'additionally']))
        
        if structured_answers >= len(answers) * 0.4:
            strengths.append("Well-structured and organized responses")
        
        # Default strength if none identified
        if not strengths:
            strengths.append("Completed the interview and provided answers to all questions")
        
        return strengths[:5]  # Return top 5 strengths
    
    def identify_weaknesses(self, scores: Dict, answers: List[Dict]) -> List[str]:
        """Identify areas needing improvement"""
        
        weaknesses = []
        
        # Score-based weaknesses
        if scores['overall'] < 6.0:
            weaknesses.append("Need to demonstrate deeper technical understanding")
        
        if scores['confidence'] < 6.0:
            weaknesses.append("Work on building confidence in delivery and reduce hesitation")
        
        if scores['clarity'] < 6.0:
            weaknesses.append("Improve clarity by reducing filler words and speaking more smoothly")
        
        # Answer-based weaknesses
        short_answers = sum(1 for ans in answers if len(ans['answer'].split()) < 30)
        if short_answers >= len(answers) * 0.5:
            weaknesses.append("Provide more detailed and elaborate answers")
        
        # Check for filler words
        total_fillers = sum(ans.get('audio_analysis', {}).get('filler_words_count', 0) 
                          for ans in answers)
        
        if total_fillers > len(answers) * 3:
            weaknesses.append("Reduce use of filler words (um, uh, like)")
        
        # Check for examples
        answers_without_examples = sum(1 for ans in answers 
                                      if 'example' not in ans['answer'].lower())
        
        if answers_without_examples >= len(answers) * 0.7:
            weaknesses.append("Include more real-world examples in your answers")
        
        # Check score variance
        score_variance = np.var([ans['score'] for ans in answers])
        if score_variance > 4.0:
            weaknesses.append("Work on consistency across different types of questions")
        
        # Default if no major weaknesses
        if not weaknesses and scores['overall'] < 9.0:
            weaknesses.append("Continue practicing to achieve mastery")
        
        return weaknesses[:5]  # Return top 5 areas for improvement
    
    def generate_recommendations(self, scores: Dict, weaknesses: List[str]) -> List[Dict]:
        """Generate personalized learning recommendations"""
        
        recommendations = []
        
        # Technical knowledge
        if scores['technical'] < 7.0:
            recommendations.append({
                'icon': '📚',
                **self.resources['technical']['algorithms']
            })
        
        if scores['technical'] < 6.0:
            recommendations.append({
                'icon': '🏗️',
                **self.resources['technical']['system_design']
            })
        
        # Communication
        if scores['clarity'] < 7.0 or any('filler' in w.lower() for w in weaknesses):
            recommendations.append({
                'icon': '💬',
                **self.resources['communication']['public_speaking']
            })
        
        # Structure
        if any('example' in w.lower() for w in weaknesses):
            recommendations.append({
                'icon': '⭐',
                **self.resources['communication']['star_method']
            })
        
        # Confidence
        if scores['confidence'] < 7.0:
            recommendations.append({
                'icon': '🎯',
                **self.resources['confidence']['mock_interviews']
            })
        
        # Practice
        recommendations.append({
            'icon': '💻',
            **self.resources['technical']['coding_practice']
        })
        
        return recommendations[:4]  # Return top 4 recommendations
    
    def calculate_soft_skills(self, answers: List[Dict]) -> Dict:
        """Calculate soft skills scores"""
        
        # Aggregate audio analysis data
        all_audio_analysis = [ans.get('audio_analysis', {}) for ans in answers]
        
        confidence_scores = [a.get('confidence_score', 7.0) for a in all_audio_analysis]
        clarity_scores = [a.get('clarity_score', 7.0) for a in all_audio_analysis]
        pace_scores = [a.get('pace_score', 7.0) for a in all_audio_analysis]
        
        # Problem solving (based on answer quality)
        problem_solving = np.mean([ans['score'] for ans in answers])
        
        return {
            'confidence': round(np.mean(confidence_scores), 1),
            'communication': round(np.mean(clarity_scores), 1),
            'problem_solving': round(problem_solving, 1),
            'pace_control': round(np.mean(pace_scores), 1)
        }