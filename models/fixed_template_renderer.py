import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
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
        
        # Get sizes safely with fallbacks
        typography = self.template.get('typography', {})
        fonts = typography.get('fonts', {})
        sizes = typography.get('sizes', {})
        
        # Name style (Bold, larger) - on same line as phone
        styles['Name'] = ParagraphStyle(
            'Name',
            fontName=fonts.get('name', 'Helvetica-Bold'),
            fontSize=sizes.get('name', 16),
            alignment=TA_LEFT,
            spaceAfter=3,
            leading=18
        )

        # Contact info style
        styles['Contact'] = ParagraphStyle(
            'Contact',
            fontName=fonts.get('body', 'Helvetica'),
            fontSize=sizes.get('contact', 10),
            alignment=TA_LEFT,
            spaceAfter=2,
            leading=12
        )

        # Section header style (Bold)
        section_header_size = sizes.get('section_header', sizes.get('heading', 12))
        styles['SectionHeader'] = ParagraphStyle(
            'SectionHeader',
            fontName=fonts.get('heading', 'Helvetica-Bold'),
            fontSize=section_header_size,
            alignment=TA_LEFT,
            spaceBefore=10,
            spaceAfter=4,
            leading=14
        )

        # Body text style (for bullet points)
        styles['Body'] = ParagraphStyle(
            'Body',
            fontName=fonts.get('body', 'Helvetica'),
            fontSize=sizes.get('body', 10),
            alignment=TA_LEFT,
            leftIndent=0,
            firstLineIndent=-15,
            spaceAfter=3,
            leading=12,
            bulletIndent=0
        )

        # Sub-bullet style (deeper indent with circle bullets)
        styles['SubBullet'] = ParagraphStyle(
            'SubBullet',
            fontName=fonts.get('body', 'Helvetica'),
            fontSize=sizes.get('body', 10),
            alignment=TA_LEFT,
            leftIndent=15,
            firstLineIndent=-15,
            spaceAfter=3,
            leading=12,
            bulletIndent=15
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
        """Render name and contact info - Name and Phone on same line"""
        personal_info = data.get('personal_info', {})
        
        # Name and Phone on same line
        name = personal_info.get('name', 'Full Name')
        phone = personal_info.get('phone', '+91-XXXXXXXXXX')
        
        # Use table for name and phone alignment
        name_phone_data = [[
            Paragraph(f"<b>{name}</b>", self.styles['Name']),
            Paragraph(f"{phone}", self.styles['Name'])
        ]]
        
        name_phone_table = Table(name_phone_data, colWidths=[4.5*inch, 2*inch])
        name_phone_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(name_phone_table)
        
        # Email and Location line
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
        
        story.append(Spacer(1, 6))

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
            
            # Create table for institution and duration alignment
            inst_text = f"<b>{institution}</b>"
            if location:
                inst_text += f" {location}"
            
            edu_data = [[
                Paragraph(f"• {inst_text}", self.styles['Body']),
                Paragraph(duration if duration else "", self.styles['Body'])
            ]]
            
            edu_table = Table(edu_data, colWidths=[5*inch, 1.5*inch])
            edu_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(edu_table)
            
            # Degree details on next line
            degree_line = degree
            if field:
                degree_line += f" in {field}"
            if cgpa:
                degree_line += f", CGPA: {cgpa}"
            elif percentage:
                degree_line += f", {percentage}"
            
            # Indent the degree line
            story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{degree_line}", self.styles['Contact']))
        
        story.append(Spacer(1, 4))

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
        
        story.append(Spacer(1, 4))

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
            
            # Research header with date
            header_text = f"<b>{title}</b>"
            if location:
                header_text += f" {location}"
            
            res_data = [[
                Paragraph(f"• {header_text}", self.styles['Body']),
                Paragraph(date if date else "", self.styles['Body'])
            ]]
            
            res_table = Table(res_data, colWidths=[5*inch, 1.5*inch])
            res_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(res_table)
            
            # Role
            if role:
                story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{role}", self.styles['Contact']))
            
            # Details
            if isinstance(details, str):
                details = [details]
            
            for detail in details:
                story.append(Paragraph(f"◦ {detail}", self.styles['SubBullet']))
        
        story.append(Spacer(1, 4))

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
            # Predefined category order and labels
            categories = [
                ('programming', 'Programming & Languages'),
                ('ml_ds', 'Machine Learning & Data Science'),
                ('libraries', 'Libraries & Frameworks'),
                ('databases', 'Databases & Tools'),
                ('platforms', 'Platforms & Operating Systems')
            ]
            
            for key, label in categories:
                if key in skills and skills[key]:
                    skill_list = skills[key]
                    if isinstance(skill_list, list):
                        skills_text = ", ".join(skill_list)
                    else:
                        skills_text = skill_list
                    
                    if skills_text.strip():  # Only add if not empty
                        story.append(Paragraph(f"• <b>{label}:</b> {skills_text}", self.styles['Body']))
        
        story.append(Spacer(1, 4))

    def _render_certifications(self, story, data):
        """Render certifications section"""
        certifications = data.get('certifications', [])
        if not certifications:
            return
        
        story.append(Paragraph("<b>Certifications</b>", self.styles['SectionHeader']))
        
        for cert in certifications:
            if isinstance(cert, str):
                if cert.strip():  # Only add non-empty strings
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
        
        story.append(Spacer(1, 4))

    def _render_achievements(self, story, data):
        """Render achievements and roles section"""
        achievements = data.get('achievements', [])
        if not achievements:
            return
        
        story.append(Paragraph("<b>Achievements and Roles</b>", self.styles['SectionHeader']))
        
        for achievement in achievements:
            if isinstance(achievement, str):
                if achievement.strip():  # Only add non-empty strings
                    story.append(Paragraph(f"• {achievement}", self.styles['Body']))
            else:
                title = achievement.get('title', '')
                description = achievement.get('description', '')
                text = title if title else description
                if text.strip():
                    story.append(Paragraph(f"• {text}", self.styles['Body']))
        
        story.append(Spacer(1, 4))

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
            
            # Company header with duration
            company_text = f"<b>{company}</b>"
            if location:
                company_text += f" {location}"
            
            exp_data = [[
                Paragraph(f"• {company_text}", self.styles['Body']),
                Paragraph(duration if duration else "", self.styles['Body'])
            ]]
            
            exp_table = Table(exp_data, colWidths=[5*inch, 1.5*inch])
            exp_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(exp_table)
            
            # Title
            if title:
                story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{title}", self.styles['Contact']))
            
            # Responsibilities
            if isinstance(responsibilities, str):
                responsibilities = [responsibilities]
            
            for resp in responsibilities:
                if resp.strip():
                    story.append(Paragraph(f"◦ {resp}", self.styles['SubBullet']))
        
        story.append(Spacer(1, 4))


# Usage example:
if __name__ == "__main__":
    # Sample data matching Chetana's format
    sample_data = {
        "personal_info": {
            "name": "Chetana Rane",
            "phone": "+91-8799861261",
            "email": "chetanarane10@gmail.com",
            "location": "Pune, India",
            "linkedin": "linkedin.com/in/chetana-rane-bb6ba3271",
            "github": "github.com/Chetana10r"
        },
        "education": [
            {
                "institution": "Fergusson College",
                "location": "Pune, India",
                "degree": "Master of Science (M.Sc.) in Data Science",
                "cgpa": "9.63",
                "duration": "Jul 2024 – Jun 2026"
            }
        ],
        "projects": [
            {
                "name": "Fake News Detection System",
                "technologies": "Multimodal Machine Learning",
                "description": [
                    "Developed a multimodal fake news detection system with text, image (OCR), audio (Whisper), and video inputs.",
                    "Utilized SentenceTransformer embeddings with a Random Forest classifier, achieving 95% accuracy."
                ]
            }
        ],
        "skills": {
            "programming": "Python, SQL, C (Basic)",
            "ml_ds": "Supervised Learning, Unsupervised Learning, Classification, Regression, NLP",
            "libraries": "Pandas, NumPy, scikit-learn, Matplotlib, Seaborn, TensorFlow, Flask",
            "databases": "MySQL, PostgreSQL, Git, Power BI, Tableau, VS Code",
            "platforms": "Windows, Linux, Raspberry Pi"
        },
        "certifications": [
            "AI GATI Hackathon: Top 12 Finalist (2024): AI-based challenge participation, Machine Learning."
        ],
        "achievements": [
            "Secured First Place in Avishkar (Engineering & Technology) and qualified for the State-level competition."
        ]
    }
    
    renderer = FixedTemplateRenderer()
    pdf_path = renderer.render_resume(sample_data)
    print(f"Resume generated: {pdf_path}")