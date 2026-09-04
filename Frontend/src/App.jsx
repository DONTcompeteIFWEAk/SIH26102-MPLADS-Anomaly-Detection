import { useEffect, useState } from "react";
import axios from "axios";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import {
  Database,
  AlertTriangle,
  IndianRupee,
  Clock,
  FileWarning,
  ArrowLeft,
  Search,
  Save,
  ClipboardCheck,
} from "lucide-react";

import "./App.css";


const API_URL = "http://127.0.0.1:8000";


function App() {

  // =====================================================
  // STATE
  // =====================================================

  const [statistics, setStatistics] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [projects, setProjects] = useState([]);

  const [selectedProject, setSelectedProject] = useState(null);

  const [investigationStatus, setInvestigationStatus] =
    useState("NEW");

  const [officerNote, setOfficerNote] =
    useState("");

  const [investigationExists, setInvestigationExists] =
    useState(false);

  const [savingInvestigation, setSavingInvestigation] =
    useState(false);

  const [saveMessage, setSaveMessage] =
    useState("");

  const [search, setSearch] = useState("");

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState(null);


  // =====================================================
  // LOAD DASHBOARD DATA
  // =====================================================

  useEffect(() => {

    async function loadData() {

      try {

        setLoading(true);

        const [
          statisticsResponse,
          anomaliesResponse,
          projectsResponse
        ] = await Promise.all([

          axios.get(`${API_URL}/statistics`),

          axios.get(`${API_URL}/anomalies`),

          axios.get(`${API_URL}/projects`)

        ]);

        setStatistics(statisticsResponse.data);

        setAnomalies(anomaliesResponse.data);

        setProjects(projectsResponse.data);

        setError(null);

      } catch (err) {

        console.error(err);

        setError(
          "Unable to connect to the SIH26102 backend."
        );

      } finally {

        setLoading(false);

      }

    }

    loadData();

  }, []);


  // =====================================================
  // LOAD SELECTED PROJECT
  // =====================================================

  async function openProject(projectId) {

    try {

      setSaveMessage("");

      // Get project
      const projectResponse = await axios.get(
        `${API_URL}/projects/${projectId}`
      );

      setSelectedProject(projectResponse.data);


      // Reset investigation form
      setInvestigationStatus("NEW");
      setOfficerNote("");
      setInvestigationExists(false);


      // Try to get existing investigation
      try {

        const investigationResponse = await axios.get(
          `${API_URL}/investigations/${projectId}`
        );

        setInvestigationStatus(
          investigationResponse.data.status || "NEW"
        );

        setOfficerNote(
          investigationResponse.data.officer_note || ""
        );

        setInvestigationExists(true);

      } catch (investigationError) {

        // 404 means investigation hasn't been created yet.
        // This is normal for a new project.

        if (
          investigationError.response &&
          investigationError.response.status !== 404
        ) {

          console.error(
            "Investigation loading error:",
            investigationError
          );

        }

      }

    } catch (err) {

      console.error(err);

      alert("Unable to load project.");

    }

  }


  // =====================================================
  // SAVE INVESTIGATION
  // =====================================================

  async function saveInvestigation() {

    if (!selectedProject) {
      return;
    }

    try {

      setSavingInvestigation(true);

      setSaveMessage("");

      const response = await axios.put(
        `${API_URL}/investigations/${selectedProject.project_id}`,
        {
          status: investigationStatus,
          officer_note: officerNote
        }
      );

      console.log(response.data);

      setInvestigationExists(true);

      setSaveMessage(
        "Investigation saved successfully."
      );

    } catch (err) {

      console.error(err);

      setSaveMessage(
        "Failed to save investigation."
      );

    } finally {

      setSavingInvestigation(false);

    }

  }


  // =====================================================
  // FILTER PROJECTS
  // =====================================================

  const filteredProjects = anomalies.filter((project) => {

    const value = search.toLowerCase();

    return (

      project.project_id
        .toLowerCase()
        .includes(value)

      ||

      project.state
        .toLowerCase()
        .includes(value)

      ||

      project.district
        .toLowerCase()
        .includes(value)

      ||

      project.constituency
        .toLowerCase()
        .includes(value)

    );

  });


  // =====================================================
  // LOADING SCREEN
  // =====================================================

  if (loading) {

    return (

      <div className="loading-screen">

        <Database size={50} />

        <h2>
          Loading SIH26102 Dashboard
        </h2>

        <p>
          Connecting to PostgreSQL through FastAPI...
        </p>

      </div>

    );

  }


  // =====================================================
  // ERROR SCREEN
  // =====================================================

  if (error) {

    return (

      <div className="loading-screen">

        <AlertTriangle size={50} />

        <h2>
          Backend Connection Failed
        </h2>

        <p>
          {error}
        </p>

        <code>
          http://127.0.0.1:8000
        </code>

      </div>

    );

  }


  // =====================================================
  // PROJECT INVESTIGATION PAGE
  // =====================================================

  if (selectedProject) {

    const p = selectedProject;

    const expenditureExcess =
      Number(p.actual_expenditure) >
      Number(p.sanctioned_amount);

    const ucMissing =
      !p.uc_available;

    const severeDelay =
      Number(p.completion_delay_days) > 180;


    return (

      <div className="app">

        {/* HEADER */}

        <header className="topbar">

          <div className="brand">

            <Database size={24} />

            <span>
              SIH26102
            </span>

          </div>

          <span className="system-title">
            MPLADS Risk & Anomaly Detection System
          </span>

        </header>


        <main className="main-content">

          {/* BACK */}

          <button
            className="back-button"
            onClick={() => {

              setSelectedProject(null);
              setSaveMessage("");

            }}
          >

            <ArrowLeft size={18} />

            Back to Dashboard

          </button>


          {/* PROJECT HEADER */}

          <section className="project-header">

            <div>

              <div className="small-label">
                PROJECT INVESTIGATION
              </div>

              <h1>
                {p.project_id}
              </h1>

              <p className="project-location">
                {p.state}
                {" • "}
                {p.district}
                {" • "}
                {p.constituency}
              </p>

            </div>


            <div
              className={`risk-header ${p.risk_level?.toLowerCase()}`}
            >

              <span>
                {p.risk_level}
              </span>

              <strong>
                {Number(p.risk_score).toFixed(1)}
              </strong>

              <small>
                Risk Score
              </small>

            </div>

          </section>


          {/* FINANCIAL + STATUS */}

          <section className="detail-grid">


            {/* FINANCIAL */}

            <div className="detail-card">

              <div className="card-title">

                <IndianRupee size={20} />

                <h3>
                  Financial Details
                </h3>

              </div>


              <div className="detail-row">

                <span>
                  Sanctioned Amount
                </span>

                <strong>
                  ₹
                  {Number(
                    p.sanctioned_amount
                  ).toLocaleString("en-IN")}
                </strong>

              </div>


              <div className="detail-row">

                <span>
                  Actual Expenditure
                </span>

                <strong>
                  ₹
                  {Number(
                    p.actual_expenditure
                  ).toLocaleString("en-IN")}
                </strong>

              </div>


              <div className="detail-row">

                <span>
                  Expenditure Ratio
                </span>

                <strong>
                  {Number(
                    p.expenditure_ratio
                  ).toFixed(2)}x
                </strong>

              </div>

            </div>


            {/* PROJECT STATUS */}

            <div className="detail-card">

              <div className="card-title">

                <Clock size={20} />

                <h3>
                  Project Status
                </h3>

              </div>


              <div className="detail-row">

                <span>
                  Work Status
                </span>

                <strong>
                  {p.work_status}
                </strong>

              </div>


              <div className="detail-row">

                <span>
                  Completion Delay
                </span>

                <strong>
                  {p.completion_delay_days} days
                </strong>

              </div>


              <div className="detail-row">

                <span>
                  Utilization Certificate
                </span>

                <strong>
                  {p.uc_available
                    ? "Available"
                    : "Missing"}
                </strong>

              </div>

            </div>


            {/* IMPLEMENTATION */}

            <div className="detail-card">

              <div className="card-title">

                <Database size={20} />

                <h3>
                  Implementation
                </h3>

              </div>


              <div className="detail-row">

                <span>
                  Sector
                </span>

                <strong>
                  {p.sector}
                </strong>

              </div>


              <div className="detail-row">

                <span>
                  Implementing Agency
                </span>

                <strong>
                  {p.implementing_agency}
                </strong>

              </div>

            </div>

          </section>


          {/* AI RISK ANALYSIS */}

          <section className="panel">

            <div className="section-heading">

              <div>

                <h2>
                  AI Risk Analysis
                </h2>

                <p>
                  Hybrid ML + rule-based assessment
                </p>

              </div>

            </div>


            <div className="risk-score-grid">


              <div className="score-card">

                <span>
                  ML Risk
                </span>

                <strong>
                  {Number(
                    p.ml_risk_score
                  ).toFixed(1)}
                </strong>

              </div>


              <div className="score-card">

                <span>
                  Rule Risk
                </span>

                <strong>
                  {Number(
                    p.rule_risk_score
                  ).toFixed(1)}
                </strong>

              </div>


              <div className="score-card final-score">

                <span>
                  Hybrid Risk
                </span>

                <strong>
                  {Number(
                    p.risk_score
                  ).toFixed(1)}
                </strong>

              </div>

            </div>


            {/* WHY FLAGGED */}

            <div className="explanation-box">

              <h3>
                <AlertTriangle size={19} />
                Why was this project flagged?
              </h3>

              <p>
                {p.risk_explanation}
              </p>

            </div>


            {/* SIGNALS */}

            <div className="signals-box">

              <h3>
                Detected Risk Signals
              </h3>


              <div className="signal-list">

                {expenditureExcess && (

                  <div className="signal-item danger">

                    <AlertTriangle size={17} />

                    <span>
                      Actual expenditure exceeds
                      sanctioned amount
                    </span>

                  </div>

                )}


                {ucMissing && (

                  <div className="signal-item warning">

                    <FileWarning size={17} />

                    <span>
                      Utilization Certificate is missing
                    </span>

                  </div>

                )}


                {severeDelay && (

                  <div className="signal-item warning">

                    <Clock size={17} />

                    <span>
                      Project has significant completion delay
                    </span>

                  </div>

                )}


                {!expenditureExcess &&
                  !ucMissing &&
                  !severeDelay && (

                  <div className="signal-item">

                    <ClipboardCheck size={17} />

                    <span>
                      No major financial/status signal
                      detected by these checks
                    </span>

                  </div>

                )}

              </div>

            </div>


            {/* RECOMMENDED VERIFICATION */}

            <div className="verification-box">

              <h3>
                Recommended Verification
              </h3>

              <ul>

                {expenditureExcess && (

                  <li>
                    Verify expenditure against
                    sanctioned amount and supporting bills.
                  </li>

                )}

                {ucMissing && (

                  <li>
                    Obtain and verify the Utilization Certificate.
                  </li>

                )}

                {p.uc_available && (

                  <li>
                    Reconcile UC amount with recorded expenditure.
                  </li>

                )}

                {severeDelay && (

                  <li>
                    Verify project completion timeline and
                    documented reasons for delay.
                  </li>

                )}

                <li>
                  Review supporting documents and
                  implementation records.
                </li>

              </ul>

            </div>

          </section>


          {/* INVESTIGATION WORKFLOW */}

          <section className="panel investigation-panel">

            <div className="section-heading">

              <div>

                <h2>
                  Officer Investigation
                </h2>

                <p>
                  Record the verification outcome for this project.
                </p>

              </div>

              {investigationExists && (

                <span className="saved-indicator">
                  Saved in PostgreSQL
                </span>

              )}

            </div>


            {/* STATUS */}

            <div className="form-group">

              <label>
                Investigation Status
              </label>

              <select
                value={investigationStatus}
                onChange={(e) =>
                  setInvestigationStatus(
                    e.target.value
                  )
                }
              >

                <option value="NEW">
                  NEW
                </option>

                <option value="UNDER REVIEW">
                  UNDER REVIEW
                </option>

                <option value="VERIFIED">
                  VERIFIED
                </option>

                <option value="FALSE POSITIVE">
                  FALSE POSITIVE
                </option>

                <option value="ESCALATED">
                  ESCALATED
                </option>

                <option value="CLOSED">
                  CLOSED
                </option>

              </select>

            </div>


            {/* NOTE */}

            <div className="form-group">

              <label>
                Officer Notes
              </label>

              <textarea
                value={officerNote}
                onChange={(e) =>
                  setOfficerNote(e.target.value)
                }
                placeholder="Enter verification findings, document observations, reasons for escalation, or other investigation notes..."
                rows="6"
              />

            </div>


            {/* SAVE */}

            <div className="investigation-actions">

              <button
                className="save-button"
                onClick={saveInvestigation}
                disabled={savingInvestigation}
              >

                <Save size={18} />

                {savingInvestigation
                  ? "Saving..."
                  : "Save Investigation"}

              </button>


              {saveMessage && (

                <span
                  className={
                    saveMessage.includes("successfully")
                      ? "save-success"
                      : "save-error"
                  }
                >
                  {saveMessage}
                </span>

              )}

            </div>

          </section>

        </main>

      </div>

    );

  }


  // =====================================================
  // RISK DISTRIBUTION
  // =====================================================

  const riskData = [

    {
      name: "Critical",
      value: projects.filter(
        p => p.risk_level === "CRITICAL"
      ).length
    },

    {
      name: "High",
      value: projects.filter(
        p => p.risk_level === "HIGH"
      ).length
    },

    {
      name: "Medium",
      value: projects.filter(
        p => p.risk_level === "MEDIUM"
      ).length
    },

    {
      name: "Low",
      value: projects.filter(
        p => p.risk_level === "LOW"
      ).length
    }

  ];


  // =====================================================
  // DASHBOARD
  // =====================================================

  return (

    <div className="app">

      {/* HEADER */}

      <header className="topbar">

        <div className="brand">

          <Database size={24} />

          <span>
            SIH26102
          </span>

        </div>

        <span className="system-title">
          MPLADS Risk & Anomaly Detection System
        </span>

      </header>


      <main className="main-content">

        {/* TITLE */}

        <section className="page-title">

          <div>

            <div className="small-label">
              MONITORING DASHBOARD
            </div>

            <h1>
              MPLADS Project Intelligence
            </h1>

            <p>
              AI-assisted detection of anomalies,
              inefficiencies and high-risk patterns.
            </p>

          </div>

        </section>


        {/* KPI */}

        <section className="kpi-grid">


          <div className="kpi-card">

            <Database />

            <div>

              <span>
                Total Projects
              </span>

              <strong>
                {statistics.total_projects}
              </strong>

            </div>

          </div>


          <div className="kpi-card">

            <IndianRupee />

            <div>

              <span>
                Total Expenditure
              </span>

              <strong>
                ₹
                {Number(
                  statistics.total_expenditure
                ).toLocaleString("en-IN")}
              </strong>

            </div>

          </div>


          <div className="kpi-card">

            <AlertTriangle />

            <div>

              <span>
                High Risk
              </span>

              <strong>
                {statistics.high_risk}
              </strong>

            </div>

          </div>


          <div className="kpi-card">

            <AlertTriangle />

            <div>

              <span>
                Critical
              </span>

              <strong>
                {statistics.critical}
              </strong>

            </div>

          </div>

        </section>


        {/* CHART + SUMMARY */}

        <section className="dashboard-grid">


          <div className="panel">

            <h2>
              Risk Distribution
            </h2>

            <p className="panel-subtitle">
              Current project risk classification
            </p>

            <div className="chart-container">

              <ResponsiveContainer
                width="100%"
                height={300}
              >

                <PieChart>

                  <Pie
                    data={riskData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={105}
                    label
                  >

                    {riskData.map(
                      (_, index) => (

                        <Cell
                          key={index}
                        />

                      )
                    )}

                  </Pie>

                  <Tooltip />

                </PieChart>

              </ResponsiveContainer>

            </div>

          </div>


          <div className="panel">

            <h2>
              Monitoring Summary
            </h2>

            <p className="panel-subtitle">
              Key indicators requiring attention
            </p>


            <div className="summary-list">


              <div>

                <Clock />

                <span>
                  Delayed Projects
                </span>

                <strong>
                  {statistics.delayed_projects}
                </strong>

              </div>


              <div>

                <FileWarning />

                <span>
                  Missing UC
                </span>

                <strong>
                  {statistics.missing_uc}
                </strong>

              </div>


              <div>

                <AlertTriangle />

                <span>
                  High / Critical
                </span>

                <strong>
                  {statistics.high_risk}
                </strong>

              </div>

            </div>

          </div>

        </section>


        {/* INVESTIGATION QUEUE */}

        <section className="panel">

          <div className="panel-header">

            <div>

              <h2>
                Investigation Queue
              </h2>

              <p className="panel-subtitle">
                Projects requiring officer attention
              </p>

            </div>


            <div className="search-box">

              <Search size={18} />

              <input
                placeholder="Search project, state, district..."
                value={search}
                onChange={(e) =>
                  setSearch(e.target.value)
                }
              />

            </div>

          </div>


          <div className="table-wrapper">

            <table>

              <thead>

                <tr>

                  <th>
                    Project
                  </th>

                  <th>
                    Location
                  </th>

                  <th>
                    Risk
                  </th>

                  <th>
                    Score
                  </th>

                  <th>
                    Reason
                  </th>

                </tr>

              </thead>


              <tbody>

                {filteredProjects
                  .slice(0, 20)
                  .map(project => (

                    <tr
                      key={project.project_id}
                      onClick={() =>
                        openProject(
                          project.project_id
                        )
                      }
                      className="clickable-row"
                    >

                      <td>

                        <strong>
                          {project.project_id}
                        </strong>

                      </td>


                      <td>

                        <strong>
                          {project.state}
                        </strong>

                        <br />

                        <small>
                          {project.district}
                        </small>

                      </td>


                      <td>

                        <span
                          className={`risk-badge-small ${project.risk_level?.toLowerCase()}`}
                        >
                          {project.risk_level}
                        </span>

                      </td>


                      <td>

                        <strong>
                          {Number(
                            project.risk_score
                          ).toFixed(1)}
                        </strong>

                      </td>


                      <td>
                        {project.risk_explanation}
                      </td>

                    </tr>

                  ))}

              </tbody>

            </table>

          </div>

        </section>

      </main>

    </div>

  );

}


export default App;