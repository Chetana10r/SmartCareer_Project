import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT
from datetime import datetime
import os

class FixedTemplateRenderer:
    def __init__(self, template_path="templates/fixed_resume_template.json"):
        try:
            with open(template_path, 'r') as f:
                self.template = json.load(f)
        except FileNotFoundError:
            self.template = {}
        self.styles = self._create_custom_styles()

    def _create_custom_styles(self):
        """Styles matching LaTeX template exactly"""
        styles = {}
        
        # Name - LARGE and Bold
        styles['Name'] = ParagraphStyle(
            'Name',
            fontName='Helvetica-Bold',
            fontSize=14,
            alignment=TA_LEFT,
            spaceAfter=1,
            leading=16
        )
        
        # Contact
        styles['Contact'] = ParagraphStyle(
            'Contact',
            fontName='Helvetica',
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=1,
            leading=12
        )
        
        # Section Header - Large, Bold, with line
        styles['SectionHeader'] = ParagraphStyle(
            'SectionHeader',
            fontName='Helvetica-Bold',
            fontSize=11,
            alignment=TA_LEFT,
            spaceBefore=7,
            spaceAfter=5,
            leading=13
        )
        
        # Institution/Company name (bold, 10pt)
        styles['InstitutionName'] = ParagraphStyle(
            'InstitutionName',
            fontName='Helvetica-Bold',
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=0,
            leading=12
        )
        
        # Degree/Title (italic, 10pt)
        styles['DegreeTitle'] = ParagraphStyle(
            'DegreeTitle',
            fontName='Helvetica-Oblique',
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=2.5,
            leading=12
        )
        
        # Project header (bold, no bullet) - \resumeSubItem style
        styles['ProjectHeader'] = ParagraphStyle(
            'ProjectHeader',
            fontName='Helvetica-Bold',
            fontSize=10,
            alignment=TA_LEFT,
            leftIndent=0,
            spaceAfter=0,
            leading=12
        )
        
        # Bullet item - \item style
        styles['BulletItem'] = ParagraphStyle(
            'BulletItem',
            fontName='Helvetica',
            fontSize=10,
            alignment=TA_LEFT,
            leftIndent=20,
            firstLineIndent=-10,
            spaceAfter=0,
            leading=12,
            wordWrap='LTR'
        )
        
        # Sub-bullet item - \labelitemii ($\circ$) style
        styles['SubBulletItem'] = ParagraphStyle(
            'SubBulletItem',
            fontName='Helvetica',
            fontSize=10,
            alignment=TA_LEFT,
            leftIndent=30,
            firstLineIndent=-10,
            spaceAfter=0,
            leading=12,
            wordWrap='LTR'
        )
        
        # Skills/Cert item - \resumeSubItem style
        styles['SkillItem'] = ParagraphStyle(
            'SkillItem',
            fontName='Helvetica',
            fontSize=10,
            alignment=TA_LEFT,
            leftIndent=0,
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

        # Match LaTeX margins: -0.6in adjustments
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0.4*inch,
            leftMargin=0.4*inch,
            topMargin=0.4*inch,
            bottomMargin=0.5*inch
        )

        story = []
        
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
        """
        LaTeX format:
        Name (LARGE, bold)  |  Phone (right)
        Email: ...  |  Location: ... (right)
        LinkedIn: ...
        GitHub: ...
        """
        pi = data.get('personal_info', {})
        
        name = pi.get('name', 'Full Name')
        phone = pi.get('phone', '')
        email = pi.get('email', '')
        location = pi.get('location', '')
        linkedin = pi.get('linkedin', '')
        github = pi.get('github', '')
        
        # Header table matching LaTeX \begin{tabular*}
        header_data = [
            [Paragraph(f"<b>{name.upper()}</b>", self.styles['Name']), 
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
        
        ht = Table(header_data, colWidths=[5*inch, 2.5*inch])
        ht.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(ht)
        story.append(Spacer(1, 5))

    def _add_section_header(self, story, title):
        """Section header with line - matches \section{} in LaTeX"""
        story.append(Paragraph(f"<b>{title.upper()}</b>", self.styles['SectionHeader']))
        # Add horizontal line
        from reportlab.platypus import HRFlowable
        from reportlab.lib import colors
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, 
                               spaceBefore=0, spaceAfter=5))

    def _render_education(self, story, data):
        """
        LaTeX format: \resumeSubheading{Institution}{Location}{Degree}{Dates}
        Line 1: Institution (bold)  |  Location (right)
        Line 2: Degree (italic)  |  Dates (italic, right)
        """
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
            
            if not inst:
                continue
            
            # Line 1: Institution | Location
            t1 = Table([[
                Paragraph(f"<b>{inst}</b>", self.styles['InstitutionName']),
                Paragraph(loc, self.styles['InstitutionName'])
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
            
            # Line 2: Degree (italic) | Duration (italic)
            deg_text = deg
            if field:
                deg_text += f" in {field}"
            if cgpa:
                deg_text += f", <b>CGPA: {cgpa}</b>"
            elif perc:
                deg_text += f", <b>{perc}</b>"
            
            t2 = Table([[
                Paragraph(f"<i>{deg_text}</i>", self.styles['DegreeTitle']),
                Paragraph(f"<i>{dur}</i>", self.styles['DegreeTitle'])
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
        """
        LaTeX format:
        \resumeSubItem{Project Name | Tech}{}
        \resumeItemListStart
        \item Description 1
        \item Description 2
        \resumeItemListEnd
        """
        projects = data.get('projects', [])
        if not projects:
            return
        
        self._add_section_header(story, "Projects")
        
        for proj in projects:
            name = proj.get('name', '')
            tech = proj.get('technologies', '')
            desc = proj.get('description', [])
            
            if not name:
                continue
            
            if isinstance(tech, list):
                tech = ', '.join(tech)
            
            # Project header (bold, no bullet)
            header = f"<b>{name}"
            if tech:
                header += f" | {tech}"
            header += "</b>"
            
            story.append(Paragraph(header, self.styles['ProjectHeader']))
            
            # Descriptions with bullets
            if isinstance(desc, str):
                desc = [desc]
            
            for d in desc:
                if d.strip():
                    story.append(Paragraph(f"• {d}", self.styles['BulletItem']))
            
            story.append(Spacer(1, 2.5))

    def _render_research(self, story, data):
        """
        LaTeX format: \resumeSubheading{Title}{Location}{Role}{Date}
        \resumeItemListStart
        \item Detail 1
        \resumeItemListEnd
        """
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
            
            if not title:
                continue
            
            # Line 1: Title (bold) | Location
            t1 = Table([[
                Paragraph(f"<b>{title}</b>", self.styles['InstitutionName']),
                Paragraph(loc, self.styles['InstitutionName'])
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
            
            # Line 2: Role (italic) | Date (italic)
            t2 = Table([[
                Paragraph(f"<i>{role}</i>", self.styles['DegreeTitle']),
                Paragraph(f"<i>{date}</i>", self.styles['DegreeTitle'])
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
            
            # Details with bullets
            if isinstance(details, str):
                details = [details]
            
            for d in details:
                if d.strip():
                    story.append(Paragraph(f"• {d}", self.styles['BulletItem']))
            
            story.append(Spacer(1, 2.5))

    def _render_technical_skills(self, story, data):
        """
        LaTeX format: \resumeSubItem{Category}{skills}
        Renders as: • Category: skills
        """
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
                        story.append(Paragraph(f"• <b>{label}:</b> {sk}", self.styles['BulletItem']))

    def _render_certifications(self, story, data):
        """
        LaTeX format: \resumeSubItem{Name}{Details}
        Renders as: • Name: Details
        """
        certs = data.get('certifications', [])
        if not certs:
            return
        
        self._add_section_header(story, "Certifications")
        
        for cert in certs:
            if isinstance(cert, str) and cert.strip():
                # Parse "Name: Details" format
                if ':' in cert:
                    parts = cert.split(':', 1)
                    name = parts[0].strip()
                    details = parts[1].strip()
                    story.append(Paragraph(f"• <b>{name}:</b> {details}", self.styles['BulletItem']))
                else:
                    story.append(Paragraph(f"• {cert}", self.styles['BulletItem']))

    def _render_achievements(self, story, data):
        """
        LaTeX format: \item Achievement
        Simple bullet list
        """
        achievements = data.get('achievements', [])
        if not achievements:
            return
        
        self._add_section_header(story, "Achievements and Roles")
        
        for ach in achievements:
            if isinstance(ach, str) and ach.strip():
                story.append(Paragraph(f"• {ach}", self.styles['BulletItem']))

    def _render_experience(self, story, data):
        """
        LaTeX format: \resumeSubheading{Company}{Location}{Title}{Duration}
        \resumeItemListStart
        \item Responsibility
        \resumeItemListEnd
        """
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
            
            if not comp:
                continue
            
            # Line 1: Company (bold) | Location
            t1 = Table([[
                Paragraph(f"<b>{comp}</b>", self.styles['InstitutionName']),
                Paragraph(loc, self.styles['InstitutionName'])
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
            
            # Line 2: Title (italic) | Duration (italic)
            t2 = Table([[
                Paragraph(f"<i>{title}</i>", self.styles['DegreeTitle']),
                Paragraph(f"<i>{dur}</i>", self.styles['DegreeTitle'])
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
            
            # Responsibilities with bullets
            if isinstance(resp, str):
                resp = [resp]
            
            for r in resp:
                if r.strip():
                    story.append(Paragraph(f"• {r}", self.styles['BulletItem']))
            
            story.append(Spacer(1, 2.5))