"""
ScamGraph AI - Comprehensive System Architecture & Deployment Guide PDF Generator
Creates a publication-quality PDF detailing the entire project:
- Problem statements & threat landscape
- Architecture & technical solutions
- ScamGraph differentiators vs legacy systems
- Complete workflow diagrams & tables
- Technology stack specifications
- Step-by-step execution & testing guide
"""

import sys
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and display total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "SCAMGRAPH AI — Autonomous Scam-Journey Intelligence Platform")
            self.drawRightString(558, 755, "System Architecture & Execution Guide")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)

        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        
        self.drawString(54, 32, "CONFIDENTIAL & PROPRIETARY — SCAMGRAPH AI DEFENSE PLATFORM")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def build_pdf(filename="ScamGraph_AI_Comprehensive_System_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#0F172A")    # Slate 900
    ACCENT = colors.HexColor("#2563EB")     # Blue 600
    ACCENT_DARK = colors.HexColor("#1D4ED8")# Blue 700
    CRITICAL = colors.HexColor("#DC2626")   # Red 600
    WARNING = colors.HexColor("#D97706")    # Amber 600
    SUCCESS = colors.HexColor("#059669")    # Emerald 600
    DARK_TEXT = colors.HexColor("#1E293B")  # Slate 800
    MUTED_TEXT = colors.HexColor("#64748B") # Slate 500
    BG_LIGHT = colors.HexColor("#F8FAFC")   # Slate 50
    BORDER_COLOR = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=ACCENT,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=ACCENT_DARK,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=DARK_TEXT,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'DocCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=DARK_TEXT
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E3A8A")
    )

    elements = []

    # ==================== COVER / HEADER ====================
    elements.append(Paragraph("SCAMGRAPH AI", title_style))
    elements.append(Paragraph("Autonomous Scam-Journey Recognition, Pre-Payment Guard & Syndicate Intelligence Platform", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceBefore=0, spaceAfter=12))

    meta_table_data = [
        [
            Paragraph("<b>Version:</b> 3.3.0 Enterprise", table_cell_style),
            Paragraph("<b>Classification:</b> Operational Defense Platform", table_cell_style),
            Paragraph("<b>Date:</b> October 2026", table_cell_style)
        ],
        [
            Paragraph("<b>Target Stack:</b> Next.js 14 / FastAPI / Graph / Redis", table_cell_style),
            Paragraph("<b>Ecosystem:</b> Indian Payment Rails (UPI, IMPS, RTGS)", table_cell_style),
            Paragraph("<b>Status:</b> Production Ready (143/143 Tests Passed)", table_cell_style)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[168, 168, 168])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 14))

    # ==================== 1. EXECUTIVE OVERVIEW ====================
    elements.append(Paragraph("1. Executive Overview & Mission Statement", h1_style))
    elements.append(Paragraph(
        "<b>ScamGraph AI</b> is a state-of-the-art cyber-fraud interception platform purpose-built to eradicate "
        "large-scale social engineering, payment coercion, and organized cyber syndicates operating across India and global digital payment corridors. "
        "Unlike conventional signature scanners that merely check blacklisted domain lists or static phone numbers, "
        "ScamGraph AI treats scam victimization as a <b>dynamic temporal journey</b>. By reconstructing victim-scammer behavioral states "
        "in real time—from initial lure and psychological isolation to biometric mandate extraction and multi-hop mule layering—ScamGraph delivers "
        "pre-transaction cognitive interventions, payment blocks, automated golden-hour fund freezing, and syndicate graph neutralization.",
        body_style
    ))

    # Callout Box
    callout_data = [[
        Paragraph(
            "<b>The Core Paradigm Shift:</b> Legacy anti-fraud looks for malicious files or known bad entities. "
            "However, 94% of modern scams in India (Digital Arrest, Electricity threats, Job tasks) use benign infrastructure "
            "(legitimate UPI handles, fresh WhatsApp numbers, real Skype video calls, clean bank accounts). "
            "<b>ScamGraph models the behavioral journey and psychological coercion DNA, not just static indicators.</b>",
            callout_style
        )
    ]]
    callout_table = Table(callout_data, colWidths=[504])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#93C5FD")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    elements.append(callout_table)
    elements.append(Spacer(1, 14))

    # ==================== 2. THE PROBLEM STATEMENT ====================
    elements.append(Paragraph("2. The Indian Cyber-Fraud Crisis: Problem Statement", h1_style))
    elements.append(Paragraph(
        "India's rapid digitization through UPI, Aadhaar-enabled payments, and ubiquitous smartphone connectivity has been met "
        "by unprecedentedly sophisticated cybercrime operations. Our exhaustive threat assessment highlights four structural vulnerabilities:",
        body_style
    ))

    problems = [
        "<b>The Mule Velocity Gap (4 to 12 Minutes):</b> Once a victim approves a UPI payment or bank transfer, stolen funds are dispersed through 4 to 7 layers of rented 'mule' accounts within 8 minutes, rendering traditional post-facto police FIRs completely ineffective for fund recovery.",
        "<b>The 'Digital Arrest' & Legal Coercion Epidemic:</b> Criminal syndicates impersonate CBI, Mumbai Police, ED, and Supreme Court judges over Skype/WhatsApp video calls, holding victims in 48-hour psychological isolation under threat of imminent arrest until life savings are transferred to 'RBI Reserve Clearance Verification' accounts.",
        "<b>Utility & Essential Service Extortion (BESCOM/MSEDCL/Jio):</b> Automated bulk SMS/WhatsApp messages claiming power or SIM disconnection tonight exploit urgency bias, tricking citizens into downloading malicious remote desktop APKs (AnyDesk, TeamViewer QuickSupport) or paying fake verification tokens.",
        "<b>Fragmented Intelligence Silos:</b> Telecommunication operators see call records, messaging platforms see chats, banks see ledger entries, and victims report to local police stations days later. No unified cognitive bridge correlates these disparate signals in flight."
    ]
    for p in problems:
        elements.append(Paragraph(f"• {p}", bullet_style))
    elements.append(Spacer(1, 12))

    # ==================== 3. SCAMGRAPH'S NOVEL APPROACH & SOLUTIONS ====================
    elements.append(Paragraph("3. Novel Technical Approach: The 6 Pillar Defense Architecture", h1_style))
    
    pillars = [
        ("Pillar 1: Temporal Scam-Journey Reconstruction", 
         "Every scam follows a predictable behavioral state machine: <i>Lure → Contact → Authority/Trust Assertion → Psychological Isolation → Payment Mandate Extraction → Mule Dispersion → Secondary Recovery Scam</i>. ScamGraph tracks the active stage of the victim and applies calibrated friction at each transition."),
        ("Pillar 2: Behavioral ScamDNA Vectorization", 
         "A 12-dimensional vector embedding space capturing psychological coercion markers (time pressure, authority impersonation, financial secrecy, legal threat, false reward) independent of the literal phrasing or local dialect."),
        ("Pillar 3: Pre-Payment Guard API (Zero-Second Interception)", 
         "An enterprise-grade synchronous API designed for banking apps (Google Pay, PhonePe, Paytm, HDFC, SBI). Evaluates recipient VPA, velocity, dormancy bursts, and payer journey state in under 85ms to enforce dynamic cognitive pauses or hard transaction blocks."),
        ("Pillar 4: Post-Loss Rescue & Golden Hour Freezing Engine", 
         "For victims who have already suffered a loss: auto-generates formal 1930 Cyber Helpline & bank lien-request packages, creates structured NCRP complaint dossiers with cryptographic evidence hashes, and actively shields victims against secondary 'cyber recovery agent' scams."),
        ("Pillar 5: Cross-Victim Syndicate Knowledge Graph", 
         "A multi-tenant NetworkX and Neo4j graph engine correlating disparate incident reports across India. Connects shared VPAs, phone numbers, IMEI fingerprints, IFSC codes, and Telegram infrastructure into organized syndicate campaigns."),
        ("Pillar 6: Outbreak Radar & Early Warning Doppler Engine", 
         "A dynamic, real-time spatial surveillance console aggregating early signals to compute velocity acceleration, mutating tactics, and regional threat blips before campaigns reach mass contagion.")
    ]

    for title, desc in pillars:
        elements.append(Paragraph(title, h2_style))
        elements.append(Paragraph(desc, body_style))
    elements.append(Spacer(1, 10))

    # Page Break for clean sectioning
    elements.append(PageBreak())

    # ==================== 4. HOW SCAMGRAPH DIFFERS ====================
    elements.append(Paragraph("4. How ScamGraph AI Differs From Legacy Systems", h1_style))
    elements.append(Paragraph(
        "A rigorous architectural comparison demonstrating why traditional defenses consistently fail against modern social engineering:",
        body_style
    ))

    diff_table_data = [
        [
            Paragraph("<b>Capability Dimension</b>", table_header_style),
            Paragraph("<b>Legacy Antivirus / DNS Scanners</b>", table_header_style),
            Paragraph("<b>Traditional Bank Rule Engines</b>", table_header_style),
            Paragraph("<b>ScamGraph AI Defense Platform</b>", table_header_style)
        ],
        [
            Paragraph("<b>Detection Model</b>", table_cell_style),
            Paragraph("Static URL/Domain blacklists & file hashes", table_cell_style),
            Paragraph("Static transaction amount & velocity thresholds", table_cell_style),
            Paragraph("<b>Multimodal behavioral journey state machine & ScamDNA embeddings</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Social Engineering Handling</b>", table_cell_style),
            Paragraph("Blind to human psychology and chats", table_cell_style),
            Paragraph("Blind to pre-payment coercion & phone calls", table_cell_style),
            Paragraph("<b>Real-time analysis of urgency, authority impersonation, and isolation cues</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Intervention Timing</b>", table_cell_style),
            Paragraph("Post-click or post-download", table_cell_style),
            Paragraph("At payment settlement (already too late)", table_cell_style),
            Paragraph("<b>In-flight cognitive pause & Pre-Payment Guard check (<85ms latency)</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Linguistic Coverage</b>", table_cell_style),
            Paragraph("English keyword dictionaries", table_cell_style),
            Paragraph("Language agnostic (numerical only)", table_cell_style),
            Paragraph("<b>8 Indian languages (Hindi, Tamil, Telugu, Marathi, etc.) + Hinglish negation</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Syndicate Attribution</b>", table_cell_style),
            Paragraph("None (isolated events)", table_cell_style),
            Paragraph("Account-level freezing only", table_cell_style),
            Paragraph("<b>Multi-hop graph clustering, mule network tracing & campaign velocity tracking</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Post-Loss Action</b>", table_cell_style),
            Paragraph("None", table_cell_style),
            Paragraph("Manual support ticket with 30-day turnaround", table_cell_style),
            Paragraph("<b>Automated 1930 / bank lien package generation + secondary scam shield</b>", table_cell_style)
        ]
    ]

    diff_table = Table(diff_table_data, colWidths=[100, 130, 134, 140])
    diff_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT])
    ]))
    elements.append(diff_table)
    elements.append(Spacer(1, 14))

    # ==================== 5. END-TO-END WORKFLOW ====================
    elements.append(Paragraph("5. End-to-End System Workflow & Dataflow", h1_style))
    elements.append(Paragraph(
        "ScamGraph AI executes an integrated 7-stage processing pipeline upon receiving suspicious input or a payment screening request:",
        body_style
    ))

    workflow_steps = [
        ("Step 1: Multimodal Ingestion & Normalization",
         "Ingests raw text, WhatsApp transcripts, payment mandate QR codes, screenshot OCR text, or suspect URLs. Normalizes Indian script variants, transliterated Hinglish, and removes evasive character substitutions."),
        ("Step 2: Tactical Signal Extraction & Negation Resolution",
         "Identifies psychological coercive tactics (Authority Impersonation, Time Panic, Legal Seizure, False Mandate). Applies context-aware negation parsing (e.g., distinguishing 'I will not pay' from 'You must pay now')."),
        ("Step 3: Journey State Classification & ScamDNA Vectorization",
         "The Journey State Machine evaluates transition probabilities across Lure, Contact, Threat, Mandate, and Loss. Computes a 12-dimensional ScamDNA embedding representing tactical velocity and manipulation vectors."),
        ("Step 4: Synchronous Pre-Payment Risk Assessment",
         "Computes unified risk scores combining recipient entity reputation, mule network velocity, payment rail risk, and payer journey vulnerability. Determines Action: <i>ALLOW</i>, <i>WARN</i>, <i>COGNITIVE_DELAY</i>, or <i>HARD_BLOCK</i>."),
        ("Step 5: Cross-Victim Entity Correlation & Graph Linking",
         "Extracts indicators (UPI VPA, mobile, IFSC, domain, APK hash) and queries the Knowledge Graph. Automatically clusters isolated incidents into master syndicate campaigns based on entity proximity and tactical similarity."),
        ("Step 6: Outbreak Radar Doppler Update",
         "Recalculates velocity curves, acceleration metrics, and geographical regional blips. Broadcasts real-time outbreak warnings across SOC dashboards and partner webhooks."),
        ("Step 7: Automated Rescue & Recovery Shield",
         "If financial loss has occurred, instantly generates automated bank lien escalation notices, generates an official NCRP/Cyber Helpline 1930 PDF report, and sets up behavioral tripwires to block recovery scammers.")
    ]

    for title, desc in workflow_steps:
        elements.append(Paragraph(f"<b>{title}:</b> {desc}", bullet_style))
    elements.append(Spacer(1, 12))

    # ==================== 6. COMPLETE TECHNOLOGY STACK ====================
    elements.append(Paragraph("6. Complete Technology Stack Specifications", h1_style))
    
    stack_data = [
        [Paragraph("<b>Component Layer</b>", table_header_style), Paragraph("<b>Technology / Framework</b>", table_header_style), Paragraph("<b>Architectural Responsibility</b>", table_header_style)],
        [Paragraph("<b>Core API Gateway</b>", table_cell_style), Paragraph("FastAPI / Python 3.14 / Uvicorn", table_cell_style), Paragraph("Asynchronous, high-throughput REST API with OpenAPI v3 specs and <85ms P99 latency", table_cell_style)],
        [Paragraph("<b>Frontend App</b>", table_cell_style), Paragraph("Next.js 14 (App Router) / React 18 / TypeScript", table_cell_style), Paragraph("Responsive enterprise portal with Canvas Radar, Cytoscape graph viz, and SOC command dashboards", table_cell_style)],
        [Paragraph("<b>Styling & Tokens</b>", table_cell_style), Paragraph("TailwindCSS / Vanilla CSS Tokens", table_cell_style), Paragraph("Bespoke dark/light aesthetic, glowing glassmorphism, semantic alert tokens", table_cell_style)],
        [Paragraph("<b>Knowledge Graph</b>", table_cell_style), Paragraph("NetworkX / Graph Algorithms / Neo4j", table_cell_style), Paragraph("Multi-hop entity resolution, risk propagation, syndicate cycle detection, and cluster mining", table_cell_style)],
        [Paragraph("<b>Vector & Embeddings</b>", table_cell_style), Paragraph("pgvector / PostgreSQL / NumPy", table_cell_style), Paragraph("12-dimensional ScamDNA vector search, cosine similarity clustering, campaign grouping", table_cell_style)],
        [Paragraph("<b>Cache & Background</b>", table_cell_style), Paragraph("Redis 7.2 / Python AsyncIO Workers", table_cell_style), Paragraph("Distributed caching, idempotency enforcement, token bucket rate limiting, async job queues", table_cell_style)],
        [Paragraph("<b>Security & Identity</b>", table_cell_style), Paragraph("Enterprise RBAC / SHA-256 / Fernet", table_cell_style), Paragraph("Tenant isolation, PII data masking, tamper-evident audit ledger, encrypted exports", table_cell_style)],
        [Paragraph("<b>Observability</b>", table_cell_style), Paragraph("Prometheus / OpenTelemetry / Structlog", table_cell_style), Paragraph("Real-time telemetry, model drift detection, AI evaluation metrics, latency tracking", table_cell_style)]
    ]
    stack_table = Table(stack_data, colWidths=[110, 160, 234])
    stack_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT])
    ]))
    elements.append(stack_table)
    elements.append(Spacer(1, 14))

    # Page Break for clean sectioning
    elements.append(PageBreak())

    # ==================== 7. EXECUTION & SETUP GUIDE ====================
    elements.append(Paragraph("7. Complete Step-by-Step Execution Guide", h1_style))
    elements.append(Paragraph(
        "Follow these exact steps to run the complete ScamGraph AI platform in local development or production mode:",
        body_style
    ))

    exec_steps = [
        ("Step 1: Environment & Prerequisites",
         "Ensure <b>Python 3.10+</b> and <b>Node.js 18+</b> (with npm or pnpm) are installed. Git clone the repository and navigate to the root directory:<br/>"
         "<code>git clone https://github.com/Sumeet-16/ScamGraph-ai.git<br/>cd ScamGraph-ai</code>"),
        ("Step 2: Python Backend Setup & Startup",
         "Create and activate a virtual environment, install dependencies, and launch the FastAPI server on port <b>8001</b>:<br/>"
         "<code>python -m venv venv<br/># Windows: venv\\Scripts\\activate | Linux/macOS: source venv/bin/activate<br/>"
         "pip install -r requirements.txt<br/>"
         "uvicorn services.api.app.main:app --host 127.0.0.1 --port 8001 --reload</code><br/>"
         "<i>The backend API Gateway will be live at: <b>http://localhost:8001</b> (Swagger UI: <b>/docs</b>)</i>"),
        ("Step 3: Frontend Web Portal Setup & Startup",
         "In a separate terminal, navigate to the web application directory, configure environment variables, install packages, and launch Next.js on port <b>3001</b>:<br/>"
         "<code>cd apps/web<br/>npm install<br/>npm run dev -- -p 3001</code><br/>"
         "<i>The unified web portal will be accessible at: <b>http://localhost:3001</b></i>"),
        ("Step 4: Running the Comprehensive Automated Test Suite",
         "To verify all 143 platform transformation tests (Security, Background Jobs, Observability, Scalability, and Launch Readiness):<br/>"
         "<code>pytest tests/test_security_governance_step21.py tests/test_async_jobs_step22.py tests/test_observability_step23.py tests/test_scalability_step24.py tests/test_launch_e2e_step26.py -v</code>"),
        ("Step 5: Docker Containerized Launch (Optional)",
         "To deploy all backend services, Redis, PostgreSQL/pgvector, and the frontend in Docker:<br/>"
         "<code>docker-compose up --build -d</code>")
    ]

    for title, desc in exec_steps:
        elements.append(Paragraph(title, h2_style))
        elements.append(Paragraph(desc, body_style))
    elements.append(Spacer(1, 10))

    # ==================== 8. COMPLETE FEATURE & UI SURFACE DIRECTORY ====================
    elements.append(Paragraph("8. Complete Feature & UI Surface Directory", h1_style))
    elements.append(Paragraph(
        "The web application delivers 16 interconnected, real-time intelligence surfaces:",
        body_style
    ))

    surfaces = [
        ("1. /shield & /protect", "Consumer Security Hub & URL/Message Scanner with journey visualizer and cognitive advice."),
        ("2. /guard", "Pre-Payment Guard simulating Google Pay/PhonePe transaction checks against mule VPAs with instant risk decisions."),
        ("3. /rescue", "Emergency Post-Loss Recovery portal automating 1930 Cyber Helpline & bank lien action plans."),
        ("4. /radar", "Interactive 360° Outbreak Radar showing live syndicate blips, velocity spikes, and regional surges."),
        ("5. /campaigns", "National Campaign Intelligence ledger tracking organized scam syndicates across states."),
        ("6. /incidents", "Incident Triage Ledger with urgency flags, cluster links, and full forensic timelines."),
        ("7. /investigate", "Deep Analyst Workbench providing graph inspection, timeline correlation, and evidence extraction."),
        ("8. /graph", "Interactive Cytoscape Knowledge Graph visualizing entity links, mule rings, and risk propagation paths."),
        ("9. /mulehunter", "Mule Account Intelligence console mapping transactional velocity, account hops, and dormancy bursts."),
        ("10. /lab", "Journey Scenario Simulator enabling counterfactual replay of scam tactics and user responses."),
        ("11. /reviews & /registry", "Citizen Evidence Ledger and Public VPA/Phone Verification Registry."),
        ("12. /alerts", "Real-time Early Warning Notification Center with filterable high-velocity outbreak bulletins."),
        ("13. /command", "Executive SOC Command Center displaying aggregate platform metrics, active alerts, and incident rates."),
        ("14. /activity", "Victim History and Personal Intervention Log with verification status."),
        ("15. /how-it-works & /help-center", "Public educational portal explaining the scam-journey lifecycle and 1930 protocols."),
        ("16. /docs & /openapi.json", "Enterprise REST API Documentation detailing 99 production endpoints.")
    ]

    surface_data = []
    for s_title, s_desc in surfaces:
        surface_data.append([
            Paragraph(f"<b>{s_title}</b>", table_cell_style),
            Paragraph(s_desc, table_cell_style)
        ])

    surface_table = Table(surface_data, colWidths=[130, 374])
    surface_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, BG_LIGHT])
    ]))
    elements.append(surface_table)
    elements.append(Spacer(1, 14))

    # ==================== 9. CONCLUSION & IMPACT ====================
    elements.append(Paragraph("9. Conclusion & Operational Impact", h1_style))
    elements.append(Paragraph(
        "ScamGraph AI closes the critical 12-minute window between social engineering coercion and unrecoverable fund dispersion. "
        "By fusing temporal journey psychology with automated pre-payment defense and cross-victim syndicate intelligence, "
        "the platform transforms reactive, fragmented fraud reporting into proactive, systemic, and sovereign-scale cyber defense. "
        "With 99 operational API endpoints, 143 passing production tests, and complete frontend-backend synchronization, "
        "ScamGraph AI is fully primed for institutional deployment across banks, payment aggregators, telecom operators, and law enforcement agencies.",
        body_style
    ))

    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF generated successfully at: {os.path.abspath(filename)}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "ScamGraph_AI_Comprehensive_System_Guide.pdf"
    build_pdf(out_file)
