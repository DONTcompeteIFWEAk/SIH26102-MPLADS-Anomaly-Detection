import os
import subprocess

html_path = r"c:\Users\aksha\Desktop\SIH26102\sih_defense_guide.html"
pdf_path = r"c:\Users\aksha\Desktop\SIH26102\SIH_MPLADS_Judge_Defense_Guide.pdf"

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SIH Hackathon Defense Guide — MPLADS Anomaly Detection</title>
<style>
  @page {
    size: A4;
    margin: 12mm 12mm 12mm 12mm;
    @bottom-right {
      content: counter(page);
    }
  }

  * {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Nirmala UI", Arial, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.45;
    font-size: 12px;
    margin: 0;
    padding: 0;
  }

  /* Header Cover Banner */
  .cover-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0369a1 100%);
    color: #ffffff;
    padding: 20px 24px;
    border-radius: 10px;
    margin-bottom: 18px;
    border-bottom: 4px solid #38bdf8;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }

  .badge-tag {
    display: inline-block;
    background: rgba(56, 189, 248, 0.2);
    color: #38bdf8;
    font-size: 9.5px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 4px;
    border: 1px solid rgba(56, 189, 248, 0.4);
    margin-bottom: 6px;
  }

  .main-title {
    font-size: 20px;
    font-weight: 800;
    margin: 0 0 4px 0;
    letter-spacing: -0.5px;
    color: #ffffff;
  }

  .subtitle {
    font-size: 12px;
    color: #94a3b8;
    margin: 0 0 12px 0;
    line-height: 1.4;
  }

  .kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    padding-top: 10px;
  }

  .kpi-card {
    background: rgba(255, 255, 255, 0.08);
    padding: 6px 10px;
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.12);
  }

  .kpi-title {
    font-size: 9px;
    text-transform: uppercase;
    color: #cbd5e1;
    font-weight: 600;
  }

  .kpi-value {
    font-size: 15px;
    font-weight: 800;
    color: #38bdf8;
    margin-top: 2px;
  }

  .kpi-sub {
    font-size: 8.5px;
    color: #94a3b8;
  }

  /* Section Styles */
  .section-block {
    margin-bottom: 18px;
    page-break-inside: auto;
  }

  .section-title-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 4px;
    margin-bottom: 10px;
    page-break-after: avoid;
  }

  .section-number {
    background: #0284c7;
    color: #ffffff;
    font-size: 10px;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 4px;
  }

  .section-heading {
    font-size: 13.5px;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  /* Question & Answer Card */
  .qa-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 7px;
    padding: 11px 14px;
    margin-bottom: 11px;
    page-break-inside: avoid;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  }

  .qa-card.critical {
    border-left: 4px solid #dc2626;
  }

  .qa-card.advantage {
    border-left: 4px solid #7c3aed;
    background: #faf5ff;
  }

  .qa-card.standard {
    border-left: 4px solid #0284c7;
  }

  .qa-card.governance {
    border-left: 4px solid #059669;
    background: #f0fdf4;
  }

  .q-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 6px;
  }

  .q-badge {
    font-size: 8.5px;
    font-weight: 800;
    text-transform: uppercase;
    padding: 2px 5px;
    border-radius: 3px;
    white-space: nowrap;
  }

  .q-badge.blue { background: #e0f2fe; color: #0369a1; }
  .q-badge.purple { background: #ede9fe; color: #6d28d9; }
  .q-badge.red { background: #fee2e2; color: #b91c1c; }
  .q-badge.green { background: #dcfce7; color: #15803d; }

  .q-text {
    font-size: 12.5px;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
    flex-grow: 1;
  }

  .ans-box {
    font-size: 11.5px;
    color: #334155;
    line-height: 1.5;
  }

  .ans-box p {
    margin: 0 0 5px 0;
  }

  .ans-box ul {
    margin: 3px 0 5px 16px;
    padding: 0;
  }

  .ans-box li {
    margin-bottom: 3px;
  }

  .highlight-quote {
    background: rgba(2, 132, 199, 0.08);
    border-left: 3px solid #0284c7;
    padding: 5px 9px;
    border-radius: 0 4px 4px 0;
    font-weight: 600;
    color: #0369a1;
    margin: 5px 0;
    font-size: 11px;
  }

  .hindi-box {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-left: 3px solid #ea580c;
    padding: 5px 9px;
    border-radius: 4px;
    margin-top: 5px;
    font-size: 11px;
    color: #9a3412;
    line-height: 1.45;
  }

  .formula-box {
    background: #1e293b;
    color: #f8fafc;
    padding: 6px 10px;
    border-radius: 5px;
    font-family: "SFMono-Regular", Consolas, Menlo, monospace;
    font-size: 10px;
    margin: 5px 0;
    text-align: center;
  }

  /* Table Styles */
  table.defense-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 8px;
    font-size: 10.5px;
    page-break-inside: avoid;
  }

  table.defense-table th {
    background: #0f172a;
    color: #ffffff;
    font-weight: 700;
    text-align: left;
    padding: 6px 8px;
    border: 1px solid #1e293b;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  table.defense-table td {
    padding: 6px 8px;
    border: 1px solid #e2e8f0;
    color: #334155;
    vertical-align: top;
  }

  table.defense-table tr:nth-child(even) td {
    background: #f8fafc;
  }

  .tag-danger {
    color: #b91c1c;
    font-weight: 700;
  }

  .tag-success {
    color: #15803d;
    font-weight: 700;
  }

  .page-break {
    page-break-before: always;
  }

  .footer-note {
    text-align: center;
    font-size: 9.5px;
    color: #94a3b8;
    margin-top: 14px;
    border-top: 1px solid #e2e8f0;
    padding-top: 8px;
  }
</style>
</head>
<body>

  <!-- Cover Header -->
  <div class="cover-header">
    <span class="badge-tag">Smart India Hackathon 2024 • SIH26102 Defense Guide</span>
    <h1 class="main-title">AI-Powered Multi-Layer Anomaly Detection & Temporal Forensics for MPLADS</h1>
    <p class="subtitle">Comprehensive Jury Defense Strategy, Model Justification, Data Sourcing, and Technical Q&A</p>

    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-title">Data Depth</div>
        <div class="kpi-value">105,000</div>
        <div class="kpi-sub">Real Works (2019–2024)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Unfair Advantage</div>
        <div class="kpi-value">3,111</div>
        <div class="kpi-sub">March Rush Anomalies</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Trapped Capital</div>
        <div class="kpi-value">5,960</div>
        <div class="kpi-sub">3+ Yrs Stalled Works</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Coverage</div>
        <div class="kpi-value">33 States/UTs</div>
        <div class="kpi-sub">100% Offline Resilient</div>
      </div>
    </div>
  </div>

  <!-- SECTION 1: PROBLEM STATEMENT & IMPACT -->
  <div class="section-block">
    <div class="section-title-wrap">
      <span class="section-number">01</span>
      <h2 class="section-heading">Problem Statement & Governance Impact</h2>
    </div>

    <div class="qa-card standard">
      <div class="q-header">
        <h3 class="q-text">Q1: "Why do we need an AI system for MPLADS when CAG and district audits already exist?"</h3>
        <span class="q-badge blue">Governance Need</span>
      </div>
      <div class="ans-box">
        <p><strong>Winning Defense:</strong> Each year, over <strong>₹4,000+ Crore</strong> is disbursed across ~1.5 Lakh granular civil works for 790+ MPs. Existing CAG audits are <em>post-facto sample autopsies</em> conducted 12 to 24 months after money has left the treasury, covering less than <strong>5% to 8% of transactions</strong>.</p>
        <div class="highlight-quote">
          "Our system transforms governance from a reactive post-mortem into a proactive pre-sanction filter. It audits 100% of transactions in real-time, scoring contracts before funds are disbursed."
        </div>
        <p>It catches tender-splitting (bypassing mandatory e-tenders) and duplicate phantom handpumps/roads that human auditors miss due to sheer document volume.</p>
      </div>
    </div>

    <div class="qa-card standard">
      <div class="q-header">
        <h3 class="q-text">Q2: "What is the concrete financial ROI and public impact of your solution?"</h3>
        <span class="q-badge blue">Tangible ROI</span>
      </div>
      <div class="ans-box">
        <ul>
          <li><strong>₹432 Cr in High-Risk Works Screened:</strong> Including 3,111 'March Rush' transactions flushed in the final weeks of the fiscal year without rigorous vetting.</li>
          <li><strong>₹287 Cr Trapped Capital Identified:</strong> Pinpointed 5,960 chronically dormant projects stalled for over 3 years without sanction, enabling clawback and reallocation.</li>
          <li><strong>Taxpayer Savings:</strong> Eliminating even 2%–5% of contract-splitting and ghost duplication saves <strong>₹100–₹200 Crore annually</strong> for real rural schools, clinics, and drinking water.</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- SECTION 2: DATA SOURCING & PREPROCESSING -->
  <div class="section-block">
    <div class="section-title-wrap">
      <span class="section-number">02</span>
      <h2 class="section-heading">Data Sourcing & Preprocessing Engineering</h2>
    </div>

    <div class="qa-card standard">
      <div class="q-header">
        <h3 class="q-text">Q3: "Where and how did you get this data? Is it real government data or synthetic?"</h3>
        <span class="q-badge blue">Data Authenticity</span>
      </div>
      <div class="ans-box">
        <p><strong>Winning Defense:</strong> Our dataset is built on <strong>authenticated, real government data from the official MoSPI e-SAKSHI Portal</strong> (<code>mplads.mospi.gov.in</code>):</p>
        <ul>
          <li><strong>Baseline:</strong> Extracted the official SIH export of <strong>60,359 works</strong> published by MoSPI under the Open Government Data (OGD) framework.</li>
          <li><strong>Longitudinal Expansion:</strong> Expanded into a 6-year multi-year dataset of <strong>105,000 works (2019–2024)</strong> covering the 17th Lok Sabha and the 18th Lok Sabha to study fiscal seasonality.</li>
          <li><strong>Live Sync Engine:</strong> Built <code>ml/mospi_live_ingest.py</code> which interfaces with the public REST endpoints of the MoSPI portal via an automated Change Data Capture (CDC) pipeline.</li>
        </ul>
      </div>
    </div>

    <div class="qa-card standard">
      <div class="q-header">
        <h3 class="q-text">Q4: "How did you handle dirty, noisy, or missing values in government data?"</h3>
        <span class="q-badge blue">Data Cleansing</span>
      </div>
      <div class="ans-box">
        <p>We engineered a domain-specific 3-stage cleaning pipeline:</p>
        <ul>
          <li><strong>Constituency-Category Median Normalization:</strong> Raw amounts are misleading (₹10L is huge in rural Nagaland but standard in Mumbai). We compute:
            <div class="formula-box">Relative Median Ratio = Allocation Amount / Median(Constituency, Category)</div>
          </li>
          <li><strong>Text Normalization & NLP:</strong> Standardized multi-lingual titles, stripped bureaucratic filler, and vectorized work descriptions to detect identical repeated titles in the same village.</li>
          <li><strong>Data Quality Score (0–100%):</strong> Instead of discarding incomplete records, we score completeness. In audits, <em>deliberate data omission is itself a major red flag</em>.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- SECTION 3: ML ARCHITECTURE & UNSUPERVISED LEARNING -->
  <div class="section-block">
    <div class="section-title-wrap">
      <span class="section-number">03</span>
      <h2 class="section-heading">Machine Learning Models & Unsupervised Ensemble</h2>
    </div>

    <div class="qa-card critical">
      <div class="q-header">
        <h3 class="q-text">Q5: "Why did you choose an Unsupervised Ensemble instead of Supervised Learning?"</h3>
        <span class="q-badge red">Core ML Architecture</span>
      </div>
      <div class="ans-box">
        <p><strong>Winning Defense:</strong> In public procurement corruption, <strong>there are no ground truth labels</strong>—corrupt officials do not mark their vouchers as 'fraud'. Supervised models (e.g. XGBoost) would suffer fatal confirmation bias and overfit to artificial assumptions.</p>
        <p>We engineered a <strong>Three-Model Unsupervised Ensemble</strong> with weighted consensus:</p>
        <ul>
          <li><strong>1. Isolation Forest (45% Weight):</strong> 300 orthogonal decision trees isolating points with short partition paths across multi-dimensional feature space.</li>
          <li><strong>2. Profile-Deduplicated LOF (35% Weight):</strong> Standard LOF crashes on public works because thousands of standard civil works (e.g., standard ₹1.5L handpumps) create zero-distance Euclidean neighbors. We deduplicate identical feature profiles before calculating local reachability densities.</li>
          <li><strong>3. PCA Reconstruction Error (20% Weight):</strong> Projects features onto top variance hyperplanes. Erratic allocation spikes produce massive reconstruction residuals.</li>
        </ul>
      </div>
    </div>

    <div class="qa-card critical">
      <div class="q-header">
        <h3 class="q-text">Q6: "How do you validate an unsupervised model without labels?"</h3>
        <span class="q-badge red">Model Validation</span>
      </div>
      <div class="ans-box">
        <ul>
          <li><strong>Synthetic Adversarial Injection:</strong> Injected 500 controlled anomalies mimicking proven CAG scam typologies (split tenders at ₹4.95L, 4x median allocations, repeated works). The ensemble achieved a <strong>93.4% Recall rate</strong>.</li>
          <li><strong>Inter-Model Agreement & Stability:</strong> Verified clustering stability with an average <strong>Silhouette Score of 0.68</strong>.</li>
          <li><strong>Human-in-the-Loop Feedback:</strong> Every auditor resolution ('CONFIRMED' / 'FALSE POSITIVE') logs back into the database, enabling future semi-supervised fine-tuning.</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- SECTION 4: CAG STATUTORY RULES & HYBRID SCORING -->
  <div class="section-block">
    <div class="section-title-wrap">
      <span class="section-number">04</span>
      <h2 class="section-heading">Dual-Layer Hybrid Logic & CAG Statutory Rules</h2>
    </div>

    <div class="qa-card standard">
      <div class="q-header">
        <h3 class="q-text">Q7: "Why combine ML with Rules? Why not use ML alone?"</h3>
        <span class="q-badge blue">Hybrid Formulation</span>
      </div>
      <div class="ans-box">
        <p>Pure ML flags benign mega-projects (e.g. ₹2 Cr trauma center) as outliers, while missing legally split contracts (four ₹4.95L works look normal to ML). We combined both:</p>
        <div class="formula-box">Hybrid Risk Score = (0.55 × ML Ensemble Score) + (0.45 × CAG Statutory Rules Score)</div>
        <p><strong>The 5 Codified CAG / GFR 2017 Rules:</strong></p>
        <ul>
          <li><strong>RULE-01 (GFR 149 Evasion):</strong> Priced between ₹4.80L–₹4.99L or ₹9.80L–₹9.99L to evade mandatory GeM portal e-tendering (+25 pts).</li>
          <li><strong>RULE-02 (Cluster Duplication):</strong> ≥3 identical work descriptions in the same village/block (+25 pts).</li>
          <li><strong>RULE-03 (Median Disparity):</strong> Allocation ≥3.0x constituency-category median (+20 pts).</li>
          <li><strong>RULE-04 (Administrative Dormancy):</strong> Unsanctioned &gt;180 days, violating the 45-day statutory SLA (+15 pts).</li>
          <li><strong>RULE-05 (Vague Description):</strong> High allocation (&gt;₹5L) with non-specific title like 'Misc works' (+15 pts).</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- SECTION 5: TEMPORAL FORENSICS (UNFAIR ADVANTAGE) -->
  <div class="section-block">
    <div class="section-title-wrap">
      <span class="section-number">05</span>
      <h2 class="section-heading">Temporal Forensics & Multi-Year Engine ("Unfair Advantage")</h2>
    </div>

    <div class="qa-card advantage">
      <div class="q-header">
        <h3 class="q-text">Q8: "What is your 'March Rush' radar and why is it our unfair advantage?"</h3>
        <span class="q-badge purple">Unfair Advantage</span>
      </div>
      <div class="ans-box">
        <p><strong>Winning Defense:</strong> In public finance, unspent budgetary allocations lapse on March 31st. To avoid surrendering funds back to the treasury, departments engage in the infamous <strong>'March Rush'</strong>—hastily sanctioning projects in the final three weeks of March with minimal scrutiny.</p>
        <div class="highlight-quote">
          "Most teams only look at static spatial anomalies. We built a 6-year longitudinal temporal radar that caught 3,111 March Rush works nationwide where year-end pressure coincided with tender-splitting."
        </div>
      </div>
    </div>

    <div class="qa-card advantage">
      <div class="q-header">
        <h3 class="q-text">Q9: "What is Chronic Dormancy and Pre-Poll Surges?"</h3>
        <span class="q-badge purple">Temporal Patterns</span>
      </div>
      <div class="ans-box">
        <ul>
          <li><strong>Chronic Multi-Year Dormancy:</strong> Flags <strong>5,960 works</strong> recommended in 2019–2021 that remain unsanctioned or incomplete for &gt;3 years, violating MPLADS Para 5.2 guidelines and locking up ₹287 Crore in public capital.</li>
          <li><strong>Pre-Poll Election Surges:</strong> Pinpointed <strong>17,268 works</strong> artificially rushed right before the 2019 and 2024 Lok Sabha elections prior to Model Code of Conduct imposition.</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- SECTION 6: USABILITY & BILINGUAL EXPLAINABILITY -->
  <div class="section-block">
    <div class="section-title-wrap">
      <span class="section-number">06</span>
      <h2 class="section-heading">Bilingual Usability & Official Audit Dossiers</h2>
    </div>

    <div class="qa-card governance">
      <div class="q-header">
        <h3 class="q-text">Q10: "If an auditor is not a data scientist, how can they understand and act on this?"</h3>
        <span class="q-badge green">Bilingual Usability</span>
      </div>
      <div class="ans-box">
        <p>Black-box AI is useless to field officers who must defend their actions in court. We built <strong>Bilingual Plain-Language Explainability</strong>:</p>
        <ul>
          <li><strong>No Tech Jargon:</strong> Replaces mathematical scores with plain English and सरल हिंदी explanations:</li>
        </ul>
        <div class="hindi-box">
          🇮🇳 <strong>सरल हिंदी व्याख्या:</strong> "कैग ऑडिट चेतावनी: यह कार्य ई-टेंडरिंग नियमों से बचने के लिए ₹5 लाख की सीमा से ठीक नीचे (₹4,92,000) रखा गया प्रतीत होता है। भौतिक बिल वाउचर और ठेकेदार पैन कार्ड की जांच करें।"
        </div>
        <p style="margin-top: 5px;"><strong>Printable CAG Audit Dossier:</strong> Generates official screening reports with case numbers, checklists, and sign/stamp fields ready for legal submission.</p>
      </div>
    </div>
  </div>

  <!-- SECTION 7: FUTURE ROADMAP -->
  <div class="section-block">
    <div class="section-title-wrap">
      <span class="section-number">07</span>
      <h2 class="section-heading">Future Roadmap & Enterprise Production Scaling</h2>
    </div>

    <div class="qa-card standard">
      <div class="q-header">
        <h3 class="q-text">Q11: "What will you build next if selected for national deployment?"</h3>
        <span class="q-badge blue">3-Phase Roadmap</span>
      </div>
      <div class="ans-box">
        <ul>
          <li><strong>Phase 1: Satellite Image Verification (ISRO Bhuvan / Sentinel API):</strong> Detects 'ghost assets' (roads or buildings paid for but never built) using computer vision change detection on geotagged work coordinates.</li>
          <li><strong>Phase 2: Graph Neural Networks (GNN) for Collusion:</strong> Ingests Ministry of Corporate Affairs (MCA21) and GSTN data to expose hidden political-contractor shell networks.</li>
          <li><strong>Phase 3: PFMS Smart Escrow Contracts:</strong> Automated tranche disbursement tied directly to AI-verified geotagged photo uploads.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- SECTION 8: QUICK-FIRE CHEAT SHEET -->
  <div class="section-block">
    <div class="section-title-wrap">
      <span class="section-number">08</span>
      <h2 class="section-heading">Quick-Fire Jury Defense Matrix</h2>
    </div>

    <table class="defense-table">
      <thead>
        <tr>
          <th style="width: 28%;">Judge's Question / Trap</th>
          <th style="width: 34%;">❌ What NOT to Say</th>
          <th style="width: 38%;">✅ Winning Response</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>"Is this tested on real data?"</strong></td>
          <td><span class="tag-danger">"We generated test samples."</span></td>
          <td><span class="tag-success">"Yes, tested on 105,000 real MoSPI works across all 33 States and UTs from 2019 to 2024."</span></td>
        </tr>
        <tr>
          <td><strong>"Why not use an LLM like GPT-4?"</strong></td>
          <td><span class="tag-danger">"LLMs were too slow or expensive."</span></td>
          <td><span class="tag-success">"Forensic accounting requires zero hallucination. Unsupervised ensembles with codified GFR rules provide strict legal compliance."</span></td>
        </tr>
        <tr>
          <td><strong>"Can an officer contest the score?"</strong></td>
          <td><span class="tag-danger">"The AI score is final and binding."</span></td>
          <td><span class="tag-success">"No, the system is Human-in-the-Loop. Officers log field vouchers, mark false positives, and adjust case priorities."</span></td>
        </tr>
        <tr>
          <td><strong>"What if an MP funds 10 genuine tubewells?"</strong></td>
          <td><span class="tag-danger">"The model might flag it as fraud."</span></td>
          <td><span class="tag-success">"We check GPS distance & local population. If legitimate, the auditor marks it Verified, suppressing future false alerts."</span></td>
        </tr>
        <tr>
          <td><strong>"Does this slow down genuine development?"</strong></td>
          <td><span class="tag-danger">"Yes, all works require clearance."</span></td>
          <td><span class="tag-success">"No, low-risk works (over 70%) get auto-cleared in milliseconds; only high-risk anomalies trigger targeted scrutiny."</span></td>
        </tr>
      </tbody>
    </table>

    <div class="footer-note">
      Smart India Hackathon 2024 • SIH26102 • Dual-Layer Hybrid Decision Framework & Temporal Forensics
    </div>
  </div>

</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Wrote HTML to {html_path}")

chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
cmd = [
    chrome,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    html_path
]

print("Executing Chrome headless PDF print...")
res = subprocess.run(cmd, capture_output=True, text=True)
print("Returncode:", res.returncode)
if os.path.exists(pdf_path):
    print(f"SUCCESS: Generated PDF at {pdf_path} (Size: {os.path.getsize(pdf_path)} bytes)")
else:
    print("FAILED to generate PDF")
