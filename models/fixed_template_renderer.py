import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_JUSTIFY
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
        """LaTeX template settings"""
        return {
            "typography": {
                "fonts": {
                    "name": "Helvetica-Bold",
                    "heading": "Helvetica-Bold",
                    "body": "Helvetica"
                },
                "sizes": {
                    "name": 14,  # LARGE in LaTeX
                    "contact": 10,
                    "section_header": 12,  # large in LaTeX
                    "body": 10,
                    "subheading": 10
                }
            },
            "layout_settings": {
                "margins": {
                    "top": 0.4,  # -0.6in adjustment
                    "bottom": 0.5,
                    "left": 0.4,  # -0.6in adjustment
                    "right": 0.4
                }
            }
        }

    def _create_custom_styles(self):
        """Create styles matching LaTeX template"""
        styles = {}
        
        # Header Name style - LARGE, Bold
        styles['Name'] = ParagraphStyle(
            'Name',
            fontName='Helvetica-Bold',
            fontSize=14,
            alignment=TA_LEFT,
            spaceAfter=0,
            leading=17
        )

        # Contact info
        styles['Contact'] = ParagraphStyle(
            'Contact',
            fontName='Helvetica',
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=0,
            leading=12
        )

        # Section Header - with underline
        styles['SectionHeader'] = ParagraphStyle(
            'SectionHeader',
            fontName='Helvetica-Bold',
            fontSize=12,
            alignment=TA_LEFT,
            spaceBefore=7,  # 7pt before section
            spaceAfter=5,   # 5pt after section
            leading=14,
            textTransform='uppercase'
        )

        # Institution/Company (bold, larger)
        styles['Institution'] = ParagraphStyle(
            'Institution',
            fontName='Helvetica-Bold',
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=0,
            leading=12
        )

        # Degree/Title (italic)
        styles['Degree'] = ParagraphStyle(
            'Degree',
            fontName='Helvetica-Oblique',
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=2.5,  # topsep=2.5pt
            leading=12
        )

        # Bullet items
        styles['BulletItem'] = ParagraphStyle(
            'BulletItem',
            fontName='Helvetica',
            fontSize=10,
            alignment=TA_LEFT,
            leftIndent=0,
            spaceAfter=0,  # itemsep=0pt
            leading=12
        )

        # Sub-bullet items (circle)
        styles['SubBullet'] = ParagraphStyle(
            'SubBullet',
            fontName='Helvetica',
            fontSize=10,
            alignment=TA_LEFT,
            leftIndent=15,
            spaceAfter=0,
            leading=12
        )

        # Skills label (bold)
        styles['SkillLabel'] = ParagraphStyle(
            'SkillLabel',
            fontName='Helvetica-Bold',
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=0,
            leading=12
        )

        return styles

    def render_resume(self, resume_data, output_path=None):
        """Generate PDF matching LaTeX template exactly"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs('static', exist_ok=True)
            output_path = f"static/resume_{timestamp}.pdf"

        # LaTeX margins: -0.6in adjustment
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0.4*inch,
            leftMargin=0.4*inch,
            topMargin=0.4*inch,
            bottomMargin=0.5*inch
        )

        story = []
        
        # Render sections
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
        """Header matching LaTeX tabular format"""
        pi = data.get('personal_info', {})
        
        name = pi.get('name', 'Full Name')
        phone = pi.get('phone', '+91-XXXXXXXXXX')
        email = pi.get('email', 'email@example.com')
        location = pi.get('location', 'City, Country')
        linkedin = pi.get('linkedin', '')
        github = pi.get('github', '')
        
        # Create table matching LaTeX header
        header_data = [
            [Paragraph(f"<b>{name}</b>", self.styles['Name']), 
             Paragraph(phone, self.styles['Contact'])],
            [Paragraph(f"Email: {email}", self.styles['Contact']),
             Paragraph(f"Location: {location}", self.styles['Contact'])],
        ]
        
        if linkedin:
            header_data.append([
                Paragraph(f"LinkedIn: {linkedin}", self.styles['Contact']),
                Paragraph("", self.styles['Contact'])
            ])
        
        if github:
            header_data.append([
                Paragraph(f"GitHub: {github}", self.styles['Contact']),
                Paragraph("", self.styles['Contact'])
            ])
        
        header_table = Table(header_data, colWidths=[4.5*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 3))

    def _add_section_header(self, story, title):
        """Add section header with underline"""
        story.append(Paragraph(f"<b>{title.upper()}</b>", self.styles['SectionHeader']))
        # Add horizontal line
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, 
                               spaceBefore=0, spaceAfter=5))

    def _render_education(self, story, data):
        """Education section matching LaTeX resumeSubheading"""
        education = data.get('education', [])
        if not education:
            return
        
        self._add_section_header(story, "Education")
        
        for edu in education:
            inst = edu.get('institution', '')
            loc = edu.get('location', '')
            deg = edu.get('degree', '')
            field = edu.get('field', '')
            cgpa = edu.get('cgpa', '')
            perc = edu.get('percentage', '')
            dur = edu.get('duration', '')
            
            # Line 1: Institution (bold) | Location (right)
            t1 = Table([[
                Paragraph(f"<b>{inst}</b>", self.styles['Institution']),
                Paragraph(loc, self.styles['Institution'])
            ]], colWidths=[5*inch, 2.5*inch])
            
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
            
            # Line 2: Degree (italic, bold parts) | Duration (italic, right)
            deg_text = deg
            if field:
                deg_text += f" in {field}"
            if cgpa:
                deg_text += f", <b>CGPA: {cgpa}</b>"
            elif perc:
                deg_text += f", <b>{perc}</b>"
            
            t2 = Table([[
                Paragraph(f"<i>{deg_text}</i>", self.styles['Degree']),
                Paragraph(f"<i>{dur}</i>", self.styles['Degree'])
            ]], colWidths=[5*inch, 2.5*inch])
            
            t2.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ]))
            story.append(t2)

    def _render_projects(self, story, data):
        """Projects section matching LaTeX format"""
        projects = data.get('projects', [])
        if not projects:
            return
        
        self._add_section_header(story, "Projects")
        
        for proj in projects:
            name = proj.get('name', '')
            tech = proj.get('technologies', '')
            desc = proj.get('description', [])
            
            if isinstance(tech, list):
                tech = ', '.join(tech)
            
            # Project header (bold name | tech)
            header = f"<b>{name}"
            if tech:
                header += f" | {tech}"
            header += "</b>:"
            
            story.append(Paragraph(header, self.styles['SkillLabel']))
            
            # Description bullets
            if isinstance(desc, str):
                desc = [desc]
            
            for d in desc:
                story.append(Paragraph(f"• {d}", self.styles['BulletItem']))
            
            story.append(Spacer(1, 2.5))

    def _render_research(self, story, data):
        """Research section matching LaTeX format"""
        research = data.get('research', [])
        if not research:
            return
        
        self._add_section_header(story, "Research")
        
        for res in research:
            title = res.get('title', '')
            loc = res.get('location', '')
            role = res.get('role', '')
            date = res.get('date', '')
            details = res.get('details', [])
            
            # Line 1: Title (bold) | Location (right)
            t1 = Table([[
                Paragraph(f"<b>{title}</b>", self.styles['Institution']),
                Paragraph(loc, self.styles['Institution'])
            ]], colWidths=[5*inch, 2.5*inch])
            
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
            
            # Line 2: Role (italic) | Date (italic, right)
            t2 = Table([[
                Paragraph(f"<i>{role}</i>", self.styles['Degree']),
                Paragraph(f"<i>{date}</i>", self.styles['Degree'])
            ]], colWidths=[5*inch, 2.5*inch])
            
            t2.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(t2)
            
            # Details
            if isinstance(details, str):
                details = [details]
            
            for d in details:
                story.append(Paragraph(f"• {d}", self.styles['BulletItem']))
            
            story.append(Spacer(1, 2.5))

    def _render_technical_skills(self, story, data):
        """Technical Skills matching LaTeX format"""
        skills = data.get('skills', {})
        if not skills:
            return
        
        self._add_section_header(story, "Technical Skills")
        
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
                        story.append(Paragraph(f"<b>{label}:</b> {sk}", self.styles['BulletItem']))

    def _render_certifications(self, story, data):
        """Certifications matching LaTeX format"""
        certs = data.get('certifications', [])
        if not certs:
            return
        
        self._add_section_header(story, "Certifications")
        
        for cert in certs:
            if isinstance(cert, str) and cert.strip():
                story.append(Paragraph(f"<b>•</b> {cert}", self.styles['BulletItem']))

    def _render_achievements(self, story, data):
        """Achievements matching LaTeX format"""
        achievements = data.get('achievements', [])
        if not achievements:
            return
        
        self._add_section_header(story, "Achievements and Roles")
        
        for ach in achievements:
            if isinstance(ach, str) and ach.strip():
                story.append(Paragraph(f"• {ach}", self.styles['BulletItem']))

    def _render_experience(self, story, data):
        """Work Experience matching LaTeX format"""
        experience = data.get('experience', [])
        if not experience:
            return
        
        self._add_section_header(story, "Work Experience")
        
        for exp in experience:
            comp = exp.get('company', '')
            loc = exp.get('location', '')
            title = exp.get('title', '')
            dur = exp.get('duration', '')
            resp = exp.get('responsibilities', [])
            
            # Line 1: Company (bold) | Location (right)
            t1 = Table([[
                Paragraph(f"<b>{comp}</b>", self.styles['Institution']),
                Paragraph(loc, self.styles['Institution'])
            ]], colWidths=[5*inch, 2.5*inch])
            
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
            
            # Line 2: Title (italic) | Duration (italic, right)
            t2 = Table([[
                Paragraph(f"<i>{title}</i>", self.styles['Degree']),
                Paragraph(f"<i>{dur}</i>", self.styles['Degree'])
            ]], colWidths=[5*inch, 2.5*inch])
            
            t2.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(t2)
            
            # Responsibilities
            if isinstance(resp, str):
                resp = [resp]
            
            for r in resp:
                if r.strip():
                    story.append(Paragraph(f"• {r}", self.styles['BulletItem']))
            
            story.append(Spacer(1, 2.5))