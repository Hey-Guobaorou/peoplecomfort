"""Render the revised A3 Markdown and generated figures to a reproducible PDF.

Requires reportlab and Pillow. Run from the repository root:
    python coursework/analyze_extended.py
    python coursework/build_pdf.py
"""
from pathlib import Path
import html
import re

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,
    Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle)

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'A3_research_report.md'
OUTPUT=ROOT/'A3_research_report.pdf'


def inline(value):
    value=html.escape(value).replace('–','-').replace('—','-').replace('×','x')
    value=re.sub(r'`([^`]+)`',r'<font color="#216c5b">\1</font>',value)
    value=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',value)
    value=re.sub(r'(https?://[^\s;]+)',lambda m:'<a href="'+m.group(1)+'">'+m.group(1)+'</a>',value)
    return value


def blocks(source):
    lines=source.splitlines();i=0
    while i<len(lines):
        line=lines[i].strip();i+=1
        if not line:continue
        if line=='<!-- page -->':yield 'page',None;continue
        if line.startswith('```'):
            code=[]
            while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
            i+=1;yield 'code','\n'.join(code);continue
        if line.startswith('|') and i<len(lines) and lines[i].startswith('|'):
            rows=[[c.strip() for c in line.strip('|').split('|')]];i+=1
            while i<len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip('|').split('|')]);i+=1
            yield 'table',rows;continue
        image=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line)
        if image:yield 'image',(image.group(1),image.group(2));continue
        for marker,kind in [('### ','h3'),('## ','h2'),('# ','h1')]:
            if line.startswith(marker):yield kind,line[len(marker):];break
        else:yield 'p',line


def main():
    styles={
        'h1':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=19,leading=23,spaceAfter=9,textColor=colors.HexColor('#173d38'),keepWithNext=True),
        'h2':ParagraphStyle('heading',fontName='Helvetica-Bold',fontSize=12.5,leading=16,spaceBefore=10,spaceAfter=7,textColor=colors.HexColor('#216c5b'),keepWithNext=True),
        'h3':ParagraphStyle('subheading',fontName='Helvetica-Bold',fontSize=10.5,leading=14,spaceBefore=9,spaceAfter=6,textColor=colors.HexColor('#216c5b'),keepWithNext=True),
        'p':ParagraphStyle('body',fontName='Helvetica',fontSize=8.8,leading=12.6,spaceAfter=7,textColor=colors.HexColor('#263b35'),splitLongWords=True),
        'cell':ParagraphStyle('cell',fontName='Helvetica',fontSize=7.25,leading=9.6,textColor=colors.HexColor('#263b35'),splitLongWords=True),
        'code':ParagraphStyle('code',fontName='Courier',fontSize=7,leading=10,backColor=colors.HexColor('#f0f5f0'),borderPadding=8,spaceAfter=8),
        'caption':ParagraphStyle('caption',fontName='Helvetica-Oblique',fontSize=7.8,leading=10,spaceAfter=8,textColor=colors.HexColor('#667c72'))}
    width=A4[0]-88;story=[]
    for kind,data in blocks(SOURCE.read_text(encoding='utf-8')):
        if kind=='page':story.append(PageBreak())
        elif kind in ('h1','h2','h3','p'):story.append(Paragraph(inline(data),styles[kind]))
        elif kind=='code':story.append(Preformatted(data,styles['code']))
        elif kind=='image':
            path=ROOT/data[1]
            with PILImage.open(path) as image:w,h=image.size
            image_width=width;image_height=width*h/w
            if image_height>360:image_height=360;image_width=360*w/h
            story.append(KeepTogether([Image(str(path),width=image_width,height=image_height),
                Paragraph(inline(data[0]),styles['caption'])]))
        elif kind=='table':
            if not data:continue
            col_count=len(data[0]);values=[[Paragraph(inline(c),styles['cell']) for c in row] for row in data]
            if col_count==2:widths=[width*.23,width*.77]
            elif col_count==4:widths=[width*.16,width*.24,width*.28,width*.32]
            elif col_count==5:widths=[width*.16,width*.16,width*.20,width*.23,width*.25]
            else:widths=[width/col_count]*col_count
            table=Table(values,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e3eee7')),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f7faf7')]),
                ('GRID',(0,0),(-1,-1),.25,colors.HexColor('#d2dfd7')),
                ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),
                ('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),
                ('BOTTOMPADDING',(0,0),(-1,-1),5)]))
            story.extend([table,Spacer(1,8)])
    def footer(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#cbdcd2'))
        canvas.line(44,38,A4[0]-44,38);canvas.setFont('Helvetica',8)
        canvas.setFillColor(colors.HexColor('#6b8075'))
        canvas.drawString(44,26,'PeopleComfort 0.2.0 | ARCH7476 A3 | Revised method prototype')
        canvas.drawRightString(A4[0]-44,26,str(doc.page));canvas.restoreState()
    doc=SimpleDocTemplate(str(OUTPUT),pagesize=A4,leftMargin=44,rightMargin=44,
        topMargin=42,bottomMargin=52,title='ARCH7476 A3 - Thermal-zone capacity under changing user composition',
        author='ARCH7476 coursework prototype')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print('Built',OUTPUT)


if __name__=='__main__':main()
