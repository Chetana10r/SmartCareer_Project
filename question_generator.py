# question_generator.py
import json
import os
import random
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class QuestionGenerator:
    """Generate interview questions using templates and LLM (optional)"""
    
    def __init__(self):
        self.load_question_templates()
        self.llm_available = self.initialize_llm()
    
    def load_question_templates(self):
        """Load question templates from JSON file"""
        template_path = 'config/question_templates.json'
        
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                self.templates = json.load(f)
        else:
            # Default templates
            self.templates = {
                "technical": {
                    "easy": [
                        "What is {concept}? Can you explain it in simple terms?",
                        "What are the main differences between {concept1} and {concept2}?",
                        "How would you explain {concept} to a non-technical person?",
                        "What are the basic principles of {concept}?",
                        "Can you describe a simple use case for {concept}?"
                    ],
                    "medium": [
                        "How would you implement {concept} in a real-world project?",
                        "What are the advantages and disadvantages of using {concept}?",
                        "Can you explain the internal working of {concept}?",
                        "How does {concept} improve performance or efficiency?",
                        "What best practices should be followed when using {concept}?"
                    ],
                    "hard": [
                        "How would you optimize {concept} for large-scale systems?",
                        "Can you compare {concept1} and {concept2} in terms of scalability and performance?",
                        "What are the potential bottlenecks when implementing {concept}?",
                        "How would you debug a performance issue related to {concept}?",
                        "Design a system that uses {concept} to solve {problem}."
                    ]
                },
                "hr": {
                    "easy": [
                        "Tell me about yourself and your background.",
                        "Why are you interested in this role?",
                        "What are your key strengths?",
                        "How do you handle stress and pressure?",
                        "What motivates you in your work?"
                    ],
                    "medium": [
                        "Describe a challenging situation you faced at work and how you handled it.",
                        "Tell me about a time when you had to work with a difficult team member.",
                        "How do you prioritize tasks when you have multiple deadlines?",
                        "Describe a project where you took initiative.",
                        "How do you handle constructive criticism?"
                    ],
                    "hard": [
                        "Tell me about a time when you failed and what you learned from it.",
                        "Describe a situation where you had to make a difficult decision with limited information.",
                        "How have you handled a situation where your team disagreed with your approach?",
                        "Tell me about a time when you had to adapt to significant changes at work.",
                        "Describe how you've handled conflicting priorities from multiple stakeholders."
                    ]
                }
            }
    
    def initialize_llm(self) -> bool:
        """Initialize LLM for dynamic question generation (optional)"""
        try:
            # Try to load local LLM (like LLaMA or Mistral)
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Lightweight model
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            logger.info("LLM initialized successfully")
            return True
            
        except Exception as e:
            logger.warning(f"LLM not available, using templates: {e}")
            return False
    
    def generate_questions(
        self,
        job_role: str,
        interview_type: str,
        difficulty: str,
        num_questions: int = 5,
        resume_context: Optional[str] = None
    ) -> List[str]:
        """Generate interview questions"""
        
        questions = []
        
        # Role-specific concepts
        concepts = self.get_concepts_for_role(job_role, interview_type)
        
        if interview_type == 'mixed':
            # Mix technical and HR questions
            tech_count = num_questions // 2
            hr_count = num_questions - tech_count
            
            questions.extend(
                self.generate_typed_questions('technical', difficulty, tech_count, concepts)
            )
            questions.extend(
                self.generate_typed_questions('hr', difficulty, hr_count, concepts)
            )
            random.shuffle(questions)
        else:
            questions = self.generate_typed_questions(
                interview_type, difficulty, num_questions, concepts
            )
        
        # If resume provided, add personalized question
        if resume_context and len(questions) > 0:
            personalized_q = self.generate_resume_question(resume_context, job_role)
            questions[-1] = personalized_q
        
        return questions[:num_questions]
    
    def generate_typed_questions(
        self,
        question_type: str,
        difficulty: str,
        count: int,
        concepts: dict
    ) -> List[str]:
        """Generate questions of specific type"""
        
        questions = []
        templates = self.templates.get(question_type, {}).get(difficulty, [])
        
        if not templates:
            templates = self.templates.get(question_type, {}).get('medium', [])
        
        for _ in range(count):
            template = random.choice(templates)
            
            # Fill template with concepts
            if '{concept}' in template:
                concept = random.choice(concepts.get('main', ['software development']))
                template = template.replace('{concept}', concept)
            
            if '{concept1}' in template and '{concept2}' in template:
                concept_list = concepts.get('main', ['arrays', 'lists'])
                if len(concept_list) >= 2:
                    c1, c2 = random.sample(concept_list, 2)
                    template = template.replace('{concept1}', c1).replace('{concept2}', c2)
            
            if '{problem}' in template:
                problem = random.choice(concepts.get('problems', ['data processing']))
                template = template.replace('{problem}', problem)
            
            questions.append(template)
        
        return questions
    
    def get_concepts_for_role(self, job_role: str, interview_type: str) -> dict:
        """Get relevant concepts for the job role"""
        
        role_concepts = {
            'data scientist': {
                'main': ['machine learning', 'neural networks', 'data preprocessing', 
                        'feature engineering', 'model evaluation', 'cross-validation'],
                'problems': ['classification', 'regression', 'clustering', 'anomaly detection']
            },
            'software engineer': {
                'main': ['object-oriented programming', 'design patterns', 'algorithms',
                        'data structures', 'REST APIs', 'databases'],
                'problems': ['system design', 'code optimization', 'scalability']
            },
            'machine learning engineer': {
                'main': ['deep learning', 'PyTorch', 'TensorFlow', 'model deployment',
                        'MLOps', 'hyperparameter tuning'],
                'problems': ['model optimization', 'production deployment', 'A/B testing']
            },
            'frontend developer': {
                'main': ['React', 'JavaScript', 'CSS', 'HTML', 'state management', 'hooks'],
                'problems': ['responsive design', 'performance optimization', 'accessibility']
            },
            'backend developer': {
                'main': ['databases', 'APIs', 'microservices', 'caching', 'authentication'],
                'problems': ['scalability', 'load balancing', 'database optimization']
            }
        }
        
        # Default to software engineer if role not found
        role_key = job_role.lower()
        return role_concepts.get(role_key, role_concepts['software engineer'])
    
    def generate_resume_question(self, resume_context: str, job_role: str) -> str:
        """Generate question based on resume context"""
        
        # Simple keyword extraction
        keywords = resume_context.lower().split()
        tech_keywords = ['python', 'java', 'machine learning', 'tensorflow', 
                        'react', 'api', 'database', 'cloud', 'aws']
        
        found_skills = [kw for kw in tech_keywords if kw in keywords]
        
        if found_skills:
            skill = random.choice(found_skills)
            return f"I see you have experience with {skill}. Can you describe a challenging project where you used {skill} and how you overcame the challenges?"
        else:
            return "Can you walk me through your most significant project and the technical decisions you made?"
    
    def generate_with_llm(self, prompt: str) -> str:
        """Generate question using LLM (if available)"""
        
        if not self.llm_available:
            return None
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            outputs = self.model.generate(
                **inputs,
                max_length=200,
                temperature=0.7,
                do_sample=True
            )
            question = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return question.strip()
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return None