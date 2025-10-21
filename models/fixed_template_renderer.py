import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from datetime import datetime
import os

class FixedTemplateRenderer:
    def __init__(self, template_path="templates/fixed_resume_template.json"):
        try:
            with open(template_path, 'r') as f:
                self.template = json.load(f)
        except FileNotFoundError:
            self.template = self._get_default_template()
        self.styles = self._create_custom_styles()

    def _get_default_template(self):
        """Exact template matching Chetana's format"""
        return {
            "typography": {
                "fonts": {
                    "name": "Helvetica-Bold",
                    "body": "Helvetica"
                },
                "sizes": {
                    "name": 12,
                    "contact": 9,
                    "section_header": 10,
                    "body": 9
                }
            },
            "layout_settings": {
                "margins": {"top": 0.5, "bottom": 0.5, "left": 0.75, "right": 0.75}
            }
        }

    def _create_custom_styles(self):
        styles = {}
        
        # Name style - exactly like your resume
        styles['Name'] = ParagraphStyle(
            'Name',
            fontName='Helvetica-Bold',
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=0,
            leading=14
        )

        # Contact style
        styles['Contact'] = ParagraphStyle(
            'Contact',
            fontName='Helvetica',
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=0,
            leading=11
        )

        # Section Header - Bold, proper spacing
        styles['SectionHeader'] = ParagraphStyle(
            'SectionHeader',
            fontName='Helvetica-Bold',
            fontSize=10,
            alignment=TA_LEFT,
            spaceBefore=8,
            spaceAfter=3,
            leading=12
        )

        # Primary bullet (•)
        styles['Bullet'] = ParagraphStyle(
            'Bullet',
            fontName='Helvetica',
            fontSize=9,
            alignment=TA_LEFT,
            leftIndent=0,
            spaceAfter=2,
            leading=11,
            bulletIndent=0
        )

        # Secondary bullet (◦)
        styles['SubBullet'] = ParagraphStyle(
            'SubBullet',
            fontName='Helvetica',
            fontSize=9,
            alignment=TA_LEFT,
            leftIndent=10,
            spaceAfter=2,
            leading=11,
            bulletIndent=0
        )

        # Inline text (for degree details)
        styles['Inline'] = ParagraphStyle(
            'Inline',
            fontName='Helvetica',
            fontSize=9,
            alignment=TA_LEFT,
            leftIndent=10,
            spaceAfter=2,
            leading=11
        )

        return styles

    def render_resume(self, resume_data, output_path=None):
        """Generate PDF resume matching exact format"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs('static', exist_ok=True)
            output_path = f"static/resume_{timestamp}.pdf"

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        story = []
        
        # Render all sections
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
        """Header: Name, Phone, Email, Location, LinkedIn, GitHub"""
        pi = data.get('personal_info', {})
        
        # Line 1: Name + Phone (right aligned)
        name = pi.get('name', 'Full Name')
        phone = pi.get('phone', '+91-XXXXXXXXXX')
        
        t1 = Table([[
            Paragraph(f"<b>{name}</b>", self.styles['Name']),
            Paragraph(phone, self.styles['Name'])
        ]], colWidths=[5*inch, 1.5*inch])
        
        t1.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(t1)
        story.append(Spacer(1, 2))
        
        # Line 2: Email, Location
        email = pi.get('email', 'email@example.com')
        location = pi.get('location', 'City, Country')
        story.append(Paragraph(f"Email: {email}  Location: {location}", self.styles['Contact']))
        story.append(Spacer(1, 2))
        
        # Line 3: LinkedIn, GitHub
        links = []
        if pi.get('linkedin'):
            links.append(f"LinkedIn: {pi['linkedin']}")
        if pi.get('github'):
            links.append(f"GitHub: {pi['github']}")
        
        if links:
            story.append(Paragraph("  ".join(links), self.styles['Contact']))
            story.append(Spacer(1, 2))

    def _render_education(self, story, data):
        """Education section with exact format"""
        education = data.get('education', [])
        if not education:
            return
        
        story.append(Paragraph("<b>Education</b>", self.styles['SectionHeader']))
        
        for edu in education:
            inst = edu.get('institution', '')
            loc = edu.get('location', '')
            deg = edu.get('degree', '')
            field = edu.get('field', '')
            cgpa = edu.get('cgpa', '')
            perc = edu.get('percentage', '')
            dur = edu.get('duration', '')
            
            # Line 1: • Institution Location [Duration right-aligned]
            inst_text = f"<b>{inst}</b> {loc}" if loc else f"<b>{inst}</b>"
            
            t = Table([[
                Paragraph(f"• {inst_text}", self.styles['Bullet']),
                Paragraph(dur if dur else "", self.styles['Bullet'])
            ]], colWidths=[5*inch, 1.5*inch])
            
            t.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(t)
            
            # Line 2: Degree details (indented)
            deg_line = deg
            if field:
                deg_line += f" in {field}"
            if cgpa:
                deg_line += f", CGPA: {cgpa}"
            elif perc:
                deg_line += f", {perc}"
            
            story.append(Paragraph(deg_line, self.styles['Inline']))

    def _render_projects(self, story, data):
        """Projects section with exact format"""
        projects = data.get('projects', [])
        if not projects:
            return
        
        story.append(Paragraph("<b>Projects</b>", self.styles['SectionHeader']))
        
        for proj in projects:
            name = proj.get('name', '')
            tech = proj.get('technologies', '')
            desc = proj.get('description', [])
            
            if isinstance(tech, list):
                tech = ', '.join(tech)
            
            # Line 1: • Project Name | Technologies:
            header = f"<b>{name}</b>"
            if tech:
                header += f" | {tech}"
            
            story.append(Paragraph(f"• {header}:", self.styles['Bullet']))
            
            # Description bullets
            if isinstance(desc, str):
                desc = [desc]
            
            for d in desc:
                story.append(Paragraph(f"◦ {d}", self.styles['SubBullet']))

    def _render_research(self, story, data):
        """Research section with exact format"""
        research = data.get('research', [])
        if not research:
            return
        
        story.append(Paragraph("<b>Research</b>", self.styles['SectionHeader']))
        
        for res in research:
            title = res.get('title', '')
            loc = res.get('location', '')
            role = res.get('role', '')
            date = res.get('date', '')
            details = res.get('details', [])
            
            # Line 1: • Title Location [Date right-aligned]
            header = f"<b>{title}</b> {loc}" if loc else f"<b>{title}</b>"
            
            t = Table([[
                Paragraph(f"• {header}", self.styles['Bullet']),
                Paragraph(date if date else "", self.styles['Bullet'])
            ]], colWidths=[5*inch, 1.5*inch])
            
            t.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(t)
            
            # Line 2: Role (indented)
            if role:
                story.append(Paragraph(role, self.styles['Inline']))
            
            # Details
            if isinstance(details, str):
                details = [details]
            
            for d in details:
                story.append(Paragraph(f"◦ {d}", self.styles['SubBullet']))

    def _render_technical_skills(self, story, data):
        """Technical Skills section with exact format"""
        skills = data.get('skills', {})
        if not skills:
            return
        
        story.append(Paragraph("<b>Technical Skills</b>", self.styles['SectionHeader']))
        
        if isinstance(skills, dict):
            categories = [
                ('programming', 'Programming & Languages'),
                ('ml_ds', 'Machine Learning & Data Science'),
                ('libraries', 'Libraries & Frameworks'),
                ('databases', 'Databases & Tools'),
                ('platforms', 'Platforms & Operating Systems')
            ]
            
            for key, label in categories:
                if key in skills and skills[key]:
                    sk = skills[key]
                    if isinstance(sk, list):
                        sk = ", ".join(sk)
                    
                    if sk.strip():
                        story.append(Paragraph(f"• <b>{label}:</b> {sk}", self.styles['Bullet']))

    def _render_certifications(self, story, data):
        """Certifications section with exact format"""
        certs = data.get('certifications', [])
        if not certs:
            return
        
        story.append(Paragraph("<b>Certifications</b>", self.styles['SectionHeader']))
        
        for cert in certs:
            if isinstance(cert, str) and cert.strip():
                story.append(Paragraph(f"• {cert}", self.styles['Bullet']))

    def _render_achievements(self, story, data):
        """Achievements section with exact format"""
        achievements = data.get('achievements', [])
        if not achievements:
            return
        
        story.append(Paragraph("<b>Achievements and Roles</b>", self.styles['SectionHeader']))
        
        for ach in achievements:
            if isinstance(ach, str) and ach.strip():
                story.append(Paragraph(f"• {ach}", self.styles['Bullet']))

    def _render_experience(self, story, data):
        """Work Experience section with exact format"""
        experience = data.get('experience', [])
        if not experience:
            return
        
        story.append(Paragraph("<b>Work Experience</b>", self.styles['SectionHeader']))
        
        for exp in experience:
            comp = exp.get('company', '')
            loc = exp.get('location', '')
            title = exp.get('title', '')
            dur = exp.get('duration', '')
            resp = exp.get('responsibilities', [])
            
            # Line 1: • Company Location [Duration right-aligned]
            comp_text = f"<b>{comp}</b> {loc}" if loc else f"<b>{comp}</b>"
            
            t = Table([[
                Paragraph(f"• {comp_text}", self.styles['Bullet']),
                Paragraph(dur if dur else "", self.styles['Bullet'])
            ]], colWidths=[5*inch, 1.5*inch])
            
            t.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(t)
            
            # Line 2: Title (indented)
            if title:
                story.append(Paragraph(title, self.styles['Inline']))
            
            # Responsibilities
            if isinstance(resp, str):
                resp = [resp]
            
            for r in resp:
                if r.strip():
                    story.append(Paragraph(f"◦ {r}", self.styles['SubBullet']))