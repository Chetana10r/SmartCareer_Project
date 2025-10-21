import re
from datetime import datetime
import spacy

class ResumeParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
    
    def parse_resume(self, text):
        """Parse resume text and extract structured information"""
        sections = self._split_into_sections(text)
        
        return {
            "personal_info": self._extract_personal_info(text),
            "education": self._extract_education(sections.get('education', '')),
            "experience": self._extract_experience(sections.get('experience', '')),
            "projects": self._extract_projects(sections.get('projects', '')),
            "skills": self._extract_skills(sections.get('skills', '') or sections.get('technical skills', '')),
            "certifications": self._extract_certifications(sections.get('certifications', '')),
            "achievements": self._extract_achievements(sections.get('achievements', '') or sections.get('achievements and roles', '')),
            "research": self._extract_research(sections.get('research', ''))
        }
    
    def _split_into_sections(self, text):
        """Split resume into sections"""
        sections = {}
        
        # Common section headers
        section_keywords = [
            'education', 'experience', 'work experience', 'projects', 
            'skills', 'technical skills', 'certifications', 'achievements',
            'achievements and roles', 'research', 'publications'
        ]
        
        lines = text.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            line_lower = line.strip().lower()
            
            # Check if line is a section header
            is_header = False
            for keyword in section_keywords:
                if line_lower == keyword or (len(line_lower) < 30 and keyword in line_lower):
                    # Save previous section
                    if current_section and section_content:
                        sections[current_section] = '\n'.join(section_content)
                    
                    current_section = keyword
                    section_content = []
                    is_header = True
                    break
            
            if not is_header and current_section:
                section_content.append(line)
        
        # Save last section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content)
        
        return sections
    
    def _extract_personal_info(self, text):
        """Extract name, email, phone, location"""
        info = {
            "name": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin": "",
            "github": ""
        }
        
        # Extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            info['email'] = email_match.group(0)
        
        # Extract phone
        phone_match = re.search(r'[\+\d][\d\-\(\)\s]{8,15}', text)
        if phone_match:
            info['phone'] = phone_match.group(0).strip()
        
        # Extract LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
        if linkedin_match:
            info['linkedin'] = linkedin_match.group(0)
        
        # Extract GitHub
        github_match = re.search(r'github\.com/[\w\-]+', text, re.IGNORECASE)
        if github_match:
            info['github'] = github_match.group(0)
        
        # Extract name (usually first line or near email)
        lines = text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if len(line) > 3 and len(line) < 50:
                if '@' not in line and '+' not in line and 'http' not in line.lower():
                    # Check if it looks like a name (2-4 words, capitalized)
                    words = line.split()
                    if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
                        info['name'] = line
                        break
        
        # Extract location
        location_keywords = ['location:', 'address:', 'city:']
        for line in lines[:15]:
            line_lower = line.lower()
            for keyword in location_keywords:
                if keyword in line_lower:
                    info['location'] = line.split(':', 1)[1].strip()
                    break
        
        # Fallback: look for city, country pattern
        if not info['location']:
            location_match = re.search(r'([A-Z][a-z]+,\s*[A-Z][a-z]+)', text)
            if location_match:
                info['location'] = location_match.group(0)
        
        return info
    
    def _extract_education(self, text):
        """Extract education details"""
        education = []
        
        if not text:
            return education
        
        # Split by bullet points or degree patterns
        entries = re.split(r'\n•|\n◦|\n-|\n\d+\.', text)
        
        for entry in entries:
            entry = entry.strip()
            if len(entry) < 10:
                continue
            
            edu = {
                "institution": "",
                "degree": "",
                "field": "",
                "cgpa": "",
                "percentage": "",
                "duration": "",
                "location": ""
            }
            
            lines = entry.split('\n')
            
            # First line usually has institution
            if lines:
                first_line = lines[0].strip()
                # Extract institution and location
                parts = first_line.split(',')
                if len(parts) >= 2:
                    edu['institution'] = parts[0].strip()
                    edu['location'] = ', '.join(parts[1:]).strip()
                else:
                    edu['institution'] = first_line
            
            # Look for degree
            degree_patterns = [
                r'(Bachelor|Master|B\.?Sc\.?|M\.?Sc\.?|B\.?Tech|M\.?Tech|B\.?E\.?|M\.?E\.?|PhD|Diploma).*',
                r'(HSC|SSC|Higher Secondary|Secondary School).*'
            ]
            for line in lines:
                for pattern in degree_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        degree_text = match.group(0)
                        # Extract field if present
                        field_match = re.search(r'in\s+([A-Z][^,\n]+)', degree_text, re.IGNORECASE)
                        if field_match:
                            edu['field'] = field_match.group(1).strip()
                            edu['degree'] = degree_text.split('in')[0].strip()
                        else:
                            edu['degree'] = degree_text.strip()
                        break
            
            # Look for CGPA/Percentage
            cgpa_match = re.search(r'CGPA[:\s]+(\d+\.?\d*)', entry, re.IGNORECASE)
            if cgpa_match:
                edu['cgpa'] = cgpa_match.group(1)
            
            percent_match = re.search(r'(\d+\.?\d*)%', entry)
            if percent_match:
                edu['percentage'] = percent_match.group(1) + '%'
            
            # Look for duration
            date_patterns = [
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[–-]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',
                r'\d{4}\s*[–-]\s*\d{4}',
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[–-]\s*Present'
            ]
            for pattern in date_patterns:
                match = re.search(pattern, entry, re.IGNORECASE)
                if match:
                    edu['duration'] = match.group(0)
                    break
            
            if edu['institution'] or edu['degree']:
                education.append(edu)
        
        return education
    
    def _extract_experience(self, text):
        """Extract work experience"""
        experience = []
        
        if not text:
            return experience
        
        entries = re.split(r'\n•|\n◦|\n-', text)
        
        for entry in entries:
            entry = entry.strip()
            if len(entry) < 20:
                continue
            
            exp = {
                "company": "",
                "title": "",
                "location": "",
                "duration": "",
                "responsibilities": []
            }
            
            lines = [l.strip() for l in entry.split('\n') if l.strip()]
            
            if not lines:
                continue
            
            # First line: company and location
            first_line = lines[0]
            parts = first_line.split(',')
            exp['company'] = parts[0].strip()
            if len(parts) > 1:
                exp['location'] = parts[-1].strip()
            
            # Look for job title and duration
            for line in lines[1:]:
                # Check for duration
                date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[–-]\s*(Present|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})', line, re.IGNORECASE)
                if date_match:
                    exp['duration'] = date_match.group(0)
                    # Title is usually before the date
                    exp['title'] = line.split(date_match.group(0))[0].strip()
                elif not exp['title'] and len(line) < 100:
                    exp['title'] = line
                else:
                    # Responsibility bullet point
                    clean_line = re.sub(r'^[◦○▪▫●•]\s*', '', line)
                    if clean_line:
                        exp['responsibilities'].append(clean_line)
            
            if exp['company']:
                experience.append(exp)
        
        return experience
    
    def _extract_projects(self, text):
        """Extract projects"""
        projects = []
        
        if not text:
            return projects
        
        entries = re.split(r'\n•(?=\s*[A-Z])', text)
        
        for entry in entries:
            entry = entry.strip()
            if len(entry) < 20:
                continue
            
            project = {
                "name": "",
                "technologies": "",
                "description": []
            }
            
            lines = [l.strip() for l in entry.split('\n') if l.strip()]
            
            if not lines:
                continue
            
            # First line: project name and technologies
            first_line = lines[0]
            if '|' in first_line:
                parts = first_line.split('|')
                project['name'] = parts[0].strip()
                project['technologies'] = parts[1].strip().rstrip(':')
            else:
                # Look for colon
                if ':' in first_line:
                    parts = first_line.split(':')
                    project['name'] = parts[0].strip()
                else:
                    project['name'] = first_line
            
            # Remaining lines are descriptions
            for line in lines[1:]:
                clean_line = re.sub(r'^[◦○▪▫●•]\s*', '', line)
                if clean_line and len(clean_line) > 10:
                    project['description'].append(clean_line)
            
            if project['name']:
                projects.append(project)
        
        return projects
    
    def _extract_skills(self, text):
        """Extract skills"""
        skills = {
            "programming": "",
            "ml_ds": "",
            "libraries": "",
            "databases": "",
            "platforms": ""
        }
        
        if not text:
            return skills
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Remove bullet points
            line = re.sub(r'^[•◦○▪▫●-]\s*', '', line)
            
            # Parse category: skills format
            if ':' in line:
                parts = line.split(':', 1)
                category = parts[0].strip().lower()
                skills_text = parts[1].strip()
                
                if 'programming' in category or 'language' in category:
                    skills['programming'] = skills_text
                elif 'machine learning' in category or 'data science' in category:
                    skills['ml_ds'] = skills_text
                elif 'framework' in category or 'libraries' in category:
                    skills['libraries'] = skills_text
                elif 'database' in category or 'tool' in category:
                    skills['databases'] = skills_text
                elif 'platform' in category or 'operating' in category:
                    skills['platforms'] = skills_text
        
        return skills
    
    def _extract_certifications(self, text):
        """Extract certifications"""
        certifications = []
        
        if not text:
            return certifications
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Remove bullet points
            line = re.sub(r'^[•◦○▪▫●-]\s*', '', line)
            certifications.append(line)
        
        return certifications
    
    def _extract_achievements(self, text):
        """Extract achievements"""
        achievements = []
        
        if not text:
            return achievements
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 15:
                continue
            
            # Remove bullet points
            line = re.sub(r'^[•◦○▪▫●-]\s*', '', line)
            achievements.append(line)
        
        return achievements
    
    def _extract_research(self, text):
        """Extract research/publications"""
        research = []
        
        if not text:
            return research
        
        entries = re.split(r'\n•', text)
        
        for entry in entries:
            entry = entry.strip()
            if len(entry) < 30:
                continue
            
            res = {
                "title": "",
                "role": "",
                "date": "",
                "location": "",
                "details": []
            }
            
            lines = [l.strip() for l in entry.split('\n') if l.strip()]
            
            if lines:
                # First line: title and location
                first_line = lines[0]
                parts = first_line.split(',')
                res['title'] = parts[0].strip()
                if len(parts) > 1:
                    res['location'] = parts[-1].strip()
                
                # Look for role and date
                for line in lines[1:]:
                    date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', line, re.IGNORECASE)
                    if date_match:
                        res['date'] = date_match.group(0)
                        res['role'] = line.split(date_match.group(0))[0].strip()
                    else:
                        clean_line = re.sub(r'^[◦○▪▫●•]\s*', '', line)
                        if clean_line:
                            res['details'].append(clean_line)
            
            if res['title']:
                research.append(res)
        
        return research