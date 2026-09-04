# SIH26102 — AI-Powered MPLADS Anomaly Detection & Risk Monitoring System

An AI/ML-powered system for detecting potential anomalies, inefficiencies, and high-risk patterns in the implementation of the Members of Parliament Local Area Development Scheme (MPLADS).

The system combines machine learning-based anomaly detection with explainable domain and audit rules to prioritize projects for human verification.

---

## 🚀 Project Overview

MPLADS involves a large number of development works distributed across constituencies, sectors, implementing agencies, and districts.

Monitoring such projects manually can make it difficult to identify:

- Unusual expenditure patterns
- Excess expenditure
- Significant project delays
- Missing Utilization Certificates
- UC and expenditure mismatches
- Unusual combinations of financial and project attributes
- Projects requiring detailed audit attention

SIH26102 aims to build an intelligent risk-monitoring system that helps monitoring authorities identify projects that deserve further investigation.

The system does **not** automatically declare a project fraudulent.

Instead, it produces:

> **Potential Anomaly → Risk Score → Explanation → Human Verification**

---

# 🎯 Objectives

The major objectives of the system are:

1. Detect unusual project patterns using machine learning.
2. Identify rule-based financial and procedural anomalies.
3. Combine ML and domain-rule signals into a hybrid risk score.
4. Provide explainable reasons for every flagged project.
5. Prioritize projects for officer investigation.
6. Maintain investigation outcomes and officer notes.
7. Provide a centralized monitoring dashboard.
8. Support future integration with actual MPLADS/eSAKSHI data.

---

# 🧠 System Architecture

