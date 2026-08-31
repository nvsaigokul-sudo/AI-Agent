# generate_report.py
"""
Script to programmatically generate a highly detailed, 5-page PDF project evaluation report
for the Study Planner Agent (CSE476 CA1 Project 1).
Exposes two programmatically rendered vector flowcharts (Plan-Act Loop & Date Parsing Heuristics),
a complete module architecture, developer integration guides, and system traces.
Saves the output PDF in the user's Downloads directory.
"""

import os
import sys
from datetime import datetime

# Helper to get the correct Downloads directory on Windows
def get_downloads_path():
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                downloads_dir = winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]
                if os.path.exists(downloads_dir):
                    return downloads_dir
        except Exception:
            pass
    
    # Fallback
    fallback_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    if not os.path.exists(fallback_path):
        os.makedirs(fallback_path, exist_ok=True)
    return fallback_path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon, Circle, Group
    from reportlab.pdfgen import canvas
except ImportError:
    print("ReportLab is not installed. Please run 'pip install reportlab' first.")
    sys.exit(1)

# Custom Canvas for dynamic page numbers ("Page X of 5") and running headers/footers
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        print(f"NumberedCanvas save: total pages = {num_pages}")
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#4b5563")) # grey-600
        
        # Draw header and footer on pages 2 through 5
        if self._pageNumber > 1:
            # Running Header
            self.drawString(54, 750, "Study Planner Agent (CSE476 CA1 Project Developer Evaluation Report)")
            self.setStrokeColor(colors.HexColor("#e5e7eb")) # grey-200
            self.setLineWidth(0.5)
            self.line(54, 742, letter[0] - 54, 742)
            
            # Running Footer
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(letter[0] - 54, 36, page_text)
            self.drawString(54, 36, "GitHub Repository: https://github.com/nvsaigokul-sudo/AI-Agent")
            self.line(54, 48, letter[0] - 54, 48)
            
        self.restoreState()


