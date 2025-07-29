import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import os

class FixedTemplateRenderer:
    def __init__(self, template_path="templates/fixed_resume_template.json"):
        with open(template_path, 'r') as f:
            self.template = json.load(f)
        self.styles = self._create_custom_styles()

    def _create_custom_styles(self):
        styles = {}
        base = getSampleStyleSheet()

        # Colors
        primary_color = colors.HexColor(self.template['colors']['primary'])
        
        # Name style
        styles['Name'] = ParagraphStyle('Name', fontName=self.template['typography']['fonts']['name'],
                                        fontSize=self.template['typography']['sizes']['name'],
                                        alignment=TA_CENTER, spaceAfter=6, textColor=primary_color)

        # Contact style
        styles['Contact'] = ParagraphStyle('Contact', fontName=self.template['typography']['fonts']['body'],
                                           fontSize=self.template['typography']['sizes']['contact'],
                                           alignment=TA_CENTER, spaceAfter=12)

        # Section header style
        styles['SectionHeader'] = ParagraphStyle('SectionHeader', fontName=self.template['typography']['fonts']['heading'],
                                                 fontSize=self.template['typography']['sizes']['heading'],
                                                 textColor=primary_color, spaceAfter=self.template['layout_settings']['section_spacing']*72,
                                                 borderWidth=1, borderColor=primary_color, borderPadding=2)

        # Body text style
        styles['Body'] = ParagraphStyle('Body', fontName=self.template['typography']['fonts']['body'],
                                        fontSize=self.template['typography']['sizes']['body'],
                                        leading=self.template['typography']['sizes']['body'] * self.template['layout_settings']['line_spacing'],
                                        spaceAfter=6)

        # Job header style
        styles['JobHeader'] = ParagraphStyle('JobHeader', fontName=self.template['typography']['fonts']['subheading'],
                                             fontSize=self.template['typography']['sizes']['subheading'], spaceAfter=4)

        return styles

    def render_resume(self, resume_data, output_path=None):
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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
        # Sort and render sections by order
        sections = sorted(self.template['sections'], key=lambda x: x['order'])
        for section in sections:
            if section['required'] or resume_data.get(section['name']):
                self._render_section(story, section, resume_data)

        doc.build(story)
        return output_path

    def _render_section(self, story, section_config, resume_data):
        section_name = section_config['name']
        if section_name == 'header': self._render_header(story, section_config, resume_data)
        elif section_name == 'professional_summary': self._render_summary(story, section_config, resume_data)
        elif section_name == 'technical_skills': self._render_skills(story, section_config, resume_data)
        elif section_name == 'professional_experience': self._render_experience(story, section_config, resume_data)
        elif section_name == 'education': self._render_education(story, section_config, resume_data)
        elif section_name == 'key_projects': self._render_projects(story, section_config, resume_data)
        elif section_name == 'certifications': self._render_certifications(story, section_config, resume_data)
        # Extend as needed for other sections

    def _render_header(self, story, config, data):
        personal_info = data.get('personal_info', {})
        story.append(Paragraph(personal_info.get('name',''), self.styles['Name']))

        # Contact info
        contact_parts = []
        if personal_info.get('email'): contact_parts.append(personal_info['email'])
        if personal_info.get('phone'): contact_parts.append(personal_info['phone'])
        if personal_info.get('location'): contact_parts.append(personal_info['location'])
        separator = config['formatting']['contact_separator']
        contact_line = separator.join(contact_parts)
        story.append(Paragraph(contact_line, self.styles['Contact']))

        # Links (LinkedIn, GitHub, Website)
        links = []
        for link_type in ['linkedin', 'github', 'website']:
            if personal_info.get(link_type):
                links.append(f'<a href="{personal_info[link_type]}">{link_type.title()}</a>')
        if links:
            links_line = separator.join(links)
            story.append(Paragraph(links_line, self.styles['Contact']))

        story.append(Spacer(1, 15))

    def _render_summary(self, story, config, data):
        header_text = config['formatting']['header_text']
        story.append(Paragraph(header_text, self.styles['SectionHeader']))
        summary = data.get('professional_summary','')
        # Respect max length
        max_length = config.get('max_length', 250)
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        story.append(Paragraph(summary, self.styles['Body']))
        story.append(Spacer(1, 10))

    def _render_skills(self, story, config, data):
        header_text = config['formatting']['header_text']
        story.append(Paragraph(header_text, self.styles['SectionHeader']))
        skills_data = data.get('skills', {})
        categories = config.get('categories', ['Technical'])
        if isinstance(skills_data, list):
            # Simple list fallback
            skills_text = ", ".join(skills_data[:20])
            story.append(Paragraph(f"<b>Technical:</b> {skills_text}", self.styles['Body']))
        elif isinstance(skills_data, dict):
            for category in categories:
                category_key = category.lower().replace(' ', '_')
                if skills_data.get(category_key):
                    max_skills = config['formatting'].get('max_skills_per_category', 8)
                    skills_list = skills_data[category_key][:max_skills]
                    skills_text = config['formatting']['skill_separator'].join(skills_list)
                    story.append(Paragraph(f"<b>{category}:</b> {skills_text}", self.styles['Body']))
        story.append(Spacer(1, 10))

    def _render_experience(self, story, config, data):
        header_text = config['formatting']['header_text']
        story.append(Paragraph(header_text, self.styles['SectionHeader']))
        experiences = data.get('experience', [])
        max_positions = config.get('max_positions', 5)
        for exp in experiences[:max_positions]:
            title = exp.get('title', '')
            company = exp.get('company', '')
            duration = exp.get('duration', '')
            job_line = f"<b>{title}</b>{config['formatting']['company_separator']}{company}"
            if duration:
                job_line += f"{config['formatting']['company_separator']}{duration}"
            story.append(Paragraph(job_line, self.styles['JobHeader']))
            # Responsibilities
            responsibilities = exp.get('responsibilities', [])
            max_bullets = config['formatting'].get('max_bullets', 6)
            bullet = config['formatting']['bullet_style']
            for resp in responsibilities[:max_bullets]:
                story.append(Paragraph(f"{bullet} {resp}", self.styles['Body']))
            story.append(Spacer(1, 8))
        story.append(Spacer(1, 5))

    def _render_education(self, story, config, data):
        header_text = config['formatting']['header_text']
        story.append(Paragraph(header_text, self.styles['SectionHeader']))
        education = data.get('education', [])
        separator = config['formatting']['institution_separator']
        for edu in education:
            degree = edu.get('degree', '')
            field = edu.get('field', '')
            institution = edu.get('institution', '')
            year = edu.get('year', '')
            edu_line = f"<b>{degree}"
            if field:
                edu_line += f" in {field}"
            edu_line += "</b>"
            if institution: edu_line += f"{separator}{institution}"
            if year: edu_line += f"{separator}{year}"
            story.append(Paragraph(edu_line, self.styles['Body']))
        story.append(Spacer(1, 10))

    def _render_projects(self, story, config, data):
        header_text = config['formatting']['header_text']
        story.append(Paragraph(header_text, self.styles['SectionHeader']))
        projects = data.get('projects', [])
        max_projects = config.get('max_projects', 4)
        for project in projects[:max_projects]:
            project_name = project.get('name', '')
            description = project.get('description', '')
            technologies = project.get('technologies', [])
            # Title
            story.append(Paragraph(f"<b>{project_name}</b>", self.styles['Body']))
            # Description
            max_desc_length = config['formatting'].get('description_max_length', 150)
            if len(description) > max_desc_length:
                description = description[:max_desc_length-3] + "..."
            story.append(Paragraph(description, self.styles['Body']))
            # Technologies
            if technologies:
                tech_line = f"{config['formatting']['tech_label']}{', '.join(technologies)}"
                story.append(Paragraph(tech_line, self.styles['Body']))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 5))

    def _render_certifications(self, story, config, data):
        header_text = config['formatting']['header_text']
        story.append(Paragraph(header_text, self.styles['SectionHeader']))
        certifications = data.get('certifications', [])
        separator = config['formatting']['separator']
        for cert in certifications:
            cert_name = cert.get('name', '')
            issuer = cert.get('issuer', '')
            year = cert.get('year', '')
            cert_line = cert_name
            if issuer:
                cert_line += f"{separator}{issuer}"
            if year:
                cert_line += f"{separator}{year}"
            story.append(Paragraph(cert_line, self.styles['Body']))
        story.append(Spacer(1, 10))

# Usage example:
# renderer = FixedTemplateRenderer()
# pdf_path = renderer.render_resume(resume_data)
