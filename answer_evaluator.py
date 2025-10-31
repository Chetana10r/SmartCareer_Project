# answer_evaluator.py
import logging
import re
from typing import Dict
from sentence_transformers import SentenceTransformer, util
import numpy as np

logger = logging.getLogger(__name__)

class AnswerEvaluator:
    """Evaluate interview answers using semantic similarity and heuristics"""
    
    def __init__(self):
        self.initialize_model()
        self.load_reference_answers()
    
    def initialize_model(self):
        """Initialize sentence transformer for semantic similarity"""
        try:
            # Use a lightweight but effective model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence transformer initialized")
            self.model_available = True
        except Exception as e:
            logger.error(f"Failed to initialize sentence transformer: {e}")
            self.model_available = False
    
    def load_reference_answers(self):
        """Load reference answers for common questions"""
        self.references = {
            'machine learning': [
                "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
                "It involves algorithms that can identify patterns in data and make predictions or decisions based on that data."
            ],
            'oop': [
                "Object-oriented programming is a programming paradigm based on objects that contain data and code.",
                "Key principles include encapsulation, inheritance, polymorphism, and abstraction."
            ],
            'rest api': [
                "REST API is an architectural style for designing networked applications using HTTP requests.",
                "It uses standard HTTP methods like GET, POST, PUT, DELETE to perform operations on resources."
            ]
        }
    
    def evaluate_answer(
        self,
        question: str,
        answer: str,
        job_role: str,
        interview_type: str
    ) -> Dict:
        """Evaluate the answer and provide score with feedback"""
        
        if not answer or len(answer.strip()) < 10:
            return {
                'score': 0.0,
                'feedback': 'Answer is too short or empty. Please provide a more detailed response.'
            }
        
        # Calculate multiple scoring dimensions
        scores = {
            'content_score': self.evaluate_content(question, answer),
            'structure_score': self.evaluate_structure(answer),
            'completeness_score': self.evaluate_completeness(answer),
            'relevance_score': self.evaluate_relevance(question, answer)
        }
        
        # Weighted average
        weights = {
            'content_score': 0.4,
            'structure_score': 0.2,
            'completeness_score': 0.2,
            'relevance_score': 0.2
        }
        
        final_score = sum(scores[key] * weights[key] for key in weights)
        final_score = round(final_score, 1)
        
        # Generate feedback
        feedback = self.generate_feedback(scores, answer, question)
        
        return {
            'score': final_score,
            'feedback': feedback,
            'detailed_scores': scores
        }
    
    def evaluate_content(self, question: str, answer: str) -> float:
        """Evaluate content quality using semantic similarity"""
        
        if not self.model_available:
            return self.heuristic_content_score(answer)
        
        try:
            # Get embeddings
            question_embedding = self.model.encode(question, convert_to_tensor=True)
            answer_embedding = self.model.encode(answer, convert_to_tensor=True)
            
            # Calculate similarity
            similarity = util.pytorch_cos_sim(question_embedding, answer_embedding)[0][0].item()
            
            # Convert to 0-10 scale
            score = (similarity + 1) * 5  # Map [-1, 1] to [0, 10]
            
            # Check for key concepts
            concept_bonus = self.check_key_concepts(question, answer)
            score = min(10.0, score + concept_bonus)
            
            return score
            
        except Exception as e:
            logger.error(f"Content evaluation error: {e}")
            return self.heuristic_content_score(answer)
    
    def heuristic_content_score(self, answer: str) -> float:
        """Simple heuristic scoring based on answer length and quality"""
        words = answer.split()
        word_count = len(words)
        
        # Base score on length
        if word_count < 20:
            score = 3.0
        elif word_count < 50:
            score = 5.0
        elif word_count < 100:
            score = 7.0
        else:
            score = 8.0
        
        # Bonus for technical terms
        technical_terms = ['implement', 'algorithm', 'optimize', 'design', 
                          'architecture', 'pattern', 'framework', 'system']
        term_count = sum(1 for term in technical_terms if term in answer.lower())
        score += min(2.0, term_count * 0.3)
        
        return min(10.0, score)
    
    def check_key_concepts(self, question: str, answer: str) -> float:
        """Check if key concepts from question are addressed in answer"""
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'how', 'why', 'when', 'where'}
        question_words = question_words - stop_words
        
        # Calculate overlap
        overlap = len(question_words & answer_words)
        overlap_ratio = overlap / max(len(question_words), 1)
        
        return min(2.0, overlap_ratio * 4)
    
    def evaluate_structure(self, answer: str) -> float:
        """Evaluate answer structure and organization"""
        score = 5.0  # Base score
        
        # Check for sentences
        sentences = [s.strip() for s in answer.split('.') if s.strip()]
        if len(sentences) >= 3:
            score += 2.0
        elif len(sentences) >= 2:
            score += 1.0
        
        # Check for examples
        example_indicators = ['example', 'instance', 'such as', 'like', 'for example']
        has_example = any(ind in answer.lower() for ind in example_indicators)
        if has_example:
            score += 1.5
        
        # Check for clear structure (intro, body, conclusion)
        transition_words = ['first', 'second', 'finally', 'additionally', 'moreover', 'however']
        has_transitions = any(word in answer.lower() for word in transition_words)
        if has_transitions:
            score += 1.5
        
        return min(10.0, score)
    
    def evaluate_completeness(self, answer: str) -> float:
        """Evaluate if answer is complete and addresses multiple aspects"""
        score = 5.0
        
        words = answer.split()
        word_count = len(words)
        
        # Length-based scoring
        if word_count < 30:
            score = 3.0
        elif word_count < 60:
            score = 6.0
        elif word_count < 100:
            score = 8.0
        else:
            score = 9.0
        
        # Check for multiple aspects
        aspects = [
            'what', 'why', 'how', 'when', 'where',
            'advantage', 'disadvantage', 'benefit', 'challenge',
            'use case', 'example', 'alternative'
        ]
        
        covered_aspects = sum(1 for aspect in aspects if aspect in answer.lower())
        score += min(1.0, covered_aspects * 0.2)
        
        return min(10.0, score)
    
    def evaluate_relevance(self, question: str, answer: str) -> float:
        """Evaluate if answer is relevant to the question"""
        
        # Extract key terms from question
        question_lower = question.lower()
        answer_lower = answer.lower()
        
        # If question asks specific "what", "how", "why"
        if 'what is' in question_lower or 'what are' in question_lower:
            if 'is' in answer_lower or 'are' in answer_lower:
                score = 8.0
            else:
                score = 6.0
        elif 'how' in question_lower:
            action_words = ['by', 'using', 'through', 'via', 'with']
            if any(word in answer_lower for word in action_words):
                score = 8.0
            else:
                score = 6.0
        elif 'why' in question_lower:
            reason_words = ['because', 'since', 'due to', 'reason', 'therefore']
            if any(word in answer_lower for word in reason_words):
                score = 8.0
            else:
                score = 6.0
        else:
            score = 7.0
        
        # Check if answer goes off-topic
        if len(answer.split()) > 150:
            # Very long answers might be rambling
            score -= 1.0
        
        return max(0.0, min(10.0, score))
    
    def generate_feedback(self, scores: Dict, answer: str, question: str) -> str:
        """Generate detailed feedback based on scores"""
        
        feedback_parts = []
        
        # Overall assessment
        avg_score = sum(scores.values()) / len(scores)
        if avg_score >= 8:
            feedback_parts.append("Excellent answer! You demonstrated strong understanding.")
        elif avg_score >= 6:
            feedback_parts.append("Good answer with room for improvement.")
        elif avg_score >= 4:
            feedback_parts.append("Adequate answer, but lacks depth.")
        else:
            feedback_parts.append("Answer needs significant improvement.")
        
        # Specific feedback
        if scores['content_score'] < 6:
            feedback_parts.append("Consider adding more technical details and depth to your explanation.")
        
        if scores['structure_score'] < 6:
            feedback_parts.append("Improve answer structure by organizing your thoughts clearly with introduction, main points, and conclusion.")
        
        if scores['completeness_score'] < 6:
            feedback_parts.append("Provide a more complete answer by addressing multiple aspects of the question.")
        
        if scores['relevance_score'] < 6:
            feedback_parts.append("Stay more focused on directly answering the question asked.")
        
        # Positive reinforcement
        if scores['content_score'] >= 8:
            feedback_parts.append("Strong technical content!")
        if scores['structure_score'] >= 8:
            feedback_parts.append("Well-structured response!")
        
        # Suggestions
        word_count = len(answer.split())
        if word_count < 30:
            feedback_parts.append("Try to elaborate more with examples and details.")
        elif word_count > 150:
            feedback_parts.append("Consider being more concise and focused.")
        
        return " ".join(feedback_parts)