import re
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
        """Parse resume text and extract ALL content"""
        sections = self._split_into_sections(text)
        
        return {
            "personal_info": self._extract_personal_info(text),
            "education": self._extract_education(sections.get('education', '')),
            "experience": self._extract_experience(sections.get('experience', '') or sections.get('work experience', '')),
            "projects": self._extract_projects(sections.get('projects', '')),
            "skills": self._extract_skills(sections.get('skills', '') or sections.get('technical skills', '')),
            "certifications": self._extract_certifications(sections.get('certifications', '')),
            "achievements": self._extract_achievements(sections.get('achievements', '') or sections.get('achievements and roles', '')),
            "research": self._extract_research(sections.get('research', ''))
        }
    
    def _split_into_sections(self, text):
        """Split resume into sections"""
        sections = {}
        section_keywords = [
            'education', 'experience', 'work experience', 
            'projects', 'skills', 'technical skills', 'certifications', 
            'achievements', 'achievements and roles', 'research'
        ]
        
        lines = text.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Check if it's a section header (short line matching keyword)
            is_header = False
            if len(line_stripped) < 40 and line_lower in section_keywords:
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content)
                current_section = line_lower
                section_content = []
                is_header = True
            
            if not is_header and current_section and line_stripped:
                section_content.append(line)
        
        # Save last section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content)
        
        return sections
    
    def _extract_personal_info(self, text):
        """Extract personal information"""
        info = {"name": "", "email": "", "phone": "", "location": "", "linkedin": "", "github": ""}
        
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            info['email'] = email_match.group(0)
        
        # Phone
        phone_match = re.search(r'[\+\d][\d\-\s]{9,}', text)
        if phone_match:
            info['phone'] = phone_match.group(0).strip()
        
        # LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
        if linkedin_match:
            info['linkedin'] = linkedin_match.group(0)
        
        # GitHub
        github_match = re.search(r'github\.com/[\w\-]+', text, re.IGNORECASE)
        if github_match:
            info['github'] = github_match.group(0)
        
        # Location
        location_match = re.search(r'Location:\s*([^\n]+)', text, re.IGNORECASE)
        if location_match:
            info['location'] = location_match.group(1).strip()
        
        # Name - first line that's not email/phone/location
        for line in lines[:10]:
            if len(line) > 3 and len(line) < 50:
                if not any(x in line.lower() for x in ['email', 'phone', 'location', '@', 'http', 'linkedin', 'github', ':']):
                    words = line.split()
                    if 2 <= len(words) <= 4:
                        info['name'] = line
                        break
        
        return info
    
    def _extract_education(self, text):
        """Extract education entries"""
        education = []
        if not text:
            return education
        
        # Split by main bullets (•)
        entries = re.split(r'\n•\s+', text)
        
        for entry in entries:
            if len(entry.strip()) < 10:
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
            
            lines = [l.strip() for l in entry.split('\n') if l.strip()]
            
            if not lines:
                continue
            
            # First line: Institution Location
            first_line = lines[0]
            # Remove any leading bullet
            first_line = re.sub(r'^[•◦\-]\s*', '', first_line)
            
            # Split by comma to get institution and location
            if ',' in first_line:
                parts = first_line.split(',', 1)
                edu['institution'] = parts[0].strip()
                edu['location'] = parts[1].strip()
            else:
                edu['institution'] = first_line.strip()
            
            # Second line usually has degree details
            full_text = ' '.join(lines)
            
            # Extract degree
            degree_patterns = [
                r'(Master of Science.*?(?:in [^,]+)?)',
                r'(Bachelor of Science.*?(?:in [^,]+)?)',
                r'(M\.Sc\..*?(?:in [^,]+)?)',
                r'(B\.Sc\..*?(?:in [^,]+)?)',
                r'(Higher Secondary Certificate.*?(?:in [^,]+)?)',
                r'(Secondary School Certificate.*?(?:in [^,]+)?)',
                r'(HSC.*?(?:in [^,]+)?)',
                r'(SSC.*?(?:in [^,]+)?)'
            ]
            
            for pattern in degree_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    deg_full = match.group(1).strip()
                    # Check if "in Field" is present
                    if ' in ' in deg_full:
                        deg_parts = deg_full.split(' in ', 1)
                        edu['degree'] = deg_parts[0].strip()
                        edu['field'] = deg_parts[1].strip().rstrip(',')
                    else:
                        edu['degree'] = deg_full
                    break
            
            # Extract CGPA
            cgpa_match = re.search(r'CGPA:\s*(\d+\.?\d*)', full_text, re.IGNORECASE)
            if cgpa_match:
                edu['cgpa'] = cgpa_match.group(1)
            
            # Extract percentage
            perc_match = re.search(r'(\d+)%', full_text)
            if perc_match:
                edu['percentage'] = perc_match.group(1) + '%'
            
            # Extract duration
            dur_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[–\-]+\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', full_text, re.IGNORECASE)
            if dur_match:
                edu['duration'] = dur_match.group(0)
            
            if edu['institution']:
                education.append(edu)
        
        return education
    
    def _extract_projects(self, text):
        """Extract projects"""
        projects = []
        if not text:
            return projects
        
        # Split by main project bullets (•)
        entries = re.split(r'\n•\s+', text)
        
        for entry in entries:
            if len(entry.strip()) < 15:
                continue
            
            project = {"name": "", "technologies": "", "description": []}
            
            lines = [l.strip() for l in entry.split('\n') if l.strip()]
            
            if not lines:
                continue
            
            # First line: Project Name | Tech:
            first_line = lines[0]
            first_line = re.sub(r'^[•]\s*', '', first_line)
            
            if '|' in first_line:
                parts = first_line.split('|', 1)
                project['name'] = parts[0].strip()
                project['technologies'] = parts[1].strip().rstrip(':')
            else:
                project['name'] = first_line.rstrip(':')
            
            # Rest are descriptions (with ◦ bullets)
            for line in lines[1:]:
                # Remove ◦ bullet
                desc_line = re.sub(r'^[◦○]\s*', '', line)
                if desc_line:
                    project['description'].append(desc_line)
            
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
        
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        for line in lines:
            # Remove bullet
            line = re.sub(r'^[•◦]\s*', '', line)
            
            if ':' not in line:
                continue
            
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
        certs = []
        if not text:
            return certs
        
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        for line in lines:
            # Remove bullet
            line = re.sub(r'^[•◦]\s*', '', line)
            if len(line) > 10:
                certs.append(line)
        
        return certs
    
    def _extract_achievements(self, text):
        """Extract achievements"""
        achievements = []
        if not text:
            return achievements
        
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        for line in lines:
            # Remove bullet
            line = re.sub(r'^[•◦]\s*', '', line)
            if len(line) > 15:
                achievements.append(line)
        
        return achievements
    
    def _extract_research(self, text):
        """Extract research"""
        research = []
        if not text:
            return research
        
        # Split by main bullets
        entries = re.split(r'\n•\s+', text)
        
        for entry in entries:
            if len(entry.strip()) < 20:
                continue
            
            res = {"title": "", "role": "", "date": "", "location": "", "details": []}
            
            lines = [l.strip() for l in entry.split('\n') if l.strip()]
            
            if not lines:
                continue
            
            # First line: Title Location
            first_line = lines[0]
            first_line = re.sub(r'^[•]\s*', '', first_line)
            
            # Check for date at end
            date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}$', first_line, re.IGNORECASE)
            if date_match:
                res['date'] = date_match.group(0)
                first_line = first_line[:date_match.start()].strip()
            
            # Split by comma for title and location
            if ',' in first_line:
                parts = first_line.split(',', 1)
                res['title'] = parts[0].strip()
                res['location'] = parts[1].strip()
            else:
                res['title'] = first_line
            
            # Look for role in second line
            if len(lines) > 1:
                second_line = lines[1]
                # Check if it's a role (not a detail with ◦)
                if not second_line.startswith('◦'):
                    res['role'] = second_line
                    start_idx = 2
                else:
                    start_idx = 1
            else:
                start_idx = 1
            
            # Rest are details
            for line in lines[start_idx:]:
                desc_line = re.sub(r'^[◦○]\s*', '', line)
                if desc_line:
                    res['details'].append(desc_line)
            
            if res['title']:
                research.append(res)
        
        return research
    
    def _extract_experience(self, text):
        """Extract experience"""
        experience = []
        if not text:
            return experience
        
        # Split by main bullets
        entries = re.split(r'\n•\s+', text)
        
        for entry in entries:
            if len(entry.strip()) < 15:
                continue
            
            exp = {"company": "", "title": "", "location": "", "duration": "", "responsibilities": []}
            
            lines = [l.strip() for l in entry.split('\n') if l.strip()]
            
            if not lines:
                continue
            
            # First line: Company Location
            first_line = lines[0]
            first_line = re.sub(r'^[•]\s*', '', first_line)
            
            # Check for duration at end
            dur_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[–\-]+\s*(Present|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})$', first_line, re.IGNORECASE)
            if dur_match:
                exp['duration'] = dur_match.group(0)
                first_line = first_line[:dur_match.start()].strip()
            
            if ',' in first_line:
                parts = first_line.split(',', 1)
                exp['company'] = parts[0].strip()
                exp['location'] = parts[1].strip()
            else:
                exp['company'] = first_line
            
            # Second line might be title
            if len(lines) > 1:
                second_line = lines[1]
                if not second_line.startswith('◦'):
                    exp['title'] = second_line
                    start_idx = 2
                else:
                    start_idx = 1
            else:
                start_idx = 1
            
            # Rest are responsibilities
            for line in lines[start_idx:]:
                resp_line = re.sub(r'^[◦○]\s*', '', line)
                if resp_line:
                    exp['responsibilities'].append(resp_line)
            
            if exp['company']:
                experience.append(exp)
        
        return experience