# Flowchart 1: Plan-Act Loop Diagram (Conceptual loop)
def create_flowchart_drawing():
    # Canvas size: width=504 (letter width 612 - 108 margins), height=230
    d = Drawing(504, 230)
    
    # Background card for the flowchart
    d.add(Rect(0, 0, 504, 230, fillColor=colors.HexColor("#f8fafc"), strokeColor=colors.HexColor("#e2e8f0"), strokeWidth=1, rx=8, ry=8))
    
    # Helper to draw a box
    def draw_box(x, y, w, h, text, subtext="", fill_color=colors.HexColor("#1e3a8a")):
        d.add(Rect(x, y, w, h, fillColor=fill_color, strokeColor=colors.HexColor("#475569"), strokeWidth=1, rx=5, ry=5))
        d.add(String(x + w/2, y + h/2 - (2 if subtext else 3), text, textAnchor='middle', fontName='Helvetica-Bold', fontSize=9, fillColor=colors.white))
        if subtext:
            d.add(String(x + w/2, y + h/2 - 12, subtext, textAnchor='middle', fontName='Helvetica', fontSize=7.5, fillColor=colors.HexColor("#e2e8f0")))

    # Helper to draw a diamond (decision)
    def draw_diamond(x, y, w, h, text, fill_color=colors.HexColor("#0d9488")):
        points = [x + w/2, y + h, x + w, y + h/2, x + w/2, y, x, y + h/2]
        d.add(Polygon(points, fillColor=fill_color, strokeColor=colors.HexColor("#0f766e"), strokeWidth=1))
        d.add(String(x + w/2, y + h/2 - 4, text, textAnchor='middle', fontName='Helvetica-Bold', fontSize=8.5, fillColor=colors.white))

    # Helper to draw arrows
    def draw_arrow(x1, y1, x2, y2, color=colors.HexColor("#64748b")):
        d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1.5))
        if x1 == x2: # Vertical arrow
            if y1 > y2: # Downward
                d.add(Polygon([x2 - 4, y2 + 6, x2 + 4, y2 + 6, x2, y2], fillColor=color, strokeColor=color))
            else: # Upward
                d.add(Polygon([x2 - 4, y2 - 6, x2 + 4, y2 - 6, x2, y2], fillColor=color, strokeColor=color))
        elif y1 == y2: # Horizontal arrow
            if x1 > x2: # Leftward
                d.add(Polygon([x2 + 6, y2 - 4, x2 + 6, y2 + 4, x2, y2], fillColor=color, strokeColor=color))
            else: # Rightward
                d.add(Polygon([x2 - 6, y2 - 4, x2 - 6, y2 + 4, x2, y2], fillColor=color, strokeColor=color))

    # Draw boxes
    draw_box(192, 185, 120, 30, "User Input Received", "Text command/request", colors.HexColor("#1e3a8a"))
    draw_arrow(252, 185, 252, 155)
    
    draw_box(162, 115, 180, 40, "Plan: Gemini LLM Engine", "Send conversation history + tools", colors.HexColor("#4f46e5"))
    draw_arrow(252, 115, 252, 85)
    
    draw_diamond(162, 25, 180, 60, "Has Function Call?")
    
    # Act Branch: YES (Function call)
    draw_arrow(342, 55, 380, 55)
    draw_box(380, 35, 105, 40, "Act: Call Python Tool", "add_task / build_schedule", colors.HexColor("#b45309"))
    d.add(String(360, 60, "Yes", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#b45309")))
    
    # Arrow back to Loop
    draw_arrow(432, 75, 432, 135)
    draw_arrow(432, 135, 342, 135)
    
    # Act Branch: NO (Final Text Response)
    draw_arrow(252, 25, 252, 0)
    d.add(String(257, 10, "No", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#0d9488")))
    
    draw_box(182, -30, 140, 30, "Return Output to User", "Display final schedule", colors.HexColor("#10b981"))
    
    return d


# Flowchart 2: Date Parsing Heuristics & Timeline sorting workflow in tools.py
def create_parser_flowchart_drawing():
    # Canvas size: width=504, height=170
    d = Drawing(504, 170)
    
    # Background card
    d.add(Rect(0, 0, 504, 170, fillColor=colors.HexColor("#f8fafc"), strokeColor=colors.HexColor("#e2e8f0"), strokeWidth=1, rx=8, ry=8))
    
    def draw_box(x, y, w, h, text, subtext="", fill_color=colors.HexColor("#0d9488")):
        d.add(Rect(x, y, w, h, fillColor=fill_color, strokeColor=colors.HexColor("#0f766e"), strokeWidth=1, rx=4, ry=4))
        d.add(String(x + w/2, y + h/2 - (2 if subtext else 3), text, textAnchor='middle', fontName='Helvetica-Bold', fontSize=8, fillColor=colors.white))
        if subtext:
            d.add(String(x + w/2, y + h/2 - 10, subtext, textAnchor='middle', fontName='Helvetica', fontSize=7, fillColor=colors.HexColor("#ccfbf1")))

    def draw_diamond(x, y, w, h, text, fill_color=colors.HexColor("#1e3a8a")):
        points = [x + w/2, y + h, x + w, y + h/2, x + w/2, y, x, y + h/2]
        d.add(Polygon(points, fillColor=fill_color, strokeColor=colors.HexColor("#1e3a8a"), strokeWidth=1))
        d.add(String(x + w/2, y + h/2 - 3, text, textAnchor='middle', fontName='Helvetica-Bold', fontSize=7.5, fillColor=colors.white))

    def draw_arrow(x1, y1, x2, y2, color=colors.HexColor("#64748b")):
        d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1.2))
        if x1 == x2:
            if y1 > y2: d.add(Polygon([x2-3, y2+5, x2+3, y2+5, x2, y2], fillColor=color, strokeColor=color))
            else: d.add(Polygon([x2-3, y2-5, x2+3, y2-5, x2, y2], fillColor=color, strokeColor=color))
        elif y1 == y2:
            if x1 > x2: d.add(Polygon([x2+5, y2-3, x2+5, y2+3, x2, y2], fillColor=color, strokeColor=color))
            else: d.add(Polygon([x2-5, y2-3, x2-5, y2+3, x2, y2], fillColor=color, strokeColor=color))

    # Layout:
    # 1. Input string
    draw_box(15, 65, 80, 30, "Due Date String", "e.g., 'September 5'", colors.HexColor("#475569"))
    draw_arrow(95, 80, 110, 80)
    
    # 2. Token Clean & Stripping
    draw_box(110, 60, 95, 40, "Token Cleaning", "Strip ordinal suffixes\n(th, rd, nd) & lower", colors.HexColor("#0d9488"))
    draw_arrow(205, 80, 220, 80)
    
    # 3. Format Diamond
    draw_diamond(220, 50, 90, 60, "Standard ISO?")
    
    # Branch YES: YYYY-MM-DD
    draw_arrow(265, 110, 265, 130)
    draw_arrow(265, 130, 320, 130)
    draw_box(320, 115, 95, 30, "Parse YYYY-MM-DD", "Direct standard strptime", colors.HexColor("#b45309"))
    d.add(String(275, 120, "Yes", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor("#b45309")))
    
    # Branch NO: Natural text
    draw_arrow(265, 50, 265, 30)
    draw_arrow(265, 30, 320, 30)
    draw_box(320, 15, 95, 30, "Map Month & Digits", "Text-to-Month dictionary", colors.HexColor("#1e3a8a"))
    d.add(String(275, 36, "No", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor("#1e3a8a")))
    
    # Merge and Sort
    draw_arrow(415, 130, 445, 130)
    draw_arrow(445, 130, 445, 100)
    draw_arrow(415, 30, 445, 30)
    draw_arrow(445, 30, 445, 60)
    
    draw_box(410, 60, 80, 40, "Anchor & Sort", "August 27, 2026\nChronological timeline", colors.HexColor("#10b981"))
    
    return d


def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    c_primary = colors.HexColor("#1e3a8a")     # Navy
    c_secondary = colors.HexColor("#0d9488")   # Teal
    c_text = colors.HexColor("#1f2937")        # Charcoal
    c_bg_light = colors.HexColor("#f8fafc")    # Off-white
    c_border = colors.HexColor("#e2e8f0")      # Light grey
    
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=25,
        leading=30,
        textColor=c_primary,
        alignment=0,
        spaceAfter=15
    )
    
    style_cover_subtitle = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12.5,
        leading=16,
        textColor=c_secondary,
        alignment=0,
        spaceAfter=30
    )
    
    style_heading1 = ParagraphStyle(
        'Heading1Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    style_heading2 = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_secondary,
        spaceBefore=8,
        spaceAfter=5,
        keepWithNext=True
    )
    
    style_body = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.2,
        leading=13.5,
        textColor=c_text,
        spaceAfter=8
    )
    
    style_bullet = ParagraphStyle(
        'BulletCustom',
        parent=style_body,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    style_metadata_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#475569")
    )
    
    style_metadata_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=c_text
    )
    
    style_quote = ParagraphStyle(
        'QuoteText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#334155")
    )
    
    style_code = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6
    )
    
    style_team = ParagraphStyle(
        'CoverTeam',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#4b5563"),
        spaceAfter=10
    )
    
    story = []
    
    # ----------------------------------------------------
    # PAGE 1: TITLE PAGE & EXECUTIVE SUMMARY
    # ----------------------------------------------------
    story.append(Spacer(1, 10))
    team_text = (
        "<b>Project Team:</b> T Sanath (Reg No: 12311513) &nbsp;|&nbsp; "
        "N V Sai Gokul (Reg No: 12401217) &nbsp;|&nbsp; "
        "Akhil (Reg No: 12311470)"
    )
    story.append(Paragraph(team_text, style_team))
    story.append(Spacer(1, 10))
    
    indicator_table = Table([[""]], colWidths=[60], rowHeights=[6])
    indicator_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_secondary),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(indicator_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("PROJECT DEVELOPER EVALUATION REPORT", style_cover_title))
    story.append(Paragraph("CSE476 CA1: Study Planner AI Agent using Google GenAI SDK<br/>Comprehensive Code Architecture, API Design, and Reasoning Analysis", style_cover_subtitle))
    story.append(Spacer(1, 10))
    
    meta_data = [
        [Paragraph("Course & Assignment:", style_metadata_label), Paragraph("CSE476 CA1 Project 1", style_metadata_val)],
        [Paragraph("Project Architecture:", style_metadata_label), Paragraph("Plan-Act Explicit Loop (Lazy Initialization Model)", style_metadata_val)],
        [Paragraph("GitHub Repository:", style_metadata_label), Paragraph("https://github.com/nvsaigokul-sudo/AI-Agent", style_metadata_val)],
        [Paragraph("API Endpoint Status:", style_metadata_label), Paragraph("Running on http://127.0.0.1:5000", style_metadata_val)],
        [Paragraph("Evaluation Date:", style_metadata_label), Paragraph(datetime.now().strftime("%B %d, %Y"), style_metadata_val)]
    ]
    meta_table = Table(meta_data, colWidths=[130, 374])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor("#f1f5f9")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 25))
    
    story.append(Paragraph("Executive Summary", style_heading2))
    summary_text = (
        "This evaluation report delivers a comprehensive analysis of the <b>Study Planner AI Agent</b> built for "
        "CSE476 CA1. The core system implements an explicit reasoning workflow utilizing the new <i>google-genai</i> "
        "library and <i>gemini-2.5-flash</i>. By capturing intermediate API function call payloads and outputting step logs, "
        "the agent avoids black-box automation, giving developers immediate sight of planning choices. "
        "The system has been extended with a robust local Flask server and a glassmorphic dashboard frontend, allowing "
        "interactive prompt execution, live task visualizer tables, and parsed timeline rendering. "
        "This document describes the code modules, dates sorting logic, API endpoints contract, and "
        "date anchoring solutions implemented to ensure reproducible academic scheduling."
    )
    summary_table = Table([[Paragraph(summary_text, style_quote)]], colWidths=[504])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('LINELEFT', (0, 0), (-1, -1), 3.0, c_primary),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(summary_table)
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 2: CORE ARCHITECTURE & CODE MODULES
    # ----------------------------------------------------
    story.append(Paragraph("1. System Architecture & Module Details", style_heading1))
    story.append(Spacer(1, 5))
    
    arch_desc = (
        "The system utilizes a decoupled architecture where the conversational state, tool logic, and temporary data "
        "are segregated. The client application (browser) communicates with the backend (Flask) using RESTful API routes. "
        "The backend binds directly to the Python <code>StudyPlannerAgent</code> class."
    )
    story.append(Paragraph(arch_desc, style_body))
    
    story.append(Paragraph("Module-by-Module Code Structure", style_heading2))
    
    code_structure_data = [
        [Paragraph("<b>File Path & Symbol</b>", style_metadata_label), Paragraph("<b>Developer Implementation Details</b>", style_metadata_label)],
        [
            Paragraph("<a href='file:///c:/Users/nvsai/Desktop/anti%20gravity/AI_Agent/agent.py'>agent.py</a><br/><code>StudyPlannerAgent</code>", style_body),
            Paragraph("Main agent manager. Initialises <code>genai.Client</code>. Exposes <code>run(user_input)</code> which handles conversational history (<code>self.history</code> list) and coordinates the execution loop by toggling <code>automatic_function_calling=False</code>.", style_body)
        ],
        [
            Paragraph("<a href='file:///c:/Users/nvsai/Desktop/anti%20gravity/AI_Agent/tools.py'>tools.py</a><br/><code>add_task</code> / <code>build_schedule</code>", style_body),
            Paragraph("Implements the tool capabilities. Includes date token cleansing, custom calendar parsing mappings, chronological sorting calculations, and string interval formatting.", style_body)
        ],
        [
            Paragraph("<a href='file:///c:/Users/nvsai/Desktop/anti%20gravity/AI_Agent/memory.py'>memory.py</a><br/><code>_tasks</code>", style_body),
            Paragraph("Provides a session-level, state-safe array database. Contains operations to insert task dictionaries, read stored collections, and reset variables to resolve memory pollution during multi-session usage.", style_body)
        ],
        [
            Paragraph("<a href='file:///c:/Users/nvsai/Desktop/anti%20gravity/AI_Agent/app.py'>app.py</a><br/>Flask Server", style_body),
            Paragraph("Hosts API endpoints. Features a <b>lazy initialization wrapper</b> to defer agent loading so missing API keys do not trigger app crashes. Redirects <code>sys.stdout</code> streams dynamically to extract planning traces.", style_body)
        ],
        [
            Paragraph("static/ (HTML/CSS/JS)", style_body),
            Paragraph("Implements the user dashboard. Renders interactive chats, parses markdown text, dynamically builds collapsible traces of the agent loop, and populates task cards and timelines.", style_body)
        ]
    ]
    
    struct_table = Table(code_structure_data, colWidths=[130, 374])
    struct_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(struct_table)
    
    story.append(Paragraph("Object State Properties", style_heading2))
    story.append(Paragraph("• <b>Client Connection</b>: The <code>genai.Client</code> is loaded with an API key extracted from <code>.env</code>. It connects to the <code>gemini-2.5-flash</code> model.", style_bullet))
    story.append(Paragraph("• <b>History Store (Conversational)</b>: Holds standard <code>types.Content</code> instances with alternating roles (<code>user</code>, <code>model</code>, and <code>tool</code>). This structure preserves conversational context across multiple inputs.", style_bullet))
    story.append(Paragraph("• <b>Memory Store (Structured)</b>: List of dicts in <code>_tasks</code> containing <code>name</code> and <code>due</code> keys, which are parsed and processed during schedule calculation.", style_bullet))
    
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 3: THE PLAN-ACT LOOP & WORKFLOW
    # ----------------------------------------------------
    story.append(Paragraph("2. The Plan-Act Execution Loop Workflow", style_heading1))
    story.append(Spacer(1, 5))
    
    loop_intro = (
        "The agent implements an explicit <b>Plan-Act loop</b> manually managed in <code>agent.py</code>. By disabling "
        "automatic function calling, the application intercepts Gemini's intent responses, executes the Python tools "
        "locally, logs the parameters/results, and feeds the outputs back into the conversation history. "
        "This structural visibility allows for exact tracing of the system's operational pathways."
    )
    story.append(Paragraph(loop_intro, style_body))
    story.append(Spacer(1, 5))
    
    # Flowchart 1: Plan-Act Loop
    story.append(create_flowchart_drawing())
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Plan-Act Workflow Steps", style_heading2))
    story.append(Paragraph("1. <b>User Input Ingestion</b>: The message from the browser is packed as a <code>types.Content</code> object with role <code>'user'</code> and saved in the history list.", style_bullet))
    story.append(Paragraph("2. <b>Planning Turn (LLM Query)</b>: The entire history list and tool function declarations are posted to the model. The model analyzes the request, referencing constraints from the system instructions.", style_bullet))
    story.append(Paragraph("3. <b>Decision Evaluation (Branch)</b>: The response object is inspected for the presence of <code>function_calls</code>. If present, it transitions to the <i>Act Phase</i>; otherwise, it exits the loop with a <i>Final Response</i>.", style_bullet))
    story.append(Paragraph("4. <b>Action Phase (Tool Call)</b>: The agent loops through each function call requested by the model. It matches the signature to either <code>tools.add_task</code> or <code>tools.build_schedule</code>, runs the method locally, wraps the result in a <code>types.Content</code> instance with role <code>'tool'</code>, appends it to the history, and re-queries the model.", style_bullet))
    
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 4: TOOL LOGIC & DATE PARSING
    # ----------------------------------------------------
    story.append(Paragraph("3. Tool Logic & Date Parsing Heuristics", style_heading1))
    story.append(Spacer(1, 5))
    
    parsing_intro = (
        "The scheduling capabilities depend on two tools in <code>tools.py</code>: <code>add_task</code> and "
        "<code>build_schedule</code>. A core developer challenge in building date-aware agents is handling the "
        "variation in user inputs (e.g. 'September 5', 'Sep 2', '2026-09-02'). The parsing pipeline in "
        "<code>tools.py</code> handles this variation dynamically."
    )
    story.append(Paragraph(parsing_intro, style_body))
    story.append(Spacer(1, 5))
    
    # Flowchart 2: Parser Workflow
    story.append(create_parser_flowchart_drawing())
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Custom Date Parsing Algorithm", style_heading2))
    story.append(Paragraph("1. <b>Token Cleaning</b>: Strips commas, periods, and ordinal suffixes (e.g. converting '5th' to '5', '2nd' to '2') using character filters.", style_bullet))
    story.append(Paragraph("2. <b>ISO & Format Match</b>: Attempts parsing against several standard patterns (<code>%Y-%m-%d</code>, <code>%d-%m-%Y</code>, <code>%m/%d/%Y</code>).", style_bullet))
    story.append(Paragraph("3. <b>Text Month Mapping</b>: If standard format matching fails, the parser matches word tokens against a mapping of full/abbreviated month names (e.g., 'sep' or 'september' to month 9) and extracts the day integer.", style_bullet))
    
    story.append(Paragraph("The Date Anchoring Resolution (Honest Failure)", style_heading2))
    failure_text = (
        "<b>Challenge:</b> In early designs, using the live system date (<code>datetime.now()</code>) for timeline calculation "
        "caused problems. If the scripts were run after the actual task deadlines (September 2 and 5), the scheduler would "
        "flag these tasks as occurring in the past, resulting in invalid study blocks.<br/>"
        "<b>Resolution:</b> The system anchors the schedule base to a fixed calendar reference date of <b>August 27, 2026</b>. "
        "This ensures study block calculations always compile correctly, maintaining code stability."
    )
    fail_table = Table([[Paragraph(failure_text, style_body)]], colWidths=[504])
    fail_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fffbeb")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#fef3c7")),
        ('LINELEFT', (0, 0), (-1, -1), 3.0, colors.HexColor("#d97706")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(fail_table)
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # PAGE 5: DEVELOPER GUIDE, API CONTRACT & FUTURE SCOPE
    # ----------------------------------------------------
    story.append(Paragraph("4. Developer Integration Guide & Future Scope", style_heading1))
    story.append(Spacer(1, 5))
    
    story.append(Paragraph("Web API Server Contract", style_heading2))
    
    api_data = [
        [Paragraph("<b>Route / Method</b>", style_metadata_label), Paragraph("<b>Request Body</b>", style_metadata_label), Paragraph("<b>Response / Payload Contract</b>", style_metadata_label)],
        [
            Paragraph("<code>/api/status</code> (GET)", style_code),
            Paragraph("None", style_body),
            Paragraph("<code>{'ready': True/False, 'error': str}</code><br/>Checks if Gemini API Key is configured.", style_body)
        ],
        [
            Paragraph("<code>/api/tasks</code> (GET)", style_code),
            Paragraph("None", style_body),
            Paragraph("<code>[{'name': str, 'due': str}]</code><br/>Retrieves registered tasks from memory.", style_body)
        ],
        [
            Paragraph("<code>/api/chat</code> (POST)", style_code),
            Paragraph("<code>{'message': str}</code>", style_body),
            Paragraph("<code>{'response': str, 'steps': list, 'tasks': list}</code><br/>Returns agent response and Plan-Act loop traces.", style_body)
        ],
        [
            Paragraph("<code>/api/clear</code> (POST)", style_code),
            Paragraph("None", style_body),
            Paragraph("<code>{'status': 'success', 'message': str}</code><br/>Resets task array and conversation history.", style_body)
        ]
    ]
    
    api_table = Table(api_data, colWidths=[120, 100, 284])
    api_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(api_table)
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("Developer Launch Details", style_heading2))
    story.append(Paragraph("• <b>Local Environment Configuration</b>: A <code>.env</code> file must be initialized at the root of the project with the parameter <code>GEMINI_API_KEY=your_key</code>.", style_bullet))
    story.append(Paragraph("• <b>Startup Command</b>: Run <code>python app.py</code>. The server mounts on port <code>5000</code>. Access the graphical interface via browser at <code>http://127.0.0.1:5000</code>.", style_bullet))
    
    story.append(Paragraph("Future Architectural Enhancements", style_heading2))
    story.append(Paragraph("1. <b>Persistent Database Layer</b>: Transitioning the array structure in <code>memory.py</code> to SQLite to keep records across system restarts.", style_bullet))
    story.append(Paragraph("2. <b>Dynamic Buffer Allocations</b>: Replacing linear study spans with overlapping conflict checks to support complex academic schedules.", style_bullet))
    
    story.append(Spacer(1, 10))
    
    # GitHub Reference Section (Callout Card)
    github_card_text = (
        "<b>Codebase Repository Access</b><br/>"
        "The complete source code, developer commits history, Jupyter notebook test runs, and web assets are available "
        "publicly. Access resources, clone repository, or open issues at:<br/>"
        "<b>GitHub link:</b> <a href='https://github.com/nvsaigokul-sudo/AI-Agent'>https://github.com/nvsaigokul-sudo/AI-Agent</a>"
    )
    
    git_table = Table([[Paragraph(github_card_text, style_body)]], colWidths=[504])
    git_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#dcfce7")),
        ('LINELEFT', (0, 0), (-1, -1), 3.0, colors.HexColor("#16a34a")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(git_table)
    
    doc.build(story, canvasmaker=NumberedCanvas)


if __name__ == "__main__":
    downloads_dir = get_downloads_path()
    output_pdf = os.path.join(downloads_dir, "Study_Planner_Agent_Project_Report.pdf")
    print(f"Generating PDF at: {output_pdf}")
    build_pdf(output_pdf)
    print("PDF generation completed successfully.")