```text
                    MPLADS PROJECT DATA
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Data Validation &    │
                 │ Feature Engineering  │
                 └──────────┬──────────┘
                            │
             ┌──────────────┴──────────────┐
             │                             │
             ▼                             ▼
   ┌───────────────────┐        ┌────────────────────┐
   │ Machine Learning  │        │ Domain Rule Engine  │
   │ Anomaly Detection │        │                    │
   └─────────┬─────────┘        └──────────┬─────────┘
             │                             │
             ▼                             ▼
   ┌───────────────────┐        ┌────────────────────┐
   │ Isolation Forest   │        │ Audit / MPLADS     │
   │ +                  │        │ Risk Rules         │
   │ Local Outlier      │        └──────────┬─────────┘
   │ Factor (LOF)       │                   │
   └─────────┬─────────┘                   │
             │                             │
             ▼                             ▼
        ┌────────────────────────────────────┐
        │        HYBRID RISK ENGINE           │
        │                                    │
        │ ML Risk × 60% + Rule Risk × 40%    │
        └────────────────┬───────────────────┘
                         │
                         ▼
               ┌─────────────────────┐
               │ Explainability      │
               │ & Risk Signals      │
               └──────────┬──────────┘
                          │
                          ▼
               ┌─────────────────────┐
               │ Officer Dashboard   │
               │ & Investigation     │
               └──────────┬──────────┘
                          │
                          ▼
                    PostgreSQL
🤖 Machine Learning Approach

The system currently uses an ensemble of two unsupervised anomaly detection algorithms.

1. Isolation Forest

Isolation Forest identifies observations that are easier to isolate from the rest of the dataset.

It is useful for detecting unusual combinations of:

Expenditure
Sanctioned amount
Project duration
Completion delay
UC values
Expenditure ratios

Model configuration includes:

n_estimators = 200
contamination = 0.05
random_state = 42
2. Local Outlier Factor (LOF)

Local Outlier Factor identifies observations that have substantially different local density compared with neighboring observations.

It helps identify projects that may look unusual relative to projects with similar characteristics.

Current configuration:

n_neighbors = 20
contamination = 0.05
🔀 ML Ensemble

Isolation Forest and LOF are combined to produce an ensemble ML risk score.

Current weighting:

Isolation Forest + LOF
        ↓
   Ensemble ML Risk

The ensemble helps reduce dependence on a single anomaly detection algorithm.

📊 Hybrid Risk Engine

The final system combines machine-learning signals with explainable domain rules.

Hybrid Risk Score

= (ML Risk × 0.60)
+ (Rule Risk × 0.40)

Therefore:

60% → Machine Learning
40% → Domain / Audit Rules

This approach combines:

Statistical anomaly detection
Local anomaly detection
Domain knowledge
Audit-oriented rules
Explainability
⚠️ Risk Classification

Projects are classified using the hybrid risk score:

Score	Classification
75–100	CRITICAL
50–74.99	HIGH
25–49.99	MEDIUM
0–24.99	LOW

These classifications are intended for prioritization and verification.

They are not proof of fraud or wrongdoing.

🔎 Risk Signals

The current prototype considers signals including:

Financial
Actual expenditure exceeding sanctioned amount
Substantially high expenditure
Extreme expenditure deviation
Expenditure/UC mismatch
Documentation
Missing Utilization Certificate
UC amount inconsistent with expenditure
Project Execution
Significant completion delay
Severe delay
Extreme delay
Projects with unusual duration/expenditure relationships
📚 Domain & Audit Rules

The rule engine is based on MPLADS-related procedural and audit-risk patterns.

The current rule library includes checks corresponding to patterns such as:

Delayed recommendation
Execution without MP recommendation
Sanction above MP-indicated amount
Inadmissible works
Excess funding to societies/trusts
Missing feasibility/estimate
Implementing-agency selection anomalies
Non-commencement
Delayed completion
Long incomplete works
Doubtful vouchers
Assets not in use
Asset misuse
Financial reporting mismatches
UC/accounts/MPR mismatches
Missing Utilization Certificates
Fund diversion
Excess advances
Unspent balances not refunded
Missing public disclosure
SC/ST allocation shortfalls

These rules are intended to convert known audit-risk patterns into machine-checkable signals.

🧪 Current Dataset

The current development version uses synthetic MPLADS-like project data for model development and evaluation.

The dataset contains:

1,000 projects

with features such as:

Project ID
State
District
Constituency
Sanctioned amount
Actual expenditure
Project duration
Completion delay
UC availability
UC amount
Work status
Sector
Implementing agency

Synthetic anomalies were injected to evaluate the anomaly detection pipeline.

Important

The synthetic geographic fields and project records are not real MPLADS records.

They should not be interpreted as actual government findings.

The actual_anomaly field is synthetic ground truth created only for development/evaluation.

📈 Synthetic Benchmark Results

The current synthetic benchmark produced the following results for the ML ensemble:

Precision : 0.82
Recall    : 0.82
F1 Score  : 0.82

These results are based on the synthetic dataset and must not be interpreted as real-world MPLADS model performance.

Real-world performance will need to be evaluated after integrating actual MPLADS/eSAKSHI data and obtaining verified investigation/audit outcomes.

🗄️ Database

The system uses PostgreSQL.

Main project information is stored in the projects table.

Investigation information is stored in the investigations table.

The database stores:

Project
Project ID
Location
Financial information
Project status
UC information
ML risk score
Rule risk score
Hybrid risk score
Risk level
Risk explanation
Investigation
Project ID
Investigation status
Officer notes
Created timestamp
Updated timestamp
🔌 Backend

The backend is implemented using:

Python
FastAPI
SQLAlchemy
PostgreSQL

Main API endpoints include:

GET  /
GET  /projects
GET  /projects/{project_id}
GET  /anomalies
GET  /critical
GET  /statistics
GET  /states
GET  /states/{state_name}
GET  /constituencies/{constituency}

POST /investigations/{project_id}
GET  /investigations/{project_id}
PUT  /investigations/{project_id}

FastAPI provides the interface between the React frontend and PostgreSQL database.

💻 Frontend

The dashboard is built using:

React
Vite
Axios
Recharts
Lucide React
CSS

The dashboard provides:

Monitoring Dashboard
Total projects
Total expenditure
High-risk projects
Critical projects
Risk distribution
Monitoring summary
Investigation queue
Project Investigation
Project information
Financial details
Project status
Implementation information
ML risk
Rule risk
Hybrid risk
Risk explanation
Detected risk signals
Recommended verification actions
Officer Investigation

Officers can record:

NEW
UNDER REVIEW
VERIFIED
FALSE POSITIVE
ESCALATED
CLOSED

along with investigation notes.

Investigation records are persisted in PostgreSQL.

📁 Project Structure
SIH26102/
│
├── data/
│   └── synthetic_mplads.csv
│
├── ml/
│   ├── __init__.py
│   ├── generate_data.py
│   ├── feature_engineering.py
│   ├── anomaly_model.py
│   ├── lof_model.py
│   ├── ensemble_model.py
│   ├── rules.py
│   ├── risk_scoring.py
│   ├── hybrid_risk_scoring.py
│   ├── evaluate_model.py
│   ├── evaluate_lof.py
│   ├── evaluate_ensemble.py
│   ├── init_database.py
│   └── load_database.py
│
├── models/
│   ├── isolation_forest.pkl
│   ├── scaler.pkl
│   ├── lof_model.pkl
│   └── lof_scaler.pkl
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
│
├── database.py
├── db_models.py
├── main.py
├── requirements.txt
└── README.md
⚙️ Local Setup
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd SIH26102
2. Create Python virtual environment
python -m venv venv

Activate it on Windows:

venv\Scripts\activate
3. Install Python dependencies
pip install -r requirements.txt
🧪 Generate Synthetic Data

Run:

python ml/generate_data.py

This generates:

data/synthetic_mplads.csv
🔧 Feature Engineering

Run:

python ml/feature_engineering.py

This generates:

data/processed_mplads.csv
🤖 Run Machine Learning Models
Isolation Forest
python ml/anomaly_model.py
LOF
python ml/lof_model.py
ML Ensemble
python ml/ensemble_model.py
📋 Run Rule Engine
python ml/rules.py
🔀 Run Hybrid Risk Engine

After the ML ensemble and rule engine have completed:

python ml/hybrid_risk_scoring.py

This generates:

data/hybrid_risk_results.csv
🗃️ PostgreSQL Setup

Create a PostgreSQL database named:

sih26102

Update the database connection in:

database.py

Example:

DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/sih26102"

Create the tables:

python ml/init_database.py

Load the hybrid results:

python ml/load_database.py
🚀 Start FastAPI

From the project root:

uvicorn main:app --reload

Backend:

http://127.0.0.1:8000

Swagger API documentation:

http://127.0.0.1:8000/docs
🌐 Start React Frontend

Open another terminal:

cd frontend

Install dependencies:

npm install

Start Vite:

npm run dev

Frontend:

http://localhost:5173
🔄 Complete Development Pipeline
generate_data.py
       ↓
synthetic_mplads.csv
       ↓
feature_engineering.py
       ↓
processed_mplads.csv
       ↓
 ┌───────────────┐
 │               │
 ▼               ▼
Isolation       LOF
Forest
 │               │
 └───────┬───────┘
         ↓
ensemble_model.py
         ↓
ensemble_results.csv
         +
rules.py
         ↓
rule_results.csv
         ↓
hybrid_risk_scoring.py
         ↓
hybrid_risk_results.csv
         ↓
load_database.py
         ↓
PostgreSQL
         ↓
FastAPI
         ↓
React Dashboard
         ↓
Officer Investigation
🛡️ Human-in-the-Loop Design

The system follows a human-in-the-loop approach.

The AI system:

Detects
   ↓
Scores
   ↓
Explains
   ↓
Prioritizes

The authorized officer:

Reviews
   ↓
Verifies documents
   ↓
Investigates
   ↓
Records outcome

This prevents an anomaly score from being treated as an automatic determination of fraud.

🔮 Future Scope

The current prototype can be extended with:

Real MPLADS Data

Integrate actual:

MPLADS public dashboard data
eSAKSHI data where accessible
Historical MPLADS datasets
District-level records
Publicly available audit information
Advanced Anomaly Detection

Potential future models:

Autoencoders
One-Class SVM
DBSCAN
Temporal anomaly detection
Graph-based anomaly detection
Document Intelligence

Add OCR/document processing for:

Utilization Certificates
Bills
Sanction documents
Completion certificates
Work photographs
Supporting records
Explainable AI

Future versions can use:

SHAP
Feature contribution analysis
Local explanations
Rule + ML evidence visualization
Geospatial Analysis

Integrate GIS data to detect:

Geographic clustering
Repeated implementing agencies
Project concentration
Constituency-level patterns
Production Deployment

Future deployment can include:

React
   ↓
Cloud API
   ↓
FastAPI
   ↓
Managed PostgreSQL
⚠️ Current Limitations
The current development dataset is synthetic.
Synthetic anomaly labels are not official fraud labels.
ML benchmark results do not represent real-world accuracy.
Real MPLADS data may have missing or inconsistent fields.
Historical MPLADS data availability differs across reporting periods.
Anomaly detection identifies unusual patterns, not confirmed fraud.
Final decisions require human verification and supporting evidence.
Model thresholds will need recalibration using real operational data.
📌 Important Disclaimer

This project is a prototype developed for Smart India Hackathon problem statement SIH26102.

Risk scores and anomaly flags are intended to assist monitoring and audit prioritization.

A high-risk score does not establish fraud, corruption, or wrongdoing.

Every flagged project should undergo appropriate human review and verification using official records and supporting documentation.

🏆 Smart India Hackathon

Problem Statement: SIH26102

Theme: AI-powered anomaly, fraud and inefficiency detection in MPLADS implementation.

The project focuses on combining:

Artificial Intelligence
+
Machine Learning
+
Domain Knowledge
+
Audit Rules
+
Explainable Risk Scoring
+
Human-in-the-Loop Investigation

to build an intelligent monitoring system for public-development projects.

👥 Team

Smart India Hackathon 2026

Team: SIH26102