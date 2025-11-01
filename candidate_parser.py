import re
import PyPDF2
import docx2txt
import spacy
from typing import Dict, List

class CandidateParser:
    def __init__(self):
        """Initialize resume parser with NLP models"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Common skill patterns
        self.tech_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node',
            'sql', 'mongodb', 'postgresql', 'mysql', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes',
            'machine learning', 'deep learning', 'data science',
            'flask', 'django', 'spring boot', 'express',
            'html', 'css', 'typescript', 'c++', 'c#', 'php', 'ruby',
            'git', 'ci/cd', 'agile', 'scrum',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy'
        ]
    
    def parse_resume(self, file_path: str) -> Dict:
        """
        Parse resume file and extract information
        
        Args:
            file_path: Path to resume file
        
        Returns:
            Dictionary with extracted resume data
        """
        # Extract text based on file type
        text = self._extract_text(file_path)
        
        if not text:
            return {'error': 'Could not extract text from file'}
        
        # Parse information
        parsed_data = {
            'rawText': text,
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'skills': self._extract_skills(text),
            'experience': self._extract_experience(text),
            'education': self._extract_education(text),
            'summary': self._extract_summary(text),
            'github': self._extract_github(text),
            'linkedin': self._extract_linkedin(text)
        }
        
        return parsed_data
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX file"""
        if file_path.lower().endswith('.pdf'):
            return self._extract_from_pdf(file_path)
        elif file_path.lower().endswith(('.docx', '.doc')):
            return self._extract_from_docx(file_path)
        else:
            return ''
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            text = ''
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return ''
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            return docx2txt.process(file_path)
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
            return ''
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name"""
        if not self.nlp:
            # Fallback: Get first line
            lines = text.strip().split('\n')
            return lines[0].strip() if lines else 'Unknown'
        
        # Use NLP to find person names
        doc = self.nlp(text[:500])  # First 500 chars
        
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                return ent.text
        
        # Fallback
        lines = text.strip().split('\n')
        return lines[0].strip() if lines else 'Unknown'
    
    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else ''
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        # Various phone formats
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # +1-234-567-8900
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (234) 567-8900
            r'\d{10}',  # 2345678900
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        return ''
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills"""
        text_lower = text.lower()
        found_skills = []
        
        # Check for each known skill
        for skill in self.tech_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        # Also extract from skills section if exists
        skills_section = self._extract_section(text, 'skills')
        if skills_section:
            # Split by common delimiters
            additional_skills = re.split(r'[,|•\n]', skills_section)
            for skill in additional_skills:
                skill = skill.strip()
                if skill and len(skill) > 2 and skill not in found_skills:
                    found_skills.append(skill.title())
        
        return list(set(found_skills))
    
    def _extract_experience(self, text: str) -> int:
        """Extract years of experience"""
        # Look for patterns like "5 years", "3+ years"
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience[:\s]+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s+(?:of\s+)?exp'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                return int(matches[0])
        
        # Try to estimate from experience section
        exp_section = self._extract_section(text, 'experience')
        if exp_section:
            # Count date ranges (approximate)
            year_pattern = r'(19|20)\d{2}'
            years = re.findall(year_pattern, exp_section)
            if len(years) >= 2:
                try:
                    return max(int(years[0]), int(years[-1])) - min(int(years[0]), int(years[-1]))
                except:
                    pass
        
        return 0
    
    def _extract_education(self, text: str) -> str:
        """Extract education information"""
        edu_section = self._extract_section(text, 'education')
        
        if edu_section:
            return edu_section.strip()
        
        # Look for degree keywords
        degrees = [
            'phd', 'doctorate', 'ph.d',
            'master', 'msc', 'm.sc', 'mba', 'm.b.a',
            'bachelor', 'bsc', 'b.sc', 'btech', 'b.tech', 'be', 'b.e',
            'diploma'
        ]
        
        text_lower = text.lower()
        for degree in degrees:
            if degree in text_lower:
                # Extract surrounding context
                idx = text_lower.index(degree)
                return text[max(0, idx-50):idx+100].strip()
        
        return 'Not specified'
    
    def _extract_summary(self, text: str) -> str:
        """Extract professional summary"""
        summary_section = self._extract_section(text, 'summary')
        
        if summary_section:
            return summary_section.strip()
        
        # Get first few lines as summary
        lines = text.strip().split('\n')
        summary_lines = []
        
        for i, line in enumerate(lines[1:10]):  # Skip name line
            line = line.strip()
            if line and len(line) > 20:
                summary_lines.append(line)
            if len(summary_lines) >= 3:
                break
        
        return ' '.join(summary_lines)
    
    def _extract_github(self, text: str) -> str:
        """Extract GitHub profile URL"""
        github_pattern = r'github\.com/[\w-]+'
        matches = re.findall(github_pattern, text.lower())
        return f"https://{matches[0]}" if matches else ''
    
    def _extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn profile URL"""
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        matches = re.findall(linkedin_pattern, text.lower())
        return f"https://{matches[0]}" if matches else ''
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from resume"""
        # Common section headers
        section_headers = {
            'skills': ['skills', 'technical skills', 'core competencies', 'expertise'],
            'experience': ['experience', 'work experience', 'employment', 'professional experience'],
            'education': ['education', 'academic', 'qualification'],
            'summary': ['summary', 'profile', 'objective', 'about']
        }
        
        headers = section_headers.get(section_name, [section_name])
        
        text_lower = text.lower()
        lines = text.split('\n')
        
        # Find section start
        start_idx = -1
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(header in line_lower for header in headers):
                start_idx = i + 1
                break
        
        if start_idx == -1:
            return ''
        
        # Find section end (next section or end of text)
        end_idx = len(lines)
        all_headers = [h for headers in section_headers.values() for h in headers]
        
        for i in range(start_idx, len(lines)):
            line_lower = lines[i].lower().strip()
            if any(header in line_lower for header in all_headers):
                end_idx = i
                break
        
        # Extract section content
        section_lines = lines[start_idx:end_idx]
        return '\n'.join(line.strip() for line in section_lines if line.strip())
    
    def validate_resume(self, parsed_data: Dict) -> Dict:
        """Validate parsed resume data"""
        validation = {
            'isValid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required fields
        if not parsed_data.get('name') or parsed_data['name'] == 'Unknown':
            validation['warnings'].append('Name not found')
        
        if not parsed_data.get('email'):
            validation['errors'].append('Email address missing')
            validation['isValid'] = False
        
        if not parsed_data.get('skills'):
            validation['warnings'].append('No skills found')
        
        if not parsed_data.get('experience'):
            validation['warnings'].append('Experience not specified')
        
        return validation