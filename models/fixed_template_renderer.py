import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from datetime import datetime
import os

class FixedTemplateRenderer:
    def __init__(self, template_path="templates/fixed_resume_template.json"):
        try:
            with open(template_path, 'r') as f:
                self.template = json.load(f)
        except FileNotFoundError:
            # Use default template if file not found
            self.template = self._get_default_template()
        self.styles = self._create_custom_styles()

    def _get_default_template(self):
        """Fallback template matching Chetana's format"""
        return {
            "typography": {
                "fonts": {
                    "name": "Helvetica-Bold", 
                    "heading": "Helvetica-Bold", 
                    "subheading": "Helvetica-Bold",
                    "body": "Helvetica"
                },
                "sizes": {
                    "name": 16, 
                    "contact": 10, 
                    "heading": 12,
                    "section_header": 12, 
                    "subheading": 11,
                    "body": 10
                }
            },
            "colors": {"primary": "#000000"},
            "layout_settings": {
                "margins": {"top": 0.6, "bottom": 0.6, "left": 0.75, "right": 0.75}, 
                "line_spacing": 1.15,
                "section_spacing": 0.15
            }
        }

    def _create_custom_styles(self):
        styles = {}
        
        # Name style (Bold, larger)
        styles['Name'] = ParagraphStyle(
            'Name',
            fontName='Helvetica-Bold',
            fontSize=self.template['typography']['sizes']['name'],
            alignment=TA_LEFT,
            spaceAfter=2,
            leading=16
        )

        # Contact info style
        styles['Contact'] = ParagraphStyle(
            'Contact',
            fontName='Helvetica',
            fontSize=self.template['typography']['sizes']['contact'],
            alignment=TA_LEFT,
            spaceAfter=1,
            leading=12
        )

        # Section header style (Bold)
        styles['SectionHeader'] = ParagraphStyle(
            'SectionHeader',
            fontName='Helvetica-Bold',
            fontSize=self.template['typography']['sizes']['section_header'],
            alignment=TA_LEFT,
            spaceBefore=12,
            spaceAfter=6,
            leading=14
        )

        # Body text style
        styles['Body'] = ParagraphStyle(
            'Body',
            fontName='Helvetica',
            fontSize=self.template['typography']['sizes']['body'],
            alignment=TA_LEFT,
            leftIndent=15,
            spaceAfter=4,
            leading=12
        )

        # Sub-bullet style (deeper indent)
        styles['SubBullet'] = ParagraphStyle(
            'SubBullet',
            fontName='Helvetica',
            fontSize=self.template['typography']['sizes']['body'],
            alignment=TA_LEFT,
            leftIndent=30,
            spaceAfter=4,
            leading=12
        )

        # Institution/Company header
        styles['InstitutionHeader'] = ParagraphStyle(
            'InstitutionHeader',
            fontName='Helvetica-Bold',
            fontSize=self.template['typography']['sizes']['body'],
            alignment=TA_LEFT,
            leftIndent=15,
            spaceAfter=2,
            leading=12
        )

        # Project/Position title
        styles['ProjectTitle'] = ParagraphStyle(
            'ProjectTitle',
            fontName='Helvetica-Bold',
            fontSize=self.template['typography']['sizes']['body'],
            alignment=TA_LEFT,
            leftIndent=15,
            spaceAfter=2,
            leading=12
        )

        return styles

    def render_resume(self, resume_data, output_path=None):
        """Generate PDF resume from data"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs('static', exist_ok=True)
            output_path = f"static/resume_{timestamp}.pdf"

        margins = self.template['layout_settings']['margins']
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=margins['right']*inch,
            leftMargin=margins['left']*inch,
            topMargin=margins['top']*inch,
            bottomMargin=margins['bottom']*inch
        )

        story = []
        
        # Render sections in order
        self._render_header(story, resume_data)
        self._render_education(story, resume_data)
        self._render_projects(story, resume_data)
        self._render_research(story, resume_data)
        self._render_technical_skills(story, resume_data)
        self._render_certifications(story, resume_data)
        self._render_achievements(story, resume_data)
        self._render_experience(story, resume_data)

        doc.build(story)
        return output_path

    def _render_header(self, story, data):
        """Render name and contact info"""
        personal_info = data.get('personal_info', {})
        
        # Name
        name = personal_info.get('name', 'Full Name')
        phone = personal_info.get('phone', '+91-XXXXXXXXXX')
        story.append(Paragraph(f"<b>{name}</b> {phone}", self.styles['Name']))
        
        # Email line
        email = personal_info.get('email', 'email@example.com')
        location = personal_info.get('location', 'City, Country')
        story.append(Paragraph(f"Email: {email}  Location: {location}", self.styles['Contact']))
        
        # LinkedIn and GitHub
        linkedin = personal_info.get('linkedin', '')
        github = personal_info.get('github', '')
        links = []
        if linkedin:
            links.append(f"LinkedIn: {linkedin}")
        if github:
            links.append(f"GitHub: {github}")
        
        if links:
            story.append(Paragraph("  ".join(links), self.styles['Contact']))
        
        story.append(Spacer(1, 8))

    def _render_education(self, story, data):
        """Render education section"""
        education = data.get('education', [])
        if not education:
            return
        
        story.append(Paragraph("<b>Education</b>", self.styles['SectionHeader']))
        
        for edu in education:
            institution = edu.get('institution', '')
            location = edu.get('location', '')
            degree = edu.get('degree', '')
            field = edu.get('field', '')
            cgpa = edu.get('cgpa', '')
            duration = edu.get('duration', '')
            percentage = edu.get('percentage', '')
            
            # Institution and location
            inst_line = f"<b>{institution}</b>"
            if location:
                inst_line += f" {location}"
            story.append(Paragraph(f"• {inst_line}", self.styles['Body']))
            
            # Degree details
            degree_line = degree
            if field:
                degree_line += f" in {field}"
            if cgpa:
                degree_line += f", CGPA: {cgpa}"
            elif percentage:
                degree_line += f", {percentage}"
            if duration:
                degree_line += f" {duration}"
            
            story.append(Paragraph(degree_line, self.styles['Body']))
        
        story.append(Spacer(1, 6))

    def _render_projects(self, story, data):
        """Render projects section"""
        projects = data.get('projects', [])
        if not projects:
            return
        
        story.append(Paragraph("<b>Projects</b>", self.styles['SectionHeader']))
        
        for project in projects:
            title = project.get('name', '')
            tech_stack = project.get('technologies', '')
            description = project.get('description', [])
            
            # Project title with tech stack
            if isinstance(tech_stack, list):
                tech_stack = ', '.join(tech_stack)
            
            project_header = f"<b>{title}</b>"
            if tech_stack:
                project_header += f" | {tech_stack}"
            
            story.append(Paragraph(f"• {project_header}:", self.styles['Body']))
            
            # Project details as sub-bullets
            if isinstance(description, str):
                description = [description]
            
            for detail in description:
                story.append(Paragraph(f"◦ {detail}", self.styles['SubBullet']))
        
        story.append(Spacer(1, 6))

    def _render_research(self, story, data):
        """Render research section"""
        research = data.get('research', [])
        if not research:
            return
        
        story.append(Paragraph("<b>Research</b>", self.styles['SectionHeader']))
        
        for item in research:
            title = item.get('title', '')
            location = item.get('location', '')
            role = item.get('role', '')
            date = item.get('date', '')
            details = item.get('details', [])
            
            # Research header
            header = f"<b>{title}</b>"
            if location:
                header += f" {location}"
            story.append(Paragraph(f"• {header}", self.styles['Body']))
            
            # Role and date
            if role:
                role_line = role
                if date:
                    role_line += f" {date}"
                story.append(Paragraph(role_line, self.styles['Body']))
            
            # Details
            if isinstance(details, str):
                details = [details]
            
            for detail in details:
                story.append(Paragraph(f"◦ {detail}", self.styles['SubBullet']))
        
        story.append(Spacer(1, 6))

    def _render_technical_skills(self, story, data):
        """Render technical skills section"""
        skills = data.get('skills', {})
        if not skills:
            return
        
        story.append(Paragraph("<b>Technical Skills</b>", self.styles['SectionHeader']))
        
        # Handle both dict and list formats
        if isinstance(skills, list):
            skills_text = ", ".join(skills)
            story.append(Paragraph(f"• <b>Technical:</b> {skills_text}", self.styles['Body']))
        elif isinstance(skills, dict):
            # Predefined category order
            categories = [
                ('programming', 'Programming & Languages'),
                ('ml_ds', 'Machine Learning & Data Science'),
                ('libraries', 'Libraries & Frameworks'),
                ('databases', 'Databases & Tools'),
                ('platforms', 'Platforms & Operating Systems')
            ]
            
            for key, label in categories:
                if key in skills and skills[key]:
                    if isinstance(skills[key], list):
                        skills_text = ", ".join(skills[key])
                    else:
                        skills_text = skills[key]
                    story.append(Paragraph(f"• <b>{label}:</b> {skills_text}", self.styles['Body']))
        
        story.append(Spacer(1, 6))

    def _render_certifications(self, story, data):
        """Render certifications section"""
        certifications = data.get('certifications', [])
        if not certifications:
            return
        
        story.append(Paragraph("<b>Certifications</b>", self.styles['SectionHeader']))
        
        for cert in certifications:
            if isinstance(cert, str):
                story.append(Paragraph(f"• {cert}", self.styles['Body']))
            else:
                name = cert.get('name', '')
                issuer = cert.get('issuer', '')
                year = cert.get('year', '')
                description = cert.get('description', '')
                
                cert_line = f"<b>{name}</b>"
                if year:
                    cert_line += f" ({year})"
                cert_line += ": "
                if description:
                    cert_line += description
                elif issuer:
                    cert_line += issuer
                
                story.append(Paragraph(f"• {cert_line}", self.styles['Body']))
        
        story.append(Spacer(1, 6))

    def _render_achievements(self, story, data):
        """Render achievements and roles section"""
        achievements = data.get('achievements', [])
        if not achievements:
            return
        
        story.append(Paragraph("<b>Achievements and Roles</b>", self.styles['SectionHeader']))
        
        for achievement in achievements:
            if isinstance(achievement, str):
                story.append(Paragraph(f"• {achievement}", self.styles['Body']))
            else:
                title = achievement.get('title', '')
                description = achievement.get('description', '')
                text = title if title else description
                story.append(Paragraph(f"• {text}", self.styles['Body']))
        
        story.append(Spacer(1, 6))

    def _render_experience(self, story, data):
        """Render work experience section"""
        experience = data.get('experience', [])
        if not experience:
            return
        
        story.append(Paragraph("<b>Work Experience</b>", self.styles['SectionHeader']))
        
        for exp in experience:
            company = exp.get('company', '')
            location = exp.get('location', '')
            title = exp.get('title', '')
            duration = exp.get('duration', '')
            responsibilities = exp.get('responsibilities', [])
            
            # Company header
            company_line = f"<b>{company}</b>"
            if location:
                company_line += f" {location}"
            story.append(Paragraph(f"• {company_line}", self.styles['Body']))
            
            # Title and duration
            title_line = title
            if duration:
                title_line += f" {duration}"
            story.append(Paragraph(title_line, self.styles['Body']))
            
            # Responsibilities
            if isinstance(responsibilities, str):
                responsibilities = [responsibilities]
            
            for resp in responsibilities:
                story.append(Paragraph(f"◦ {resp}", self.styles['SubBullet']))
        
        story.append(Spacer(1, 6))


# Usage example:
if __name__ == "__main__":
    # Sample data matching Chetana's format
    sample_data = {
        "personal_info": {
            "name": "John Doe",
            "phone": "+91-1234567890",
            "email": "john.doe@example.com",
            "location": "Mumbai, India",
            "linkedin": "linkedin.com/in/johndoe",
            "github": "github.com/johndoe"
        },
        "education": [
            {
                "institution": "ABC University",
                "location": "Mumbai, India",
                "degree": "Master of Science (M.Sc.) in Data Science",
                "cgpa": "9.5",
                "duration": "Jul 2023 – Jun 2025"
            }
        ],
        "projects": [
            {
                "name": "AI Chatbot",
                "technologies": "Python, NLP, Flask",
                "description": [
                    "Built an intelligent chatbot using natural language processing.",
                    "Deployed as a web application with 90% accuracy."
                ]
            }
        ],
        "skills": {
            "programming": "Python, SQL, Java",
            "ml_ds": "Machine Learning, Deep Learning, NLP",
            "libraries": "TensorFlow, Pandas, NumPy",
            "databases": "MySQL, MongoDB",
            "platforms": "Windows, Linux"
        },
        "certifications": [
            "Machine Learning: Stanford University (2024): Neural Networks, AI",
            "Data Analytics: Google (2023): Statistical Analysis, Visualization"
        ],
        "achievements": [
            "Secured First Place in National Hackathon 2024",
            "Published research paper in IEEE Conference"
        ]
    }
    
    renderer = FixedTemplateRenderer()
    pdf_path = renderer.render_resume(sample_data)
    print(f"Resume generated: {pdf_path}")