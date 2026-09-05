# SIH26102 — AI-Powered MPLADS Anomaly & Risk Detection System

An AI-assisted screening platform for identifying potential anomalies, financial irregularities, documentation gaps, and implementation inefficiencies in MPLADS projects.

> **Important:** The system identifies potential anomaly patterns and high-risk projects for human/audit verification. A high-risk score is NOT proof of fraud.

---

## Problem Statement

**SIH26102**

Development of an AI-powered system to detect anomalies, fraud, and inefficiencies in MPLAD Scheme implementation.

The system is designed as a decision-support and audit-screening platform that combines:

- Machine Learning anomaly detection
- CAG-inspired domain rules
- Hybrid risk scoring
- Explainable risk factors
- Officer investigation workflow
- PostgreSQL database
- FastAPI backend
- React dashboard

---

# System Architecture

```text
                    MPLADS DATA
                         |
                         v
                Data Validation
                         |
                         v
                Feature Engineering
                         |
              +----------+----------+
              |                     |
              v                     v
       Isolation Forest            LOF
              |                     |
              +----------+----------+
                         |
                         v
                    Ensemble ML
                         |
                         |
              +----------+----------+
              |                     |
              v                     v
        ML Risk Score        CAG Rule Engine
              |                     |
              +----------+----------+
                         |
                         v
                 Hybrid Risk Score
                         |
                         v
                  Explainability
                         |
                         v
                PostgreSQL Database
                         |
                         v
                    FastAPI
                         |
                         v
                  React Dashboard
                         |
                         v
              Investigation Queue
Key Features
1. Data Validation

The preprocessing pipeline checks:

Required columns
Missing values
Duplicate project IDs
Numeric validity
Negative financial values
Boolean validity
Expenditure anomalies
UC/expenditure discrepancies
Large completion delays

Validation warnings are retained rather than automatically treating every unusual value as fraud.

2. Feature Engineering

The system derives financial, documentation, and implementation indicators including:

Expenditure ratio
Expenditure deviation percentage
Absolute expenditure deviation
UC/expenditure difference
UC ratio
UC discrepancy percentage
Missing UC
Completion delay
Severe delay
Extreme delay
Delay-to-duration ratio
Expenditure per project-duration day
Expenditure per elapsed day
Excess expenditure
Extreme expenditure
Missing UC + high expenditure

These features are used by the anomaly detection models and rule engine.

Machine Learning Layer

The ML layer uses two complementary unsupervised anomaly detection techniques.

Isolation Forest

Isolation Forest identifies observations that are relatively easy to isolate from the rest of the dataset.

Configuration:

n_estimators = 200
contamination = 0.05
random_state = 42
Local Outlier Factor

LOF identifies observations that have substantially different local density compared with their neighboring observations.

Configuration:

n_neighbors = 20
contamination = 0.05
Ensemble ML

Isolation Forest and LOF are combined to reduce dependence on a single anomaly detector.

Current weighting:

Isolation Forest : 40%
LOF              : 60%

The model outputs are percentile-calibrated to produce a normalized ML risk score from approximately 0–100.

CAG-Inspired Rule Engine

The rule engine provides domain-aware screening signals inspired by historical audit irregularity patterns.

Current rules include:

Rule	Description
Excess expenditure	Actual expenditure exceeds sanctioned amount
Extreme expenditure	Expenditure exceeds sanction by more than 25%
Missing UC	Utilization Certificate unavailable
UC mismatch	UC amount materially differs from expenditure
Significant delay	Completion delay exceeds 180 days
Severe delay	Completion delay exceeds one year
Not started	Project work has not started

The rule engine is intended to complement ML rather than replace it.

Hybrid Risk Engine

The final risk score combines ML and rule-based evidence.

Hybrid Risk Score =
    60% × Ensemble ML Risk
  + 40% × Rule Risk

Risk levels:

75–100  → CRITICAL
50–74   → HIGH
25–49   → MEDIUM
0–24    → LOW

The system also generates human-readable explanations for the risk factors contributing to a project's score.

Synthetic Benchmark

The current development dataset contains:

Projects                 : 1,000
Synthetic anomalies      : 50
Anomaly proportion       : 5%

The benchmark contains injected synthetic anomaly patterns such as:

Excess expenditure
Large completion delays
Missing utilization certificates
UC/expenditure mismatches

Using the current controlled synthetic dataset, the final hybrid screening configuration produced:

Precision : 0.80
Recall    : 0.80
F1 Score  : 0.80

True Positives  : 40
False Positives : 10
False Negatives : 10
True Negatives  : 940

This corresponds to approximately 98% overall accuracy on the synthetic benchmark.

Important Benchmark Limitation

These metrics are based only on synthetic ground-truth labels.

They must NOT be interpreted as real-world MPLADS fraud-detection accuracy.

The synthetic dataset is used to validate the technical pipeline during development. Real deployment requires validated MPLADS records and appropriate audit-confirmed outcomes.

Risk Interpretation

The system does not make a legal or audit finding.

Instead, it produces signals such as:

Potential Anomaly
High-Risk Pattern
Audit Attention Required
Requires Verification

For example:

CRITICAL

ML Risk:       97.96
Rule Risk:     45.00
Hybrid Risk:   76.78

Reasons:
- Expenditure exceeds sanction
- Expenditure >25% above sanction
- Missing utilization certificate

Action:
Requires human/audit verification
Human-in-the-Loop Workflow
Project Data
     |
     v
Automated Screening
     |
     v
Risk Score + Explanation
     |
     v
Officer Review
     |
     +-------> Valid Project
     |
     +-------> Requires Verification
     |
     +-------> Investigation
     |
     v
Audit / Administrative Action

The final decision remains with authorized officers and auditors.

Backend

The backend is implemented using:

Python
FastAPI
SQLAlchemy
PostgreSQL
API Endpoints
GET  /
GET  /projects
GET  /projects/{project_id}

GET  /anomalies
GET  /critical

GET  /statistics
GET  /states
GET  /states/{state_name}
GET  /constituencies/{constituency}

POST /investigations
GET  /investigations/{project_id}
PUT  /investigations/{project_id}
Database

PostgreSQL stores:

Project information
Financial indicators
ML risk score
Rule risk score
Hybrid risk score
Risk level
Risk explanation
Investigation records
Officer notes
Investigation status

Current development database:

Database : sih26102
Projects : 1000
Frontend

The frontend is implemented using:

React
Vite
JavaScript
Axios
Recharts
Lucide React
CSS

The dashboard provides:

Overall project statistics
Risk distribution
Hybrid risk engine overview
High-risk project queue
Project-level risk analysis
ML vs rule risk
Explainable risk factors
Investigation workflow
Project Structure
SIH26102/
│
├── data/
│   ├── synthetic_mplads.csv
│   ├── validated_mplads.csv
│   ├── processed_mplads.csv
│   ├── ml_results.csv
│   ├── lof_results.csv
│   ├── ensemble_results.csv
│   ├── rule_results.csv
│   ├── hybrid_risk_results.csv
│   └── hybrid_evaluation_results.csv
│
├── ml/
│   ├── generate_data.py
│   ├── data_validation.py
│   ├── feature_engineering.py
│   ├── anomaly_model.py
│   ├── lof_model.py
│   ├── ensemble_model.py
│   ├── rules.py
│   ├── hybrid_risk_scoring.py
│   ├── evaluate_model.py
│   ├── evaluate_lof.py
│   └── evaluate_hybrid.py
│
├── models/
│   ├── isolation_forest.pkl
│   ├── scaler.pkl
│   ├── lof_model.pkl
│   ├── lof_scaler.pkl
│   └── ...
│
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── App.css
│
├── database.py
├── db_models.py
├── main.py
├── requirements.txt
└── README.md
Running the Project
1. Activate virtual environment

Windows PowerShell:

.\venv\Scripts\Activate.ps1
2. Install dependencies
pip install -r requirements.txt
3. Generate development dataset
python ml/generate_data.py
4. Validate data
python ml/data_validation.py
5. Feature engineering
python ml/feature_engineering.py
6. Run Isolation Forest
python ml/anomaly_model.py
7. Run LOF
python ml/lof_model.py
8. Run ensemble
python ml/ensemble_model.py
9. Run CAG-inspired rules
python ml/rules.py
10. Generate hybrid risk
python ml/hybrid_risk_scoring.py
11. Evaluate
python ml/evaluate_hybrid.py
Database Setup

Create a PostgreSQL database named:

sih26102

Configure the connection string in:

database.py

Initialize tables:

python ml/init_database.py

Load the latest hybrid results:

python ml/load_database.py
Start Backend

From the project root:

uvicorn main:app --reload

Backend:

http://127.0.0.1:8000
Start Frontend

Open a second terminal:

cd frontend
npm install
npm run dev

Frontend:

http://localhost:5173
Technology Stack
Layer	Technology
Frontend	React + Vite
Styling	CSS
Visualization	Recharts
Icons	Lucide React
Backend	FastAPI
ORM	SQLAlchemy
Database	PostgreSQL
ML	scikit-learn
Data Processing	Pandas + NumPy
Models	Isolation Forest + LOF
Domain Intelligence	CAG-inspired Rules
Development	VS Code
Version Control	Git + GitHub
Data Strategy

The prototype is designed to support multiple sources of evidence.

Potential production data sources include:

Official MPLADS datasets
eSAKSHI data where accessible
MPLADS public dashboard information
Project expenditure information
Utilization Certificate records
Project completion information
Uploaded project documentation
Audit observations

Historical CAG observations can be used to inform domain rules and validation logic.

They should not be treated as conventional machine-learning labels unless appropriately structured and validated.

Production Data Considerations

The current development benchmark uses synthetic data.

A production implementation should address:

Official data access
Data-sharing permissions
Historical vs current system differences
eSAKSHI integration
Document availability
OCR for scanned records
Missing records
Data quality inconsistencies
Audit-confirmed labels
Model drift
Threshold calibration
State/district/agency-specific baselines
Security and access control
Limitations
The current dataset is synthetic.
Synthetic anomaly labels do not represent confirmed fraud.
Model performance has not been validated against real audit-confirmed MPLADS outcomes.
Historical CAG observations are used as domain knowledge rather than direct ML labels.
Missing data can increase uncertainty.
Risk thresholds require calibration on real operational data.
High-risk projects require human verification.
The current prototype does not independently establish legal or financial misconduct.
Future Scope
Data Integration
Integrate official MPLADS/eSAKSHI datasets
Automated ingestion pipelines
Historical project tracking
Advanced ML
Autoencoder-based anomaly detection
Graph-based relationship analysis
Temporal anomaly detection
District/state-specific baselines
Model ensemble optimization
Document Intelligence
OCR
UC extraction
Sanction-order extraction
Estimate/BOQ comparison
Document consistency checking
Explainable AI
SHAP-based explanations
Feature contribution visualization
Evidence-linked explanations
Investigation Workflow
Officer assignment
Investigation status tracking
Evidence attachments
Audit notes
Resolution history
Escalation workflow
Security
Authentication
Role-based access control
Audit logging
Encryption
Secure deployment
Responsible AI Position

This platform is designed as an audit-screening and decision-support system.

It should:

prioritize projects for review,
surface unusual patterns,
explain why a project was flagged,
support evidence-based investigation.

It should not:

automatically accuse an individual or organization,
declare fraud solely from an ML score,
replace authorized officers or auditors,
treat synthetic benchmark performance as real-world accuracy.
Smart India Hackathon

Problem Statement: SIH26102

Theme: AI-powered anomaly, fraud-risk, and inefficiency detection in MPLADS implementation.

The prototype demonstrates a complete technical pipeline from data validation and anomaly detection to hybrid risk scoring, database storage, API delivery, and an officer-facing dashboard.