import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from sentence_transformers import SentenceTransformer
import numpy as np

class ResumeMatcher:
    def __init__(self):
        """Initialize NLP models for resume matching"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        try:
            # Sentence-BERT for semantic similarity
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        except:
            print("Warning: Sentence-BERT model not found. Install with: pip install sentence-transformers")
            self.sentence_model = None
        
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def match_candidates_to_job(self, job, candidates):
        """
        Match multiple candidates to a job posting
        Returns list of candidates with match scores
        """
        results = []
        
        for candidate in candidates:
            match_data = self.calculate_match_score(candidate, job)
            
            results.append({
                'candidateId': candidate.get('_id'),
                'candidateName': candidate.get('name', 'Unknown'),
                'email': candidate.get('email', ''),
                'matchScore': match_data['overallScore'],
                'skillsMatch': match_data['skillsScore'],
                'experienceMatch': match_data['experienceScore'],
                'educationMatch': match_data['educationScore'],
                'semanticMatch': match_data['semanticScore'],
                'matchedSkills': match_data['matchedSkills'],
                'missingSkills': match_data['missingSkills'],
                'breakdown': match_data
            })
        
        return results
    
    def calculate_match_score(self, candidate, job):
        """
        Calculate comprehensive match score between candidate and job
        Returns detailed breakdown of match
        """
        # Extract data
        resume_text = self._extract_resume_text(candidate)
        job_text = self._extract_job_text(job)
        
        candidate_skills = set([s.lower() for s in candidate.get('skills', [])])
        job_skills = set([s.lower() for s in self._extract_skills(job)])
        
        # Calculate different matching scores
        skills_score = self._calculate_skills_match(candidate_skills, job_skills)
        experience_score = self._calculate_experience_match(candidate, job)
        education_score = self._calculate_education_match(candidate, job)
        keyword_score = self._calculate_keyword_match(resume_text, job_text)
        semantic_score = self._calculate_semantic_match(resume_text, job_text)
        
        # Weighted overall score
        weights = {
            'skills': 0.35,
            'experience': 0.20,
            'education': 0.15,
            'keyword': 0.15,
            'semantic': 0.15
        }
        
        overall_score = (
            skills_score * weights['skills'] +
            experience_score * weights['experience'] +
            education_score * weights['education'] +
            keyword_score * weights['keyword'] +
            semantic_score * weights['semantic']
        )
        
        # Get matched and missing skills
        matched_skills = list(candidate_skills & job_skills)
        missing_skills = list(job_skills - candidate_skills)
        
        return {
            'overallScore': round(overall_score, 2),
            'skillsScore': round(skills_score, 2),
            'experienceScore': round(experience_score, 2),
            'educationScore': round(education_score, 2),
            'keywordScore': round(keyword_score, 2),
            'semanticScore': round(semantic_score, 2),
            'matchedSkills': matched_skills,
            'missingSkills': missing_skills,
            'weights': weights
        }
    
    def _extract_resume_text(self, candidate):
        """Extract all text from candidate profile"""
        text_parts = []
        
        # Add all relevant fields
        fields = ['summary', 'experience', 'education', 'projects', 'achievements']
        
        for field in fields:
            if field in candidate:
                if isinstance(candidate[field], str):
                    text_parts.append(candidate[field])
                elif isinstance(candidate[field], list):
                    text_parts.extend([str(item) for item in candidate[field]])
        
        # Add skills
        if 'skills' in candidate:
            text_parts.append(' '.join(candidate['skills']))
        
        return ' '.join(text_parts)
    
    def _extract_job_text(self, job):
        """Extract all text from job posting"""
        text_parts = []
        
        fields = ['description', 'requirements', 'responsibilities', 'qualifications']
        
        for field in fields:
            if field in job:
                if isinstance(job[field], str):
                    text_parts.append(job[field])
                elif isinstance(job[field], list):
                    text_parts.extend([str(item) for item in job[field]])
        
        return ' '.join(text_parts)
    
    def _extract_skills(self, job):
        """Extract skills from job posting"""
        skills = []
        
        # From explicit skills field
        if 'skills' in job:
            if isinstance(job['skills'], list):
                skills.extend(job['skills'])
            elif isinstance(job['skills'], str):
                skills.extend([s.strip() for s in job['skills'].split(',')])
        
        # From requirements
        if 'requirements' in job:
            req_text = job['requirements']
            if isinstance(req_text, str):
                # Extract skills from requirements text
                skills.extend(self._extract_skills_from_text(req_text))
        
        return list(set(skills))
    
    def _extract_skills_from_text(self, text):
        """Extract technical skills from text"""
        # Common technical skills patterns
        tech_keywords = [
            'python', 'java', 'javascript', 'react', 'node', 'sql', 'mongodb',
            'aws', 'azure', 'docker', 'kubernetes', 'git', 'machine learning',
            'data science', 'flask', 'django', 'spring', 'angular', 'vue',
            'tensorflow', 'pytorch', 'html', 'css', 'typescript', 'c++', 'c#',
            'php', 'ruby', 'go', 'rust', 'scala', 'kotlin', 'swift'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in tech_keywords:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _calculate_skills_match(self, candidate_skills, job_skills):
        """Calculate skills match percentage"""
        if not job_skills:
            return 100.0
        
        matched = len(candidate_skills & job_skills)
        total = len(job_skills)
        
        return (matched / total) * 100
    
    def _calculate_experience_match(self, candidate, job):
        """Calculate experience match score"""
        candidate_exp = candidate.get('experience', 0)
        
        # Extract required experience from job
        job_exp = self._extract_experience_requirement(job)
        
        if job_exp == 0:
            return 100.0
        
        if candidate_exp >= job_exp:
            return 100.0
        elif candidate_exp >= job_exp * 0.7:
            return 80.0
        elif candidate_exp >= job_exp * 0.5:
            return 60.0
        else:
            return (candidate_exp / job_exp) * 50
    
    def _extract_experience_requirement(self, job):
        """Extract experience requirement from job"""
        # Check explicit field
        if 'experienceRequired' in job:
            return job['experienceRequired']
        
        # Parse from text
        text = self._extract_job_text(job)
        
        # Look for patterns like "3+ years", "5-7 years"
        patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\s*-\s*\d+\s*years?',
            r'minimum\s+(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return 0
    
    def _calculate_education_match(self, candidate, job):
        """Calculate education match score"""
        candidate_edu = candidate.get('education', '').lower()
        job_text = self._extract_job_text(job).lower()
        
        education_levels = {
            'phd': 4,
            'doctorate': 4,
            'masters': 3,
            'msc': 3,
            'mba': 3,
            'bachelors': 2,
            'bsc': 2,
            'btech': 2,
            'be': 2,
            'diploma': 1
        }
        
        candidate_level = 0
        for edu, level in education_levels.items():
            if edu in candidate_edu:
                candidate_level = max(candidate_level, level)
        
        required_level = 0
        for edu, level in education_levels.items():
            if edu in job_text:
                required_level = max(required_level, level)
        
        if required_level == 0:
            return 100.0
        
        if candidate_level >= required_level:
            return 100.0
        elif candidate_level == required_level - 1:
            return 70.0
        else:
            return 40.0
    
    def _calculate_keyword_match(self, resume_text, job_text):
        """Calculate TF-IDF based keyword match"""
        try:
            # Fit TF-IDF
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([resume_text, job_text])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity * 100
        except:
            return 0.0
    
    def _calculate_semantic_match(self, resume_text, job_text):
        """Calculate semantic similarity using Sentence-BERT"""
        if not self.sentence_model:
            return 0.0
        
        try:
            # Generate embeddings
            resume_embedding = self.sentence_model.encode([resume_text])
            job_embedding = self.sentence_model.encode([job_text])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
            
            return similarity * 100
        except:
            return 0.0
    
    def get_skill_recommendations(self, candidate, job):
        """Get skill recommendations for candidate"""
        candidate_skills = set([s.lower() for s in candidate.get('skills', [])])
        job_skills = set([s.lower() for s in self._extract_skills(job)])
        
        missing_skills = list(job_skills - candidate_skills)
        
        return {
            'missingSkills': missing_skills,
            'prioritySkills': missing_skills[:5],  # Top 5 most important
            'recommendations': self._generate_skill_recommendations(missing_skills)
        }
    
    def _generate_skill_recommendations(self, missing_skills):
        """Generate learning recommendations for missing skills"""
        recommendations = []
        
        for skill in missing_skills[:5]:
            recommendations.append({
                'skill': skill,
                'resources': [
                    f"Coursera: {skill.title()} Course",
                    f"Udemy: Master {skill.title()}",
                    f"YouTube: {skill.title()} Tutorial"
                ]
            })
        
        return recommendations