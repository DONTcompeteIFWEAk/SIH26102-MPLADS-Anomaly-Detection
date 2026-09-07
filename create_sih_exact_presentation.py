import os
import subprocess
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Exact Colors matching SIH Screenshot Template
    C_WHITE = RGBColor(255, 255, 255)
    C_NAVY_TITLE = RGBColor(29, 68, 119)     # #1D4477 Dark Blue serif on Title slide
    C_BLACK = RGBColor(0, 0, 0)
    C_DARK_TEXT = RGBColor(15, 23, 42)       # #0F172A Deep dark text
    C_BLUE_BANNER = RGBColor(15, 98, 172)    # #0F62AC Blue bottom banner
    C_HEADING_BLUE = RGBColor(30, 90, 153)   # #1E5A99 Sub-heading blue
    C_PURPLE_OVAL = RGBColor(91, 62, 132)    # #5B3E84 Team Oval border
    C_BOX_BG = RGBColor(248, 250, 252)       # #F8FAFC
    C_BOX_BORDER = RGBColor(203, 213, 225)   # #CBD5E1
    C_CYAN_ACCENT = RGBColor(2, 132, 199)

    logo_path = r"c:\Users\aksha\Desktop\SIH26102\sih_logo.png"
    bulb_center_path = r"c:\Users\aksha\Desktop\SIH26102\sih_bulb_center.png"

    def set_white_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_WHITE
        bg.line.fill.background()
        return bg

    def add_bottom_banner(slide, slide_num):
        # Blue bar across bottom
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(6.8), Inches(13.333), Inches(0.7))
        bar.fill.solid()
        bar.fill.fore_color.rgb = C_BLUE_BANNER
        bar.line.fill.background()

        # Center text: @SIH Idea submission- Template
        c_box = slide.shapes.add_textbox(Inches(3.0), Inches(6.88), Inches(7.333), Inches(0.5))
        tf_c = c_box.text_frame
        tf_c.word_wrap = True
        p_c = tf_c.paragraphs[0]
        p_c.text = "@SIH Idea submission- Template"
        p_c.font.size = Pt(11)
        p_c.font.color.rgb = C_WHITE
        p_c.alignment = PP_ALIGN.CENTER

        # Right slide number
        r_box = slide.shapes.add_textbox(Inches(12.0), Inches(6.88), Inches(1.0), Inches(0.5))
        tf_r = r_box.text_frame
        p_r = tf_r.paragraphs[0]
        p_r.text = str(slide_num)
        p_r.font.size = Pt(12)
        p_r.font.bold = True
        p_r.font.color.rgb = C_WHITE
        p_r.alignment = PP_ALIGN.RIGHT

    def add_top_elements(slide, title_text, team_name="Your\nTeam\nName"):
        # Top-Left Oval: Team Name
        oval = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.6), Inches(0.35), Inches(1.3), Inches(1.05))
        oval.fill.solid()
        oval.fill.fore_color.rgb = C_WHITE
        oval.line.color.rgb = C_PURPLE_OVAL
        oval.line.width = Pt(2)
        tf_o = oval.text_frame
        tf_o.word_wrap = True
        p_o = tf_o.paragraphs[0]
        p_o.text = team_name
        p_o.font.size = Pt(10)
        p_o.font.color.rgb = C_DARK_TEXT
        p_o.font.name = "Times New Roman"
        p_o.alignment = PP_ALIGN.CENTER

        # Top-Center: Slide Title in serif bold
        t_box = slide.shapes.add_textbox(Inches(2.5), Inches(0.4), Inches(7.5), Inches(0.8))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = C_BLACK
        p_t.font.name = "Times New Roman"
        p_t.alignment = PP_ALIGN.CENTER

        # Top-Right: SIH Logo
        if os.path.exists(logo_path):
            slide.shapes.add_picture(logo_path, Inches(10.5), Inches(0.25), width=Inches(2.4))

    def add_card(slide, left, top, width, height, bg_color=C_BOX_BG, border_color=C_BOX_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
        return card

    # =========================================================
    # SLIDE 1: TITLE PAGE (Exact Match to Screenshot 1)
    # =========================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_white_bg(s1)

    # Top-Right SIH Logo
    if os.path.exists(logo_path):
        s1.shapes.add_picture(logo_path, Inches(10.5), Inches(0.25), width=Inches(2.4))

    # Top Center: SMART INDIA HACKATHON 2026
    sih_title_box = s1.shapes.add_textbox(Inches(1.5), Inches(0.4), Inches(8.8), Inches(0.7))
    tf_sih = sih_title_box.text_frame
    p_sih = tf_sih.paragraphs[0]
    p_sih.text = "SMART INDIA HACKATHON 2026"
    p_sih.font.size = Pt(26)
    p_sih.font.bold = True
    p_sih.font.color.rgb = C_NAVY_TITLE
    p_sih.font.name = "Times New Roman"
    p_sih.alignment = PP_ALIGN.CENTER

    # Title Subtitle: TITLE PAGE
    tp_box = s1.shapes.add_textbox(Inches(2.5), Inches(1.2), Inches(6.8), Inches(0.6))
    tf_tp = tp_box.text_frame
    p_tp = tf_tp.paragraphs[0]
    p_tp.text = "TITLE PAGE"
    p_tp.font.size = Pt(20)
    p_tp.font.bold = True
    p_tp.font.color.rgb = C_BLACK
    p_tp.font.name = "Times New Roman"
    p_tp.alignment = PP_ALIGN.CENTER

    # Center-Right: Large SIH Bulb Graphic
    if os.path.exists(bulb_center_path):
        s1.shapes.add_picture(bulb_center_path, Inches(7.5), Inches(1.6), width=Inches(4.8))

    # Left Side: Mandatory SIH Fields
    l_box = s1.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(6.8), Inches(4.8))
    tf_l = l_box.text_frame
    tf_l.word_wrap = True

    fields = [
        ("• Problem Statement ID –", " SIH26102"),
        ("• Problem Statement Title-", " Autonomous Public Fund Anomaly Detection & Temporal Forensics System for MPLADS"),
        ("• Theme-", " Smart Governance & Public Financial Surveillance"),
        ("• PS Category- Software/Hardware", " Software"),
        ("• Team ID-", " [Team ID]"),
        ("• Team Name (Registered on portal)", " [Team Name]")
    ]

    for i, (label, val) in enumerate(fields):
        p = tf_l.paragraphs[0] if i == 0 else tf_l.add_paragraph()
        r1 = p.add_run(); r1.text = label; r1.font.bold = True; r1.font.size = Pt(17); r1.font.color.rgb = C_BLACK; r1.font.name = "Times New Roman"
        r2 = p.add_run(); r2.text = val; r2.font.bold = False; r2.font.size = Pt(16); r2.font.color.rgb = RGBColor(30, 41, 59); r2.font.name = "Times New Roman"
        p.space_before = Pt(16)

    # =========================================================
    # SLIDE 2: IDEA TITLE / PROPOSED SOLUTION (Screenshot 2)
    # =========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_white_bg(s2)
    add_top_elements(s2, "IDEA TITLE")
    add_bottom_banner(s2, 2)

    # Main Section Heading with Diamond Bullet & Underline
    h2_box = s2.shapes.add_textbox(Inches(0.6), Inches(1.5), Inches(12.0), Inches(0.6))
    tf_h2 = h2_box.text_frame
    p_h2 = tf_h2.paragraphs[0]
    p_h2.text = "❖Proposed Solution (Describe your Idea/Solution/Prototype)"
    p_h2.font.size = Pt(18)
    p_h2.font.bold = True
    p_h2.font.underline = True
    p_h2.font.color.rgb = C_HEADING_BLUE
    p_h2.font.name = "Times New Roman"

    # Three Structured Content Cards
    cards_s2 = [
        ("Detailed explanation of the proposed solution", [
            "Dual-Layer Hybrid Intelligence: Integrates a 3-model unsupervised ML ensemble (Isolation Forest 45%, Profile-Deduplicated LOF 35%, PCA 20%) with 5 codified CAG statutory rules.",
            "Real-Time Pre-Sanction Surveillance: Screens 100% of public works transactions before funds leave the treasury, replacing delayed 2-year sample autopsies.",
            "Full Pan-India Scope: Ingests 105,000 authentic civil works across all 33 States & UTs (2019-2024), monitoring ₹6,260 Cr in scheme expenditure."
        ], Inches(0.6), Inches(2.2), Inches(3.9), Inches(4.3)),
        ("How it addresses the problem", [
            "Solves Post-Facto Audit Blindspot: Traditional CAG audits inspect <8% of works 12–24 months late; our system audits 100% in milliseconds (<15ms).",
            "Eliminates GFR 149 Evasion: Flags procurement contract-splitting artificially priced just below ₹5L and ₹10L e-tender thresholds.",
            "Stops Ghost Village Re-Billing: Geospatial NLP cross-references identical works repeated in the same village/block to prevent double-invoicing."
        ], Inches(4.7), Inches(2.2), Inches(3.9), Inches(4.3)),
        ("Innovation and uniqueness of the solution", [
            "🚨 The 'March Rush' Radar: First-ever longitudinal forensic engine detecting fiscal year-end fund dumping in March (3,111 works flagged).",
            "⏳ Chronic Dormancy Engine: Pinpointed ₹287 Cr in 5,960 works stalled >3 years from 2019–2021 for fund clawback.",
            "🇮🇳 Bilingual Usability: Converts math scores into plain English + सरल हिंदी directives with printable official CAG dossiers."
        ], Inches(8.8), Inches(2.2), Inches(3.9), Inches(4.3))
    ]

    for title, bullets, l, t, w, h in cards_s2:
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
        card.fill.solid(); card.fill.fore_color.rgb = C_BOX_BG
        card.line.color.rgb = C_BOX_BORDER
        card.line.width = Pt(1)

        tb = s2.shapes.add_textbox(l + Inches(0.15), t + Inches(0.15), w - Inches(0.3), h - Inches(0.3))
        tf = tb.text_frame; tf.word_wrap = True
        pt = tf.paragraphs[0]; pt.text = f"• {title}:"; pt.font.size = Pt(12); pt.font.bold = True; pt.font.color.rgb = C_NAVY_TITLE; pt.font.name = "Times New Roman"
        for b in bullets:
            pb = tf.add_paragraph(); pb.text = f"  - {b}"; pb.font.size = Pt(10.5); pb.font.color.rgb = C_DARK_TEXT; pb.space_before = Pt(6)

    # =========================================================
    # SLIDE 3: TECHNICAL APPROACH (Screenshot 4 - With FLOWCHART)
    # =========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_white_bg(s3)
    add_top_elements(s3, "TECHNICAL APPROACH")
    add_bottom_banner(s3, 3)

    # Bullet 1: Technologies to be used
    t1_box = s3.shapes.add_textbox(Inches(0.6), Inches(1.4), Inches(12.0), Inches(1.3))
    tf_t1 = t1_box.text_frame; tf_t1.word_wrap = True
    pt1 = tf_t1.paragraphs[0]
    pt1.text = "• Technologies to be used (programming languages, frameworks, hardware)"
    pt1.font.size = Pt(15); pt1.font.bold = True; pt1.font.color.rgb = C_BLACK; pt1.font.name = "Times New Roman"

    tech_p = tf_t1.add_paragraph()
    tech_p.text = "  - AI / ML Decision Engine: Scikit-learn (Isolation Forest, Profile-Deduplicated LOF, PCA SVD), Joblib, NumPy, Pandas\n  - Backend & APIs: FastAPI (Asynchronous Python 3.12), SQLAlchemy ORM, Pydantic V2 schemas, Uvicorn\n  - Database & Ingestion: PostgreSQL 16 (105k works, 557 seats), MoSPI e-SAKSHI live CDC scraper (REST API)\n  - Frontend & GIS: React 18, Vite, Leaflet Geospatial GIS, Recharts Data Visualizer, Responsive CSS (100% Offline Demo)"
    tech_p.font.size = Pt(11); tech_p.font.color.rgb = C_DARK_TEXT; tech_p.space_before = Pt(4)

    # Bullet 2: Methodology & Implementation Flowchart
    t2_box = s3.shapes.add_textbox(Inches(0.6), Inches(2.9), Inches(12.0), Inches(0.5))
    tf_t2 = t2_box.text_frame
    pt2 = tf_t2.paragraphs[0]
    pt2.text = "• Methodology and process for implementation (Flow Charts / Architecture Workflow)"
    pt2.font.size = Pt(15); pt2.font.bold = True; pt2.font.color.rgb = C_BLACK; pt2.font.name = "Times New Roman"

    # VISUAL FLOWCHART: 5 Sequential Pipeline Boxes with Arrows
    flow_steps = [
        ("1. Data Ingestion & Cleansing", "• MoSPI e-SAKSHI Portal API\n• 105,000 Real Works\n• Deduplication & NLP\n• Completeness Scoring"),
        ("2. Feature Engineering", "• Constituency Median Ratio\n• GFR 149 Proximity Flag\n• Village Cluster Matching\n• Days Since Recommendation"),
        ("3. Dual-Layer Hybrid Engine", "• Isolation Forest (45%)\n• Deduplicated LOF (35%)\n• PCA Reconstruction (20%)\n• 5 Codified CAG Rules"),
        ("4. Temporal Forensics", "• 'March Rush' Radar\n• Chronic Dormancy (>3 Yrs)\n• Pre-Poll Election Surges\n• Longitudinal Normalization"),
        ("5. Bilingual Actionable Output", "• Easy English + सरल हिंदी\n• Statutory CAG Directives\n• Printable Audit Dossier\n• Live AI Simulator")
    ]

    for i, (stitle, sbody) in enumerate(flow_steps):
        bx_left = Inches(0.6 + i * 2.45)
        bx_top = Inches(3.55)
        bx_w = Inches(2.25)
        bx_h = Inches(3.0)

        # Flowchart Box
        fbox = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx_left, bx_top, bx_w, bx_h)
        fbox.fill.solid()
        fbox.fill.fore_color.rgb = RGBColor(238, 245, 255) if i % 2 == 0 else RGBColor(245, 248, 255)
        fbox.line.color.rgb = C_BLUE_BANNER
        fbox.line.width = Pt(1.5)

        tb = s3.shapes.add_textbox(bx_left + Inches(0.08), bx_top + Inches(0.1), bx_w - Inches(0.16), bx_h - Inches(0.2))
        tf = tb.text_frame; tf.word_wrap = True
        pt = tf.paragraphs[0]; pt.text = stitle; pt.font.size = Pt(10.5); pt.font.bold = True; pt.font.color.rgb = C_BLUE_BANNER; pt.alignment = PP_ALIGN.CENTER
        
        pb = tf.add_paragraph(); pb.text = sbody; pb.font.size = Pt(9); pb.font.color.rgb = C_DARK_TEXT; pb.space_before = Pt(6)

        # Arrow connector between boxes (except last)
        if i < len(flow_steps) - 1:
            arrow = s3.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, bx_left + bx_w + Inches(0.02), bx_top + Inches(1.3), Inches(0.16), Inches(0.25))
            arrow.fill.solid(); arrow.fill.fore_color.rgb = C_BLUE_BANNER
            arrow.line.fill.background()

    # =========================================================
    # SLIDE 4: FEASIBILITY AND VIABILITY (Screenshot 3)
    # =========================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_white_bg(s4)
    add_top_elements(s4, "FEASIBILITY AND VIABILITY")
    add_bottom_banner(s4, 4)

    feasibility_sections = [
        ("• Analysis of the feasibility of the idea", [
            "Data Feasibility: 100% validated on real authenticated MoSPI data (60,359 baseline works expanded to 105,000 multi-year records spanning 2019-2024 across all 33 States/UTs).",
            "Technical Scalability: Sub-second latency (<15ms per work inference), allowing instant pre-sanction screening as a live middleware plugin inside e-SAKSHI.",
            "Zero Operational Friction: AI model operates exclusively on mandatory fields already submitted by MPs and district authorities (no additional forms required)."
        ]),
        ("• Potential challenges and risks", [
            "Algorithmic Risk (Zero-Distance KNN Collapse): Public works data contains thousands of identical civil works (e.g. ₹1.5L handpumps) that distort standard neighborhood density metrics.",
            "Operational Risk (Field Officer Resistance): District vigilance officers reject black-box AI algorithms because they cannot legally justify scores in parliamentary reviews.",
            "False Positive Risk: Megaprojects (e.g. ₹2 Cr regional trauma center) appear as extreme statistical outliers despite being 100% legitimate and authorized."
        ]),
        ("• Strategies for overcoming these challenges", [
            "Profile-Deduplicated LOF: Canonical feature grouping deduplicates repetitive civil works before distance calculations, preserving true neighborhood integrity.",
            "Bilingual Plain-Language Explainability: Translates mathematical metrics into plain English and सरल हिंदी with exact CAG statutory references (GFR 149, Para 5.2).",
            "Dual-Layer Hybrid Logic & Feedback Loop: Statistically extreme legitimate works pass through CAG rules; human auditor resolutions dynamically calibrate decision thresholds."
        ])
    ]

    curr_top = Inches(1.5)
    for title, bullets in feasibility_sections:
        tb = s4.shapes.add_textbox(Inches(0.6), curr_top, Inches(12.0), Inches(1.6))
        tf = tb.text_frame; tf.word_wrap = True
        pt = tf.paragraphs[0]; pt.text = title; pt.font.size = Pt(14); pt.font.bold = True; pt.font.color.rgb = C_BLACK; pt.font.name = "Times New Roman"
        for b in bullets:
            pb = tf.add_paragraph(); pb.text = f"  - {b}"; pb.font.size = Pt(11); pb.font.color.rgb = C_DARK_TEXT; pb.space_before = Pt(3)
        curr_top += Inches(1.7)

    # =========================================================
    # SLIDE 5: IMPACT AND BENEFITS (Screenshot 5)
    # =========================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_white_bg(s5)
    add_top_elements(s5, "IMPACT AND BENEFITS")
    add_bottom_banner(s5, 5)

    impact_sections = [
        ("• Potential impact on the target audience", [
            "Ministry of Statistics & Programme Implementation (MoSPI): Transforms scheme administration from periodic sample reviews into automated, 100% continuous national fund surveillance.",
            "District Authorities & Implementing District Authorities (IDAs): Instant pre-sanction gatekeeping prevents illegal tender splitting before vouchers are signed or payments disbursed.",
            "Comptroller and Auditor General (CAG) & State AGs: Replaces tedious manual voucher sampling with prioritized, high-probability anomaly dossiers and pre-compiled legal checklists.",
            "Rural Citizens & Constituents: Ensures promised community assets (drinking water borewells, school additions, primary health centres) are physically delivered without ghost diversion."
        ]),
        ("• Benefits of the solution (social, economic, environmental, etc.)", [
            "Economic Benefits: Screens ₹4,000+ Cr annual scheme flow. Caught ₹432.5 Cr in high-risk works and ₹287 Cr in frozen capital. Estimated ₹100–₹200 Crore annual taxpayer savings.",
            "Social & Governance Benefits: Eliminates political patronage cartels; builds citizen trust through transparent, public-facing constituency spending scorecards.",
            "Operational & Time Efficiency: Reduces audit lead-time from 12–24 months to under 15 milliseconds, while eliminating 95% of manual file-checking drudgery for district collectors.",
            "Environmental & Infrastructure Integrity: Fast-tracks pending rural solar electrification, wastewater drainage, and flood protection works delayed by administrative dormancy."
        ])
    ]

    curr_top5 = Inches(1.6)
    for title, bullets in impact_sections:
        tb = s5.shapes.add_textbox(Inches(0.6), curr_top5, Inches(12.0), Inches(2.4))
        tf = tb.text_frame; tf.word_wrap = True
        pt = tf.paragraphs[0]; pt.text = title; pt.font.size = Pt(15); pt.font.bold = True; pt.font.color.rgb = C_BLACK; pt.font.name = "Times New Roman"
        for b in bullets:
            pb = tf.add_paragraph(); pb.text = f"  - {b}"; pb.font.size = Pt(11); pb.font.color.rgb = C_DARK_TEXT; pb.space_before = Pt(5)
        curr_top5 += Inches(2.55)

    # =========================================================
    # SLIDE 6: RESEARCH AND REFERENCES (Screenshot thumbnail 6)
    # =========================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_white_bg(s6)
    add_top_elements(s6, "RESEARCH AND REFERENCES")
    add_bottom_banner(s6, 6)

    h6_box = s6.shapes.add_textbox(Inches(0.6), Inches(1.5), Inches(12.0), Inches(0.5))
    tf_h6 = h6_box.text_frame
    pt6 = tf_h6.paragraphs[0]
    pt6.text = "• Details / Links of the references and research work"
    pt6.font.size = Pt(16); pt6.font.bold = True; pt6.font.color.rgb = C_BLACK; pt6.font.name = "Times New Roman"

    refs = [
        ("1. Ministry of Statistics and Programme Implementation (MoSPI), Government of India", "Guidelines on Member of Parliament Local Area Development Scheme (MPLADS) — Statutory provisions on Para 3.12 (Tender procedures), Para 5.2 (45-Day Sanction SLA), and Para 2.11 (Permissible works). URL: mplads.gov.in"),
        ("2. Office of the Comptroller and Auditor General of India (CAG)", "Performance Audit Report on Member of Parliament Local Area Development Scheme — Reports detailing chronic fund dormancy, contract splitting, March Rush fiscal dumps, and unspent constituency balances. URL: cag.gov.in"),
        ("3. Ministry of Finance, Department of Expenditure, Government of India", "General Financial Rules (GFR 2017) — Rule 149 governing mandatory procurement of goods & services through Government e-Marketplace (GeM) and statutory e-tendering thresholds (₹5 Lakh / ₹10 Lakh)."),
        ("4. Liu, F. T., Ting, K. M., & Zhou, Z. H. (IEEE ICDM)", "'Isolation Forest' — Foundations of unsupervised isolation tree algorithms for multi-dimensional anomaly detection without normality assumptions. IEEE International Conference on Data Mining."),
        ("5. Breunig, M. M., Kriegel, H. P., Ng, R. T., & Sander, J. (ACM SIGMOD)", "'LOF: Identifying Density-Based Local Outliers' — Formulations of Local Outlier Factor and local reachability density metrics in spatial data structures."),
        ("6. Open Government Data (OGD) Platform India (data.gov.in)", "Authenticated datasets on MPLADS physical progress, financial release vs expenditure, and constituency-wise project archives (2019–2024)." )
    ]

    curr_top6 = Inches(2.2)
    for title, desc in refs:
        card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), curr_top6, Inches(12.0), Inches(0.68))
        card.fill.solid(); card.fill.fore_color.rgb = C_BOX_BG
        card.line.color.rgb = C_BOX_BORDER
        card.line.width = Pt(1)

        tb = s6.shapes.add_textbox(Inches(0.75), curr_top6 + Inches(0.04), Inches(11.7), Inches(0.6))
        tf = tb.text_frame; tf.word_wrap = True
        pt = tf.paragraphs[0]; pt.text = title; pt.font.size = Pt(11); pt.font.bold = True; pt.font.color.rgb = C_NAVY_TITLE; pt.font.name = "Times New Roman"
        pd = tf.add_paragraph(); pd.text = desc; pd.font.size = Pt(9.5); pd.font.color.rgb = C_DARK_TEXT; pd.space_before = Pt(1)
        curr_top6 += Inches(0.74)

    # =========================================================
    # SLIDE 7: WORKING PROTOTYPE & TEAM DETAILS
    # =========================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_white_bg(s7)
    add_top_elements(s7, "WORKING PROTOTYPE & TEAM")
    add_bottom_banner(s7, 7)

    # Left Column: Working Prototype Demonstration Highlights
    add_card(s7, Inches(0.6), Inches(1.5), Inches(5.8), Inches(5.0), bg_color=C_BOX_BG)
    p_box = s7.shapes.add_textbox(Inches(0.8), Inches(1.65), Inches(5.4), Inches(4.7))
    tf_p = p_box.text_frame; tf_p.word_wrap = True
    pt_h = tf_p.paragraphs[0]; pt_h.text = "🖥️ Live Functional Prototype Modules"; pt_h.font.size = Pt(14); pt_h.font.bold = True; pt_h.font.color.rgb = C_NAVY_TITLE; pt_h.font.name = "Times New Roman"

    proto_bullets = [
        ("Geospatial GIS Anomaly Heatmap", "Interactive Leaflet India map rendering risk intensity across all 33 States/UTs with constituency-level audit drill-downs."),
        ("Works Anomaly Explorer (105k)", "Full-text searchable, paginated table with real-time ML vs CAG score comparisons and multi-year temporal filtering (2019-2024)."),
        ("Live AI Audit Simulator", "Interactive 'What-If' sandbox allowing evaluators to adjust project budget, delay, and village duplication to test ML risk recalculation live."),
        ("Officer Case Management Queue", "Field-ready case tracking (UNDER REVIEW, SITE INSPECTION, FALSE POSITIVE) logging auditor observations."),
        ("Official Printable CAG Dossiers", "One-click printable audit screening reports with formal case IDs, checklists, and sign/stamp fields.")
    ]
    for h, b in proto_bullets:
        ph = tf_p.add_paragraph(); ph.text = f"• {h}: "; ph.font.size = Pt(11); ph.font.bold = True; ph.font.color.rgb = C_BLUE_BANNER; ph.space_before = Pt(6)
        pb = tf_p.add_paragraph(); pb.text = b; pb.font.size = Pt(10); pb.font.color.rgb = C_DARK_TEXT

    # Right Column: Team Composition & Roles Grid
    add_card(s7, Inches(6.8), Inches(1.5), Inches(5.8), Inches(5.0), bg_color=C_BOX_BG)
    t_box = s7.shapes.add_textbox(Inches(7.0), Inches(1.65), Inches(5.4), Inches(4.7))
    tf_t = t_box.text_frame; tf_t.word_wrap = True
    pt_th = tf_t.paragraphs[0]; pt_th.text = "👥 Team Members & Project Responsibilities"; pt_th.font.size = Pt(14); pt_th.font.bold = True; pt_th.font.color.rgb = C_NAVY_TITLE; pt_th.font.name = "Times New Roman"

    team_members = [
        ("Team Leader", "[Leader Name]", "Lead AI/ML Architect & Backend Engine (FastAPI)"),
        ("Member 2", "[Member Name]", "Data Pipeline, Cleaning & MoSPI Scraper (Python)"),
        ("Member 3", "[Member Name]", "Frontend Architecture, React 18 & Recharts Visualizer"),
        ("Member 4", "[Member Name]", "Geospatial GIS Mapping Specialist (Leaflet API)"),
        ("Member 5", "[Member Name]", "CAG Statutory Rules & GFR Domain Compliance"),
        ("Member 6 / Mentor", "[Mentor / Name]", "Quality Assurance, Audit Testing & Evaluation")
    ]
    for role, name, desc in team_members:
        pr = tf_t.add_paragraph(); pr.text = f"• {role}: {name}"; pr.font.size = Pt(11); pr.font.bold = True; pr.font.color.rgb = C_BLUE_BANNER; pr.space_before = Pt(6)
        pd = tf_t.add_paragraph(); pd.text = f"  Role: {desc}"; pd.font.size = Pt(9.5); pd.font.color.rgb = C_DARK_TEXT

    out_pptx = r"c:\Users\aksha\Desktop\SIH26102\SIH2026_IDEA_Presentation_SIH26102.pptx"
    prs.save(out_pptx)
    print(f"SUCCESS: Exact SIH Template PPTX saved at {out_pptx}")

if __name__ == "__main__":
    build_presentation()
