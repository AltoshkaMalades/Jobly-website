import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_cv_pdf(profile):
    """Generate a PDF buffer for the given Profile instance."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        spaceAfter=12,
        textColor=colors.HexColor('#111111'),
    )
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        spaceBefore=14,
        spaceAfter=6,
        textColor=colors.HexColor('#0b3d91'),
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontSize=11,
        leading=15,
        spaceAfter=8,
    )
    note_style = ParagraphStyle(
        'Note',
        parent=styles['BodyText'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#555555'),
        spaceAfter=8,
    )

    story = []
    full_name = profile.user.get_full_name() or profile.user.username
    story.append(Paragraph(full_name, title_style))
    story.append(Paragraph(profile.summary or 'Краткое резюме отсутствует.', body_style))
    story.append(Spacer(1, 12))

    contact_data = [
        ['Email:', profile.user.email or 'Не указан'],
        ['Роль:', profile.get_role_display() or 'Не указан'],
    ]
    contact_table = Table(contact_data, colWidths=[1.2 * inch, 4.8 * inch], hAlign='LEFT')
    contact_table.setStyle(
        TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#222222')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ])
    )
    story.append(contact_table)
    story.append(Spacer(1, 18))

    if profile.education:
        story.append(Paragraph('Образование', heading_style))
        story.append(Paragraph(profile.education, body_style))

    if profile.experience:
        story.append(Paragraph('Опыт работы', heading_style))
        story.append(Paragraph(profile.experience, body_style))

    if profile.skills:
        story.append(Paragraph('Навыки', heading_style))
        skills_text = '<br/>'.join([skill.strip() for skill in profile.skills.splitlines() if skill.strip()])
        story.append(Paragraph(skills_text or 'Навыки не указаны.', body_style))

    if profile.bio:
        story.append(Paragraph('Дополнительная информация', heading_style))
        story.append(Paragraph(profile.bio, body_style))

    story.append(Spacer(1, 36))
    story.append(Paragraph('Сгенерировано с помощью JobAggregator', note_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
