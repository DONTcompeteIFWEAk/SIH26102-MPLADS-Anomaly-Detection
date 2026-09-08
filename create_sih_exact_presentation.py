import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Exact Official Color Palette
    C_BLUE_BANNER = RGBColor(20, 93, 160)     # #145da0 - Official SIH footer banner
    C_HEADING_BLUE = RGBColor(29, 68, 119)    # #1d4477 - Official dark blue title
    C_NAVY_TITLE = RGBColor(29, 68, 119)      # #1d4477
    C_PURPLE_OVAL = RGBColor(91, 33, 182)     # #5b21b6 - Top-left team badge
    C_ORANGE_BADGE = RGBColor(255, 160, 83)   # #FFA053 - Winning slide orange header
    C_BLACK = RGBColor(0, 0, 0)
    C_WHITE = RGBColor(255, 255, 255)
    C_DARK_TEXT = RGBColor(30, 41, 59)        # #1e293b
    C_MUTED = RGBColor(71, 85, 105)           # #475569
    C_BOX_BG = RGBColor(248, 250, 252)        # #f8fafc
    C_BOX_BORDER = RGBColor(203, 213, 225)    # #cbd5e1

    logo_path = r"c:\Users\aksha\Desktop\SIH26102\sih_logo_transparent.png"
    bulb_center_path = r"c:\Users\aksha\Desktop\SIH26102\sih_bulb_center.png"

    def set_white_bg(slide):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = C_WHITE

    def add_bottom_banner(slide, slide_num):
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.05), Inches(13.333), Inches(0.45))
        banner.fill.solid()
        banner.fill.fore_color.rgb = C_BLUE_BANNER
        banner.line.color.rgb = C_BLUE_BANNER
        tf = banner.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"Team ID: T106  |  Team Name: RunTime Terror{' ' * 95}{slide_num}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.font.name = "Arial"
        p.alignment = PP_ALIGN.LEFT

    def add_top_elements(slide, title_text, subtitle_text=None):
        # Top-Left Oval: Team Name
        oval = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.6), Inches(0.2), Inches(1.4), Inches(1.05))
        oval.fill.solid()
        oval.fill.fore_color.rgb = C_WHITE
        oval.line.color.rgb = C_PURPLE_OVAL
        oval.line.width = Pt(2.5)
        tf_o = oval.text_frame
        tf_o.word_wrap = True
        p_o = tf_o.paragraphs[0]
        p_o.text = "Team\nRunTime\nTerror"
        p_o.font.size = Pt(9.5)
        p_o.font.bold = True
        p_o.font.color.rgb = C_DARK_TEXT
        p_o.font.name = "Times New Roman"
        p_o.alignment = PP_ALIGN.CENTER

        # Top-Center: Slide Title
        t_box = slide.shapes.add_textbox(Inches(2.2), Inches(0.25), Inches(8.8), Inches(0.9))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = C_BLACK
        p_t.font.name = "Times New Roman"
        p_t.alignment = PP_ALIGN.CENTER

        if subtitle_text:
            p_sub = tf_t.add_paragraph()
            p_sub.text = subtitle_text
            p_sub.font.size = Pt(10)
            p_sub.font.color.rgb = C_MUTED
            p_sub.font.name = "Arial"
            p_sub.alignment = PP_ALIGN.CENTER

        # Top-Right: SIH Logo
        if os.path.exists(logo_path):
            slide.shapes.add_picture(logo_path, Inches(10.8), Inches(0.18), width=Inches(2.1))

    def add_orange_badge(slide, left, top, width, height, text):
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        badge.fill.solid()
        badge.fill.fore_color.rgb = C_ORANGE_BADGE
        badge.line.color.rgb = C_BLACK
        badge.line.width = Pt(1.5)
        tf = badge.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_BLACK
        p.font.name = "Arial"
        p.alignment = PP_ALIGN.CENTER
        return badge

    def add_card(slide, left, top, width, height, bg_color=C_BOX_BG, border_color=C_BOX_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        return card

    # =========================================================
    # SLIDE 1: TITLE PAGE (Exact Match to Official SIH Format)
    # =========================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_white_bg(s1)

    if os.path.exists(logo_path):
        s1.shapes.add_picture(logo_path, Inches(10.8), Inches(0.18), width=Inches(2.1))

    # Top Center: SMART INDIA HACKATHON 2026
    sih_title_box = s1.shapes.add_textbox(Inches(1.5), Inches(0.3), Inches(9.2), Inches(0.75))
    tf_sih = sih_title_box.text_frame
    p_sih = tf_sih.paragraphs[0]
    p_sih.text = "SMART INDIA HACKATHON 2026"
    p_sih.font.size = Pt(28)
    p_sih.font.bold = True
    p_sih.font.color.rgb = C_NAVY_TITLE
    p_sih.font.name = "Times New Roman"
    p_sih.alignment = PP_ALIGN.CENTER

    tp_box = s1.shapes.add_textbox(Inches(2.5), Inches(1.05), Inches(7.2), Inches(0.6))
    tf_tp = tp_box.text_frame
    p_tp = tf_tp.paragraphs[0]
    p_tp.text = "TITLE PAGE"
    p_tp.font.size = Pt(22)
    p_tp.font.bold = True
    p_tp.font.color.rgb = C_BLACK
    p_tp.font.name = "Times New Roman"
    p_tp.alignment = PP_ALIGN.CENTER

    if os.path.exists(bulb_center_path):
        s1.shapes.add_picture(bulb_center_path, Inches(8.6), Inches(1.8), height=Inches(4.9))

    l_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(7.0), Inches(5.1))
    tf_l = l_box.text_frame
    tf_l.word_wrap = True

    fields = [
        ("• Problem Statement ID –", " SIH26102"),
        ("• Problem Statement Title-", " Autonomous Public Fund Anomaly Detection & Temporal Forensics System for MPLADS"),
        ("• Theme-", " Smart Governance & Public Financial Systems"),
        ("• PS Category- Software/Hardware", " Software"),
        ("• Team ID-", " T106"),
        ("• Team Name (Registered on portal)-", " RunTime Terror"),
        ("• Team Leader-", " Akshat Mittal"),
        ("• Team Members-", " Khushi, Aryan Shahi, Abhay Pratap, Gaurav Shukla, Shreya Srivastava")
    ]

    for i, (label, val) in enumerate(fields):
        p = tf_l.paragraphs[0] if i == 0 else tf_l.add_paragraph()
        r1 = p.add_run(); r1.text = label; r1.font.bold = True; r1.font.size = Pt(14.5); r1.font.color.rgb = C_BLACK; r1.font.name = "Times New Roman"
        r2 = p.add_run(); r2.text = val; r2.font.bold = False; r2.font.size = Pt(13.5); r2.font.color.rgb = RGBColor(30, 41, 59); r2.font.name = "Times New Roman"
        p.space_before = Pt(7)

    add_bottom_banner(s1, 1)

    # =========================================================
    # SLIDE 2: PROBLEM STATEMENT, WHY DIFFERENT & IDEA/APPROACH
    # (Embedded Winning Slide matching WhatsApp Reference)
    # =========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_white_bg(s2)
    add_top_elements(s2, "IDEA TITLE / PROPOSED SOLUTION")
    add_bottom_banner(s2, 2)

    # Left Column: Problem Statement & Why Different
    add_orange_badge(s2, Inches(0.6), Inches(1.35), Inches(5.8), Inches(0.4), "Problem Statement")
    add_card(s2, Inches(0.6), Inches(1.85), Inches(5.8), Inches(2.2))
    tb_prob = s2.shapes.add_textbox(Inches(0.7), Inches(1.9), Inches(5.6), Inches(2.1))
    tf_p = tb_prob.text_frame; tf_p.word_wrap = True
    prob_pts = [
        "Massive Volume Blindspot: 105,000+ MPLADS works nationwide make exhaustive manual scrutiny mathematically impossible.",
        "Lagged Sample Autopsies: Sample-based reviews occur 12–24 months after fund disbursement when funds are already gone.",
        "Data Siloing: Financial vouchers, execution milestone timelines, and contractor details live in disconnected databases.",
        "Contextual Nuance: High expenditure alone is not misconduct; true anomaly detection requires multi-dimensional baseline benchmarking."
    ]
    for i, pt in enumerate(prob_pts):
        p = tf_p.paragraphs[0] if i == 0 else tf_p.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(9.5); p.font.color.rgb = C_DARK_TEXT; p.font.name = "Arial"; p.space_before = Pt(4)

    add_orange_badge(s2, Inches(0.6), Inches(4.15), Inches(5.8), Inches(0.4), "Why is it different?")
    add_card(s2, Inches(0.6), Inches(4.65), Inches(5.8), Inches(2.25))
    tb_diff = s2.shapes.add_textbox(Inches(0.7), Inches(4.7), Inches(5.6), Inches(2.15))
    tf_d = tb_diff.text_frame; tf_d.word_wrap = True
    diff_pts = [
        ("🚨 March Rush Radar: ", "World's first temporal forensics engine catching fiscal-dump sanction surges before March 31.", RGBColor(234, 88, 12)),
        ("⏳ Chronic Dormancy Engine: ", "Pinpoints long-stalled projects (>3 years, ₹287 Cr) for immediate statutory clawback and reallocation.", RGBColor(147, 51, 234)),
        ("📍 Duplicate / Cluster Signals: ", "Geospatial NLP groups repeated works in identical villages to stop duplicate contractor billing.", RGBColor(2, 132, 199)),
        ("🗣️ Bilingual + Explainable: ", "Translates complex AI math into plain legal English and सरल हिंदी directives with one-click CAG dossiers.", RGBColor(5, 150, 105))
    ]
    for i, (hd, bd, col) in enumerate(diff_pts):
        p = tf_d.paragraphs[0] if i == 0 else tf_d.add_paragraph()
        r1 = p.add_run(); r1.text = f"• {hd}"; r1.font.bold = True; r1.font.size = Pt(9.5); r1.font.color.rgb = col; r1.font.name = "Arial"
        r2 = p.add_run(); r2.text = bd; r2.font.bold = False; r2.font.size = Pt(9.5); r2.font.color.rgb = C_DARK_TEXT; r2.font.name = "Arial"
        p.space_before = Pt(4)

    # Right Column: Idea/Approach (5 steps) & Architecture Hub
    add_orange_badge(s2, Inches(6.8), Inches(1.35), Inches(5.9), Inches(0.4), "Idea/Approach")
    add_card(s2, Inches(6.8), Inches(1.85), Inches(5.9), Inches(2.4))
    tb_app = s2.shapes.add_textbox(Inches(6.9), Inches(1.9), Inches(5.7), Inches(2.3))
    tf_app = tb_app.text_frame; tf_app.word_wrap = True
    app_steps = [
        ("1 INGEST", "MoSPI e-SAKSHI & Public Records: Ingests 105,000 national works across all 33 States/UTs.", RGBColor(37, 99, 235)),
        ("2 CLEAN", "Feature Engineering: Computes cost-per-unit medians, GFR 149 proximity, and delay days.", RGBColor(8, 145, 178)),
        ("3 DETECT", "Dual Hybrid Intelligence: Isolation Forest (45%), LOF (35%), PCA (20%) + 5 codified CAG rules.", RGBColor(124, 58, 237)),
        ("4 PRIORITIZE", "Explainable Risk Stratification: Calibrated 0-100 scores with concrete violation causes.", RGBColor(234, 88, 12)),
        ("5 VERIFY", "Officer Workflow & CAG Dossier: Printable, court-admissible audit reports for vigilance officers.", RGBColor(22, 163, 74))
    ]
    for i, (step, desc, col) in enumerate(app_steps):
        p = tf_app.paragraphs[0] if i == 0 else tf_app.add_paragraph()
        r1 = p.add_run(); r1.text = f"[{step}] "; r1.font.bold = True; r1.font.size = Pt(9); r1.font.color.rgb = col; r1.font.name = "Arial"
        r2 = p.add_run(); r2.text = desc; r2.font.bold = False; r2.font.size = Pt(9); r2.font.color.rgb = C_DARK_TEXT; r2.font.name = "Arial"
        p.space_before = Pt(3)

    # Architecture Hub graphic
    arch_hub_path = r"c:\Users\aksha\Desktop\SIH26102\arch_hub.png"
    if os.path.exists(arch_hub_path):
        s2.shapes.add_picture(arch_hub_path, Inches(6.8), Inches(4.35), width=Inches(5.9), height=Inches(2.55))

    # =========================================================
    # SLIDE 3: DATA FLOW, PROTOTYPE & TECHNOLOGY STACK
    # (Embedded Winning Slide matching WhatsApp Reference)
    # =========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_white_bg(s3)
    add_top_elements(s3, "TECHNICAL APPROACH")
    add_bottom_banner(s3, 3)

    # Left Column: Data Flow (2 flowcharts)
    add_orange_badge(s3, Inches(0.6), Inches(1.35), Inches(5.8), Inches(0.4), "Data Flow")
    df_path = r"c:\Users\aksha\Desktop\SIH26102\dataflow_pipeline.png"
    if os.path.exists(df_path):
        s3.shapes.add_picture(df_path, Inches(0.6), Inches(1.85), width=Inches(5.8), height=Inches(2.5))

    ml_flow_path = r"c:\Users\aksha\Desktop\SIH26102\ml_ensemble_flow.png"
    if os.path.exists(ml_flow_path):
        s3.shapes.add_picture(ml_flow_path, Inches(0.6), Inches(4.45), width=Inches(5.8), height=Inches(2.45))

    # Right Column: Prototype (4 real screens) & Tech Stack Hub
    add_orange_badge(s3, Inches(6.8), Inches(1.35), Inches(5.9), Inches(0.4), "Prototype")
    proto_grid_path = r"c:\Users\aksha\Desktop\SIH26102\proto_grid_4screens.png"
    if os.path.exists(proto_grid_path):
        s3.shapes.add_picture(proto_grid_path, Inches(6.8), Inches(1.85), width=Inches(5.9), height=Inches(2.45))

    add_orange_badge(s3, Inches(6.8), Inches(4.38), Inches(5.9), Inches(0.38), "Technology Stack")
    tech_hub_path = r"c:\Users\aksha\Desktop\SIH26102\tech_stack_hub.png"
    if os.path.exists(tech_hub_path):
        s3.shapes.add_picture(tech_hub_path, Inches(6.8), Inches(4.8), width=Inches(5.9), height=Inches(2.15))

    # =========================================================
    # SLIDE 4: FEASIBILITY AND VIABILITY (Official SIH Template)
    # =========================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_white_bg(s4)
    add_top_elements(s4, "FEASIBILITY AND VIABILITY")
    add_bottom_banner(s4, 4)

    sections_s4 = [
        ("• Analysis of the feasibility of the idea", [
            ("Data Feasibility: ", "100% validated on authentic MoSPI datasets (expanded to 105,000 multi-year records spanning 2019-2024 across all 33 States/UTs)."),
            ("Technical Scalability: ", "Sub-second inference (<15ms per work), allowing seamless real-time pre-sanction screening as a plug-in inside e-SAKSHI."),
            ("Zero Extra Burden: ", "Requires zero additional manual forms from MPs or district officers; extracts existing mandatory data fields.")
        ]),
        ("• Potential challenges and risks", [
            ("Algorithmic Risk (Zero-Distance KNN Collapse): ", "Public works have thousands of identical repetitive civil works that distort standard KNN distance calculations."),
            ("Operational Risk (Auditor Adoption): ", "District vigilance officers reject black-box AI algorithms because they cannot legally justify scores in parliamentary reviews."),
            ("False Positive Risk: ", "Legitimate mega-projects (e.g. ₹2 Cr trauma center) look like extreme statistical outliers despite being completely genuine.")
        ]),
        ("• Strategies for overcoming these challenges", [
            ("Profile-Deduplicated LOF: ", "Groups identical civil works profiles into canonical representations before KNN, preserving true neighborhood reachability density."),
            ("Bilingual Plain-Language Diagnostics: ", "Translates mathematical metrics into plain English and सरल हिंदी with exact statutory CAG citations (GFR 149, Para 5.2)."),
            ("Dual-Layer Hybrid Logic & Feedback Loop: ", "Statutory rules validate legitimate high-budget works; human officer resolutions dynamically calibrate decision thresholds.")
        ])
    ]

    curr_top4 = Inches(1.4)
    for title, bullets in sections_s4:
        tb = s4.shapes.add_textbox(Inches(0.6), curr_top4, Inches(12.1), Inches(1.75))
        tf = tb.text_frame; tf.word_wrap = True
        pt = tf.paragraphs[0]; pt.text = title; pt.font.size = Pt(15); pt.font.bold = True; pt.font.color.rgb = C_BLACK; pt.font.name = "Times New Roman"
        for label, val in bullets:
            p = tf.add_paragraph()
            r1 = p.add_run(); r1.text = f"  - {label}"; r1.font.bold = True; r1.font.size = Pt(11.5); r1.font.color.rgb = C_NAVY_TITLE; r1.font.name = "Times New Roman"
            r2 = p.add_run(); r2.text = val; r2.font.bold = False; r2.font.size = Pt(11.5); r2.font.color.rgb = C_DARK_TEXT; r2.font.name = "Times New Roman"
            p.space_before = Pt(3)
        curr_top4 += Inches(1.85)

    # =========================================================
    # SLIDE 5: IMPACT AND BENEFITS (Official SIH Template)
    # =========================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_white_bg(s5)
    add_top_elements(s5, "IMPACT AND BENEFITS")
    add_bottom_banner(s5, 5)

    sections_s5 = [
        ("• Potential impact on the target audience", [
            ("MoSPI National Oversight: ", "Transforms national scheme surveillance from periodic sample autopsies into automated, 100% continuous oversight."),
            ("District Authorities & IDAs: ", "Instant pre-sanction gatekeeping prevents illegal tender splitting before vouchers are signed or payments disbursed."),
            ("CAG & State AGs: ", "Replaces tedious manual voucher sampling with prioritized, high-probability anomaly dossiers and pre-compiled legal checklists."),
            ("Rural Citizens & Constituents: ", "Ensures promised community assets (drinking water, schools, primary health) are physically delivered without ghost diversion.")
        ]),
        ("• Benefits of the solution (social, economic, environmental, etc.)", [
            ("Economic Benefits: ", "Screens ₹4,000+ Cr annual scheme flow. Caught ₹432.5 Cr in high-risk works and ₹287 Cr in frozen capital. Estimated ₹100–₹200 Crore annual taxpayer savings."),
            ("Social & Governance: ", "Eliminates political patronage cartels; builds citizen trust through transparent, public-facing constituency spending scorecards."),
            ("Operational Efficiency: ", "Reduces audit lead-time from 12–24 months to under 15 milliseconds, eliminating 95% of manual file-checking drudgery."),
            ("Infrastructure Integrity: ", "Fast-tracks pending rural solar electrification, wastewater drainage, and flood protection works delayed by administrative dormancy.")
        ])
    ]

    curr_top5 = Inches(1.4)
    for title, bullets in sections_s5:
        tb = s5.shapes.add_textbox(Inches(0.6), curr_top5, Inches(12.1), Inches(2.6))
        tf = tb.text_frame; tf.word_wrap = True
        pt = tf.paragraphs[0]; pt.text = title; pt.font.size = Pt(15.5); pt.font.bold = True; pt.font.color.rgb = C_BLACK; pt.font.name = "Times New Roman"
        for label, val in bullets:
            p = tf.add_paragraph()
            r1 = p.add_run(); r1.text = f"  - {label}"; r1.font.bold = True; r1.font.size = Pt(11.5); r1.font.color.rgb = C_NAVY_TITLE; r1.font.name = "Times New Roman"
            r2 = p.add_run(); r2.text = val; r2.font.bold = False; r2.font.size = Pt(11.5); r2.font.color.rgb = C_DARK_TEXT; r2.font.name = "Times New Roman"
            p.space_before = Pt(4)
        curr_top5 += Inches(2.7)

    # =========================================================
    # SLIDE 6: OFFICER / AUDITOR WORKFLOW (Matching user's PPTX)
    # =========================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_white_bg(s6)
    add_top_elements(s6, "OFFICER / AUDITOR WORKFLOW", "How a district vigilance officer or auditor moves from a national signal to a CAG-ready case")
    add_bottom_banner(s6, 6)

    # 7 Step Cards
    step_items = [
        ("1", "LOGIN", "Secure role-based\nauditor access", RGBColor(2, 132, 199), RGBColor(240, 249, 255)),
        ("2", "GIS HEATMAP", "See risk intensity\nacross 33 States", RGBColor(8, 145, 178), RGBColor(236, 254, 255)),
        ("3", "EXPLORER", "Search, filter &\ncompare scores", RGBColor(13, 148, 136), RGBColor(240, 253, 250)),
        ("4", "FLAGGED WORK", "Drill into the\nwork-level evidence", RGBColor(234, 88, 12), RGBColor(255, 247, 237)),
        ("5", "AI SIMULATOR", "Test budget, delay\n& village what-ifs", RGBColor(202, 138, 4), RGBColor(254, 252, 232)),
        ("6", "CASE QUEUE", "Update status +\nrecord observations", RGBColor(147, 51, 234), RGBColor(250, 245, 255)),
        ("7", "CAG DOSSIER", "Generate / print\nformal screening", RGBColor(22, 163, 74), RGBColor(240, 253, 244))
    ]

    for i, (num, stitle, sdesc, col, bg_col) in enumerate(step_items):
        card_l = Inches(0.6 + i * 1.74)
        card_t = Inches(1.5)
        card_w = Inches(1.64)
        card_h = Inches(3.5)

        card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_l, card_t, card_w, card_h)
        card.fill.solid(); card.fill.fore_color.rgb = bg_col
        card.line.color.rgb = col; card.line.width = Pt(1.5)

        circle = s6.shapes.add_shape(MSO_SHAPE.OVAL, card_l + Inches(0.52), card_t + Inches(0.2), Inches(0.6), Inches(0.6))
        circle.fill.solid(); circle.fill.fore_color.rgb = col
        circle.line.color.rgb = col
        tf_c = circle.text_frame
        p_c = tf_c.paragraphs[0]; p_c.text = num; p_c.font.size = Pt(11); p_c.font.bold = True; p_c.font.color.rgb = C_WHITE; p_c.alignment = PP_ALIGN.CENTER

        tb = s6.shapes.add_textbox(card_l + Inches(0.05), card_t + Inches(0.9), card_w - Inches(0.1), Inches(2.4))
        tf = tb.text_frame; tf.word_wrap = True
        pt = tf.paragraphs[0]; pt.text = stitle; pt.font.size = Pt(10); pt.font.bold = True; pt.font.color.rgb = col; pt.alignment = PP_ALIGN.CENTER
        pd = tf.add_paragraph(); pd.text = sdesc; pd.font.size = Pt(8.5); pd.font.color.rgb = C_MUTED; pd.alignment = PP_ALIGN.CENTER; pd.space_before = Pt(6)

    # Live Prototype Callout Box
    cp_box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(5.2), Inches(12.1), Inches(1.6))
    cp_box.fill.solid(); cp_box.fill.fore_color.rgb = C_WHITE
    cp_box.line.color.rgb = C_BLUE_BANNER; cp_box.line.width = Pt(2.0)

    tb_call = s6.shapes.add_textbox(Inches(0.8), Inches(5.35), Inches(2.2), Inches(1.3))
    tf_call = tb_call.text_frame; tf_call.word_wrap = True
    pt_call = tf_call.paragraphs[0]; pt_call.text = "LIVE PROTOTYPE\nCALLOUT"; pt_call.font.size = Pt(11); pt_call.font.bold = True; pt_call.font.color.rgb = C_BLUE_BANNER; pt_call.alignment = PP_ALIGN.CENTER

    modules = [
        ("GIS", "Leaflet India\nanomaly heatmap"),
        ("EXPLORER", "105k searchable\nworks grid"),
        ("SIMULATOR", "Live what-if risk\nrecalculation"),
        ("QUEUE", "UNDER REVIEW /\nSITE INSPECTION"),
        ("DOSSIER", "Printable audit\nscreening report")
    ]
    for i, (mtitle, mdesc) in enumerate(modules):
        ml = Inches(3.2 + i * 1.85)
        mt = Inches(5.35)
        mw = Inches(1.75)
        mh = Inches(1.3)

        mbx = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, ml, mt, mw, mh)
        mbx.fill.solid(); mbx.fill.fore_color.rgb = C_BOX_BG
        mbx.line.color.rgb = C_BOX_BORDER; mbx.line.width = Pt(1.0)

        mtb = s6.shapes.add_textbox(ml + Inches(0.05), mt + Inches(0.08), mw - Inches(0.1), mh - Inches(0.16))
        mtf = mtb.text_frame; mtf.word_wrap = True
        mp1 = mtf.paragraphs[0]; mp1.text = mtitle; mp1.font.size = Pt(9.5); mp1.font.bold = True; mp1.font.color.rgb = C_BLUE_BANNER; mp1.alignment = PP_ALIGN.CENTER
        mp2 = mtf.add_paragraph(); mp2.text = mdesc; mp2.font.size = Pt(8.5); mp2.font.color.rgb = C_DARK_TEXT; mp2.alignment = PP_ALIGN.CENTER; mp2.space_before = Pt(3)

    # =========================================================
    # SLIDE 7: RESEARCH REFERENCES & TEAM
    # =========================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_white_bg(s7)
    add_top_elements(s7, "RESEARCH REFERENCES & TEAM")
    add_bottom_banner(s7, 7)

    # Left Column: Statutory Citations
    add_card(s7, Inches(0.6), Inches(1.4), Inches(5.8), Inches(4.7), bg_color=C_BOX_BG)
    tb_r7 = s7.shapes.add_textbox(Inches(0.75), Inches(1.5), Inches(5.5), Inches(4.5))
    tf_r7 = tb_r7.text_frame; tf_r7.word_wrap = True
    pt_r7 = tf_r7.paragraphs[0]; pt_r7.text = "• Statutory Governance & Academic Citations"; pt_r7.font.size = Pt(13); pt_r7.font.bold = True; pt_r7.font.color.rgb = C_NAVY_TITLE; pt_r7.font.name = "Times New Roman"

    refs_data = [
        ("1. MoSPI, Government of India (Guidelines on MPLADS)", "Para 3.12 (Tendering procedures), Para 5.2 (45-Day Sanction SLA), and Para 2.11 (Permissible public community assets)."),
        ("2. Office of the Comptroller & Auditor General of India (CAG)", "Performance Audit Reports on MPLADS: Fund dormancy, tender splitting, and March Rush fiscal dump analyses."),
        ("3. Ministry of Finance, Department of Expenditure (GFR 2017)", "Rule 149: Mandatory GeM public procurement thresholds (<₹5 Lakh / ₹10 Lakh) preventing artificial work fragmentation."),
        ("4. Liu, F. T., Ting, K. M., & Zhou, Z. H. (IEEE ICDM)", "'Isolation Forest' — Foundations of unsupervised isolation tree algorithms for multi-dimensional anomaly detection.")
    ]
    for rh, rd in refs_data:
        p1 = tf_r7.add_paragraph(); p1.text = rh; p1.font.size = Pt(10.5); p1.font.bold = True; p1.font.color.rgb = C_BLUE_BANNER; p1.font.name = "Times New Roman"; p1.space_before = Pt(6)
        p2 = tf_r7.add_paragraph(); p2.text = rd; p2.font.size = Pt(9.5); p2.font.color.rgb = C_DARK_TEXT; p2.font.name = "Times New Roman"

    # Right Column: Team Roster
    add_card(s7, Inches(6.8), Inches(1.4), Inches(5.9), Inches(4.7), bg_color=C_BOX_BG)
    tb_tm = s7.shapes.add_textbox(Inches(6.95), Inches(1.5), Inches(5.6), Inches(4.5))
    tf_tm = tb_tm.text_frame; tf_tm.word_wrap = True
    pt_tm = tf_tm.paragraphs[0]; pt_tm.text = "• Team RunTime Terror (T106) Roster"; pt_tm.font.size = Pt(13); pt_tm.font.bold = True; pt_tm.font.color.rgb = C_NAVY_TITLE; pt_tm.font.name = "Times New Roman"

    roster = [
        ("Team Leader: Akshat Mittal", "Lead AI/ML Architect & Backend Engine (FastAPI, Scikit-Learn)"),
        ("Member 2: Khushi", "Data Pipeline, MoSPI Scraper & Schema Cleaning (Python)"),
        ("Member 3: Aryan Shahi", "Frontend Architecture, React 18 & Recharts Data Visualizer"),
        ("Member 4: Abhay Pratap", "Geospatial GIS Specialist (Leaflet API & Heatmap Engine)"),
        ("Member 5: Gaurav Shukla", "CAG Statutory Rules & GFR Domain Compliance Engineering"),
        ("Member 6: Shreya Srivastava", "Quality Assurance, Audit Testing & Evaluation Lead")
    ]
    for rname, rrole in roster:
        p1 = tf_tm.add_paragraph(); p1.text = f"• {rname}"; p1.font.size = Pt(10.5); p1.font.bold = True; p1.font.color.rgb = C_BLUE_BANNER; p1.font.name = "Times New Roman"; p1.space_before = Pt(5)
        p2 = tf_tm.add_paragraph(); p2.text = f"  {rrole}"; p2.font.size = Pt(9.5); p2.font.color.rgb = C_DARK_TEXT; p2.font.name = "Times New Roman"

    # 100% Functional Prototype Banner
    pbanner = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(6.25), Inches(12.1), Inches(0.42))
    pbanner.fill.solid(); pbanner.fill.fore_color.rgb = RGBColor(236, 253, 245)
    pbanner.line.color.rgb = RGBColor(16, 185, 129); pbanner.line.width = Pt(1.5)
    tf_pb = pbanner.text_frame
    p_pb = tf_pb.paragraphs[0]
    p_pb.text = "🎯 100% FUNCTIONAL PROTOTYPE • VALIDATED ON 105,000 REAL MOSPI WORKS ACROSS ALL 33 STATES & UTs"
    p_pb.font.size = Pt(10); p_pb.font.bold = True; p_pb.font.color.rgb = RGBColor(4, 120, 87); p_pb.alignment = PP_ALIGN.CENTER

    out_pptx_t106 = r"c:\Users\aksha\Desktop\SIH26102\SIH2026_IDEA_Presentation_SIH26102_T106.pptx"
    prs.save(out_pptx_t106)
    print(f"SUCCESS: Saved updated PPTX to {out_pptx_t106}")

    out_pptx = r"c:\Users\aksha\Desktop\SIH26102\SIH2026_IDEA_Presentation_SIH26102.pptx"
    try:
        prs.save(out_pptx)
        print(f"SUCCESS: Also updated {out_pptx}")
    except Exception as e:
        print(f"Note: {out_pptx} is currently open in PowerPoint ({e}), saved to {out_pptx_t106}")

    out_pptx_win = r"c:\Users\aksha\Desktop\SIH26102\SIH26102_Winning_Presentation.pptx"
    try:
        prs.save(out_pptx_win)
        print(f"SUCCESS: Also updated {out_pptx_win}")
    except Exception as e:
        print(f"Note: {out_pptx_win} ({e})")


if __name__ == "__main__":
    build_presentation()
