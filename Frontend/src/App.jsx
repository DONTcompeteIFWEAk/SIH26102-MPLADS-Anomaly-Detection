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
  Save,
  ClipboardCheck,
  Brain,
  Scale,
  ShieldCheck,
} from "lucide-react";

import "./App.css";


const API_URL = "http://127.0.0.1:8000";


function App() {

  // =====================================================
  // STATE
  // =====================================================

  // Real MPLADS financial screening
  const [realFinancial, setRealFinancial] = useState([]);
  const [realFinancialStats, setRealFinancialStats] = useState(null);
  const [selectedRealRecord, setSelectedRealRecord] = useState(null);
  const [realRecordLoading, setRealRecordLoading] = useState(false);

  // Real MPLADS work-level hybrid screening
  const [realWork, setRealWork] = useState([]);
  const [realWorkStats, setRealWorkStats] = useState(null);
  const [selectedRealWork, setSelectedRealWork] = useState(null);
  const [realWorkLoading, setRealWorkLoading] = useState(false);

  // Real MPLADS work investigation
  const [workInvestigationStatus, setWorkInvestigationStatus] =
    useState("NEW");

  const [workOfficerNote, setWorkOfficerNote] =
    useState("");

  const [workInvestigationExists, setWorkInvestigationExists] =
    useState(false);

  const [savingWorkInvestigation, setSavingWorkInvestigation] =
    useState(false);

  const [workSaveMessage, setWorkSaveMessage] =
    useState("");

  const [workInvestigationQueue, setWorkInvestigationQueue] =
    useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState(null);

  // =====================================================
  // DERIVED REAL-DATA VIEW MODELS
  // =====================================================
  // These values are derived only from real backend responses.
  // No synthetic project data is used in the production dashboard.
  const realRiskData = [
    { name: "CRITICAL", value: Number(realFinancialStats?.risk_distribution?.CRITICAL || 0) },
    { name: "HIGH", value: Number(realFinancialStats?.risk_distribution?.HIGH || 0) },
    { name: "MEDIUM", value: Number(realFinancialStats?.risk_distribution?.MEDIUM || 0) },
    { name: "LOW", value: Number(realFinancialStats?.risk_distribution?.LOW || 0) },
  ];

  const realTopRecords = [...realFinancial]
    .sort((a, b) => Number(b.financial_rule_score || 0) - Number(a.financial_rule_score || 0))
    .slice(0, 10);

  const realTopWorks = realWork.slice(0, 10);


  // =====================================================
  // LOAD DASHBOARD DATA
  // =====================================================

  useEffect(() => {

    async function loadData() {
      try {
        setLoading(true);

        const [
          realFinancialResponse,
          realFinancialStatsResponse,
          realWorkResponse,
          realWorkStatsResponse,
          workInvestigationQueueResponse
        ] = await Promise.all([
          axios.get(`${API_URL}/real-financial`),
          axios.get(`${API_URL}/real-financial/statistics`),
          axios.get(`${API_URL}/real-work/high-risk?limit=100&offset=0`),
          axios.get(`${API_URL}/real-work/statistics`),
          axios.get(`${API_URL}/work-investigations/queue`)
        ]);

        setRealFinancial(realFinancialResponse.data);
        setRealFinancialStats(realFinancialStatsResponse.data);
        setRealWork(realWorkResponse.data);
        setRealWorkStats(realWorkStatsResponse.data);
        setWorkInvestigationQueue(
          Array.isArray(workInvestigationQueueResponse.data)
            ? workInvestigationQueueResponse.data
            : []
        );
        setError(null);
      } catch (err) {
        console.error(err);
        setError(
          "Unable to connect to the SIH26102 real MPLADS screening backend."
        );
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  // =====================================================
  // LOAD REAL MPLADS RECORD
  // =====================================================

  async function openRealRecord(projectId) {
    try {
      setRealRecordLoading(true);

      const response = await axios.get(
        `${API_URL}/real-financial/${projectId}`
      );

      const record = response.data?.data || response.data;

      if (!record || !record.project_id) {
        throw new Error("Invalid real MPLADS record returned by backend.");
      }

      setSelectedRealRecord(record);
    } catch (err) {
      console.error("Real MPLADS record loading failed:", err);
      alert(
        err?.response?.data?.detail ||
        "Unable to load real MPLADS record. Check that FastAPI is running and the /real-financial/{project_id} endpoint is available."
      );
    } finally {
      setRealRecordLoading(false);
    }
  }

  // =====================================================
  // LOAD REAL MPLADS WORK RECORD
  // =====================================================

  async function openRealWork(workId) {
    try {
      setRealWorkLoading(true);
      setWorkSaveMessage("");

      const response = await axios.get(
        `${API_URL}/real-work/${encodeURIComponent(workId)}`
      );

      const record = response.data?.data || response.data;

      if (!record || !record.work_id) {
        throw new Error("Invalid real MPLADS work record returned by backend.");
      }

      setSelectedRealWork(record);

      // Reset work investigation form.
      setWorkInvestigationStatus("NEW");
      setWorkOfficerNote("");
      setWorkInvestigationExists(false);

      // Load an existing investigation if one already exists.
      try {
        const investigationResponse = await axios.get(
          `${API_URL}/work-investigations/${encodeURIComponent(workId)}`
        );

        setWorkInvestigationStatus(
          investigationResponse.data.status || "NEW"
        );

        setWorkOfficerNote(
          investigationResponse.data.officer_note || ""
        );

        setWorkInvestigationExists(true);
      } catch (investigationError) {
        if (
          investigationError.response &&
          investigationError.response.status !== 404
        ) {
          console.error(
            "Work investigation loading error:",
            investigationError
          );
        }
      }
    } catch (err) {
      console.error("Real MPLADS work loading failed:", err);
      alert(
        err?.response?.data?.detail ||
        "Unable to load real MPLADS work record."
      );
    } finally {
      setRealWorkLoading(false);
    }
  }


  // =====================================================
  // START WORK INVESTIGATION
  // =====================================================

  async function startWorkInvestigation() {
    if (!selectedRealWork?.work_id) {
      return;
    }

    try {
      setSavingWorkInvestigation(true);
      setWorkSaveMessage("");

      const response = await axios.post(
        `${API_URL}/work-investigations/${encodeURIComponent(
          selectedRealWork.work_id
        )}`
      );

      setWorkInvestigationStatus(
        response.data.status || "NEW"
      );
      setWorkOfficerNote(
        response.data.officer_note || ""
      );
      setWorkInvestigationExists(true);
      setWorkSaveMessage(
        "Investigation started successfully."
      );

      await refreshWorkInvestigationQueue();
    } catch (err) {
      console.error("Starting work investigation failed:", err);
      setWorkSaveMessage(
        err?.response?.data?.detail ||
        "Failed to start investigation."
      );
    } finally {
      setSavingWorkInvestigation(false);
    }
  }


  // =====================================================
  // REFRESH WORK INVESTIGATION QUEUE
  // =====================================================

  async function refreshWorkInvestigationQueue() {
    try {
      const response = await axios.get(
        `${API_URL}/work-investigations/queue`
      );

      setWorkInvestigationQueue(
        Array.isArray(response.data) ? response.data : []
      );
    } catch (err) {
      console.error(
        "Work investigation queue loading failed:",
        err
      );
    }
  }


  // =====================================================
  // SAVE WORK INVESTIGATION
  // =====================================================

  async function saveWorkInvestigation() {
    if (!selectedRealWork?.work_id) {
      return;
    }

    try {
      setSavingWorkInvestigation(true);
      setWorkSaveMessage("");

      // PUT also creates the record if it does not exist, but the UI
      // normally creates it first with the Start Investigation button.
      const response = await axios.put(
        `${API_URL}/work-investigations/${encodeURIComponent(
          selectedRealWork.work_id
        )}`,
        {
          status: workInvestigationStatus,
          officer_note: workOfficerNote
        }
      );

      setWorkInvestigationStatus(
        response.data.status || workInvestigationStatus
      );
      setWorkOfficerNote(
        response.data.officer_note ?? workOfficerNote
      );
      setWorkInvestigationExists(true);
      setWorkSaveMessage(
        "Investigation saved successfully."
      );

      await refreshWorkInvestigationQueue();
    } catch (err) {
      console.error("Saving work investigation failed:", err);
      setWorkSaveMessage(
        err?.response?.data?.detail ||
        "Failed to save investigation."
      );
    } finally {
      setSavingWorkInvestigation(false);
    }
  }


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

        {/* REAL-DATA DASHBOARD HEADER */}
        <section className="page-title">
          <div>
            <div className="small-label">REAL MPLADS MONITORING</div>
            <h1>MPLADS Risk & Screening Intelligence</h1>
            <p>
              AI-assisted screening of real MPLADS work and aggregate financial
              records for anomalies, inefficiencies and high-risk patterns.
            </p>
          </div>
        </section>

        <section className="panel verification-box" style={{ marginBottom: "18px" }}>
          <div style={{ display: "flex", gap: "10px", alignItems: "flex-start" }}>
            <ShieldCheck size={20} />
            <div>
              <strong>Production data view</strong>
              <p className="panel-subtitle" style={{ marginBottom: 0 }}>
                The dashboard below uses real MPLADS records. Synthetic development
                data is not displayed in the application. Screening results are
                risk indicators for human verification and do not establish fraud.
              </p>
            </div>
          </div>
        </section>

        {/* =====================================================
            REAL MPLADS WORK-LEVEL SCREENING
            ===================================================== */}

        <section className="panel real-financial-panel">
          <div className="panel-header">
            <div>
              <div className="small-label">REAL WORK-LEVEL DATA</div>
              <h2>Real MPLADS Work Screening</h2>
              <p className="panel-subtitle">
                Hybrid ML and behavioral-rule screening of real MPLADS
                work records for patterns requiring verification.
              </p>
            </div>

            <div className="hybrid-weight-badge">
              {realWorkStats?.total_records || 0} Works
            </div>
          </div>

          {realWorkStats && (
            <>
              <div className="kpi-grid real-financial-kpis">
                <div className="kpi-card">
                  <Database />
                  <div>
                    <span>Real Works</span>
                    <strong>{realWorkStats.total_records}</strong>
                  </div>
                </div>

                <div className="kpi-card">
                  <AlertTriangle />
                  <div>
                    <span>Screening Flags</span>
                    <strong>{realWorkStats.flagged_records}</strong>
                  </div>
                </div>

                <div className="kpi-card">
                  <Brain />
                  <div>
                    <span>Medium or Above</span>
                    <strong>{realWorkStats.medium_or_above_records}</strong>
                  </div>
                </div>

                <div className="kpi-card">
                  <ShieldCheck />
                  <div>
                    <span>Data Quality Avg.</span>
                    <strong>
                      {realWorkStats.data_quality?.average_score ?? "—"}
                    </strong>
                  </div>
                </div>
              </div>

              <div className="dashboard-grid">
                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <div className="small-label">RISK DISTRIBUTION</div>
                      <h3>Hybrid Risk Levels</h3>
                    </div>
                  </div>

                  <div className="summary-list">
                    {["CRITICAL", "HIGH", "MEDIUM", "LOW"].map((level) => (
                      <div key={level}>
                        <span>{level}</span>
                        <strong>
                          {realWorkStats.risk_distribution?.[level] || 0}
                        </strong>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <div className="small-label">BEHAVIORAL SIGNALS</div>
                      <h3>Screening Indicators</h3>
                    </div>
                  </div>

                  <div className="summary-list">
                    <div>
                      <span>High state allocation</span>
                      <strong>
                        {realWorkStats.signal_counts?.high_state_allocation || 0}
                      </strong>
                    </div>
                    <div>
                      <span>High constituency allocation</span>
                      <strong>
                        {realWorkStats.signal_counts?.high_constituency_allocation || 0}
                      </strong>
                    </div>
                    <div>
                      <span>High category allocation</span>
                      <strong>
                        {realWorkStats.signal_counts?.high_category_allocation || 0}
                      </strong>
                    </div>
                    <div>
                      <span>Repeated description</span>
                      <strong>
                        {realWorkStats.signal_counts?.repeated_description || 0}
                      </strong>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

          <div className="panel-header" style={{ marginTop: "24px" }}>
            <div>
              <div className="small-label">PRIORITIZED RECORDS</div>
              <h3>Highest-Risk Work Records</h3>
              <p className="panel-subtitle">
                Records prioritized by the hybrid screening score.
              </p>
            </div>

            <div className="hybrid-weight-badge">
              ML 60% + Rules 40%
            </div>
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Work ID</th>
                  <th>State</th>
                  <th>Constituency</th>
                  <th>Allocation</th>
                  <th>Score</th>
                  <th>Level</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {realTopWorks.map((work) => (
                  <tr key={work.work_id}>
                    <td><strong>{work.work_id}</strong></td>
                    <td>{work.state || "—"}</td>
                    <td>{work.constituency || "—"}</td>
                    <td>
                      ₹{Number(work.allocation_amount || 0).toLocaleString("en-IN")}
                    </td>
                    <td>
                      <strong>
                        {Number(work.hybrid_risk_score || 0).toFixed(2)}
                      </strong>
                    </td>
                    <td>
                      <span
                        className={`risk-badge-small ${
                          work.hybrid_risk_level?.toLowerCase() || ""
                        }`}
                      >
                        {work.hybrid_risk_level || "—"}
                      </span>
                    </td>
                    <td>
                      <button
                        type="button"
                        className="real-view-button"
                        disabled={realWorkLoading}
                        onClick={() => openRealWork(work.work_id)}
                      >
                        {realWorkLoading ? "Loading..." : "View details"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {selectedRealWork && !realWorkLoading && (
            <section className="real-record-detail">
              <div className="real-record-header">
                <div>
                  <div className="small-label">REAL MPLADS WORK</div>
                  <h3>{selectedRealWork.work_id}</h3>
                  <p>
                    {selectedRealWork.state || "State not available"}
                    {" • "}
                    {selectedRealWork.constituency || "Constituency not available"}
                  </p>
                </div>

                <button
                  className="real-record-close"
                  type="button"
                  onClick={() => setSelectedRealWork(null)}
                >
                  Close
                </button>
              </div>

              <div className="real-detail-grid">
                <div className="real-detail-card">
                  <h4>Work</h4>
                  <div className="detail-row">
                    <span>Description</span>
                    <strong>{selectedRealWork.work || "Not available"}</strong>
                  </div>
                  <div className="detail-row">
                    <span>Category</span>
                    <strong>{selectedRealWork.category || "Not available"}</strong>
                  </div>
                  <div className="detail-row">
                    <span>Status</span>
                    <strong>{selectedRealWork.status || "Not available"}</strong>
                  </div>
                </div>

                <div className="real-detail-card">
                  <h4>Allocation</h4>
                  <div className="detail-row">
                    <span>Allocation Amount</span>
                    <strong>
                      ₹{Number(selectedRealWork.allocation_amount || 0).toLocaleString("en-IN")}
                    </strong>
                  </div>
                  <div className="detail-row">
                    <span>State Median Ratio</span>
                    <strong>
                      {Number(selectedRealWork.allocation_vs_state_median || 0).toFixed(2)}x
                    </strong>
                  </div>
                  <div className="detail-row">
                    <span>Constituency Median Ratio</span>
                    <strong>
                      {Number(selectedRealWork.allocation_vs_constituency_median || 0).toFixed(2)}x
                    </strong>
                  </div>
                  <div className="detail-row">
                    <span>Category Median Ratio</span>
                    <strong>
                      {Number(selectedRealWork.allocation_vs_category_median || 0).toFixed(2)}x
                    </strong>
                  </div>
                </div>

                <div className="real-detail-card">
                  <h4>Hybrid Risk</h4>
                  <div className="detail-row">
                    <span>ML Risk</span>
                    <strong>
                      {Number(selectedRealWork.real_ml_risk_score || 0).toFixed(2)}
                    </strong>
                  </div>
                  <div className="detail-row">
                    <span>Rule Score</span>
                    <strong>
                      {Number(selectedRealWork.work_rule_score || 0).toFixed(2)}
                    </strong>
                  </div>
                  <div className="detail-row">
                    <span>Hybrid Score</span>
                    <strong>
                      {Number(selectedRealWork.hybrid_risk_score || 0).toFixed(2)}
                    </strong>
                  </div>
                  <div className="detail-row">
                    <span>Risk Level</span>
                    <strong>{selectedRealWork.hybrid_risk_level || "Not available"}</strong>
                  </div>
                </div>

                <div className="real-detail-card">
                  <h4>Behavioral Signals</h4>
                  <div className="detail-row">
                    <span>High State Allocation</span>
                    <strong>
                      {selectedRealWork.rule_high_state_allocation ? "Yes" : "No"}
                    </strong>
                  </div>
                  <div className="detail-row">
                    <span>High Constituency Allocation</span>
                    <strong>
                      {selectedRealWork.rule_high_constituency_allocation ? "Yes" : "No"}
                    </strong>
                  </div>
                  <div className="detail-row">
                    <span>High Category Allocation</span>
                    <strong>
                      {selectedRealWork.rule_high_category_allocation ? "Yes" : "No"}
                    </strong>
                  </div>
                  <div className="detail-row">
                    <span>Repeated Description</span>
                    <strong>
                      {selectedRealWork.rule_repeated_description ? "Yes" : "No"}
                    </strong>
                  </div>
                </div>

                <div className="real-detail-card">
                  <h4>Review</h4>
                  <div className="detail-row">
                    <span>Recommended Action</span>
                    <strong>{selectedRealWork.recommended_action || "Not available"}</strong>
                  </div>
                  <div className="detail-row">
                    <span>Data Quality</span>
                    <strong>{selectedRealWork.data_quality_score ?? "Not available"}</strong>
                  </div>
                  <div className="detail-row">
                    <span>Data source</span>
                    <strong>Real MPLADS work record</strong>
                  </div>
                </div>

                <div className="real-detail-card">
                  <h4>Administrative Information</h4>
                  <div className="detail-row">
                    <span>MP Name</span>
                    <strong>{selectedRealWork.mp_name || "Not available"}</strong>
                  </div>
                  <div className="detail-row">
                    <span>IDA</span>
                    <strong>{selectedRealWork.ida || "Not available"}</strong>
                  </div>
                  <div className="detail-row">
                    <span>Recommended Date</span>
                    <strong>{selectedRealWork.recommended_date || "Not available"}</strong>
                  </div>
                </div>
              </div>

              {/* =====================================================
                  WORK INVESTIGATION
                  ===================================================== */}

              <section className="panel investigation-panel" style={{ marginTop: "18px" }}>
                <div className="section-heading">
                  <div>
                    <h2>Officer Investigation</h2>
                    <p>Record the verification outcome for this work.</p>
                  </div>

                  {workInvestigationExists && (
                    <span className="saved-indicator">
                      Saved in PostgreSQL
                    </span>
                  )}
                </div>

                {!workInvestigationExists ? (
                  <div>
                    <p className="panel-subtitle">
                      This work has been prioritized by the screening system.
                      Start an investigation to record an officer review.
                    </p>

                    <button
                      type="button"
                      className="save-button"
                      onClick={startWorkInvestigation}
                      disabled={savingWorkInvestigation}
                    >
                      <ClipboardCheck size={18} />
                      {savingWorkInvestigation
                        ? "Starting..."
                        : "Start Investigation"}
                    </button>
                  </div>
                ) : (
                  <>
                    <div className="form-group">
                      <label>Investigation Status</label>
                      <select
                        value={workInvestigationStatus}
                        onChange={(e) =>
                          setWorkInvestigationStatus(e.target.value)
                        }
                      >
                        <option value="NEW">NEW</option>
                        <option value="UNDER REVIEW">UNDER REVIEW</option>
                        <option value="VERIFIED">VERIFIED</option>
                        <option value="FALSE POSITIVE">FALSE POSITIVE</option>
                        <option value="ESCALATED">ESCALATED</option>
                        <option value="CLOSED">CLOSED</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label>Officer Notes</label>
                      <textarea
                        value={workOfficerNote}
                        onChange={(e) => setWorkOfficerNote(e.target.value)}
                        placeholder="Enter verification findings, document observations, reasons for escalation, or other investigation notes..."
                        rows="6"
                      />
                    </div>

                    <div className="investigation-actions">
                      <button
                        type="button"
                        className="save-button"
                        onClick={saveWorkInvestigation}
                        disabled={savingWorkInvestigation}
                      >
                        <Save size={18} />
                        {savingWorkInvestigation
                          ? "Saving..."
                          : "Save Investigation"}
                      </button>

                      {workSaveMessage && (
                        <span
                          className={
                            workSaveMessage.includes("successfully")
                              ? "save-success"
                              : "save-error"
                          }
                        >
                          {workSaveMessage}
                        </span>
                      )}
                    </div>
                  </>
                )}
              </section>

              <div className="verification-box" style={{ marginTop: "18px" }}>
                <strong>Verification notice:</strong>{" "}
                This is an automated screening signal from real MPLADS work
                data. It is not a confirmed fraud finding and requires
                human/audit verification.
              </div>
            </section>
          )}

          {realWorkLoading && (
            <div className="real-record-detail">
              <div className="small-label">LOADING WORK</div>
              <h3>Fetching real MPLADS work record...</h3>
              <p className="panel-subtitle">
                Loading the selected work from the FastAPI backend.
              </p>
            </div>
          )}

          {/* =====================================================
              WORK INVESTIGATION QUEUE
              ===================================================== */}

          <div className="panel" style={{ marginTop: "24px" }}>
            <div className="panel-header">
              <div>
                <div className="small-label">INVESTIGATION QUEUE</div>
                <h3>Officer Review Queue</h3>
                <p className="panel-subtitle">
                  Work records that have been opened for human verification.
                </p>
              </div>

              <div className="hybrid-weight-badge">
                {workInvestigationQueue.length} Cases
              </div>
            </div>

            {workInvestigationQueue.length === 0 ? (
              <div className="verification-box">
                No work investigations have been started yet.
              </div>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Work ID</th>
                      <th>Status</th>
                      <th>Officer Note</th>
                      <th>Updated</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {workInvestigationQueue.map((item) => (
                      <tr key={item.id || item.work_id}>
                        <td><strong>{item.work_id}</strong></td>
                        <td>
                          <span className="risk-badge-small">
                            {item.status || "NEW"}
                          </span>
                        </td>
                        <td>
                          {item.officer_note || "No note added"}
                        </td>
                        <td>
                          {item.updated_at
                            ? new Date(item.updated_at).toLocaleString("en-IN")
                            : "—"}
                        </td>
                        <td>
                          <button
                            type="button"
                            className="real-view-button"
                            onClick={() => openRealWork(item.work_id)}
                          >
                            Open work
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>


        {/* =====================================================
            REAL MPLADS FINANCIAL SCREENING
            ===================================================== */}

        <section className="panel real-financial-panel">

          <div className="panel-header">

            <div>

              <div className="small-label">
                REAL PUBLIC DATA
              </div>

              <h2>
                Real MPLADS Financial Screening
              </h2>

              <p className="panel-subtitle">
                Screening of publicly available MPLADS aggregate
                financial records for patterns requiring verification.
              </p>

            </div>

            <div className="hybrid-weight-badge">
              {realFinancialStats?.total_records || 0} Records
            </div>

          </div>


          {realFinancialStats && (

            <div className="kpi-grid real-financial-kpis">

              <div className="kpi-card">
                <Database />
                <div>
                  <span>Real Records</span>
                  <strong>{realFinancialStats.total_records}</strong>
                </div>
              </div>

              <div className="kpi-card">
                <AlertTriangle />
                <div>
                  <span>High Risk</span>
                  <strong>{realFinancialStats.high_risk_records}</strong>
                </div>
              </div>

              <div className="kpi-card">
                <FileWarning />
                <div>
                  <span>Excess Expenditure</span>
                  <strong>
                    {realFinancialStats.signal_counts.signal_excess_expenditure || 0}
                  </strong>
                </div>
              </div>

              <div className="kpi-card">
                <IndianRupee />
                <div>
                  <span>High Unspent Balance</span>
                  <strong>
                    {realFinancialStats.signal_counts.signal_high_unspent_balance || 0}
                  </strong>
                </div>
              </div>

            </div>

          )}


          {realFinancialStats && (

            <div className="dashboard-grid">

              <div className="panel">

                <h3>Financial Risk Distribution</h3>

                <p className="panel-subtitle">
                  Screening classification across real records
                </p>

                <div className="chart-container">

                  <ResponsiveContainer width="100%" height={280}>

                    <PieChart>

                      <Pie
                        data={realRiskData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={95}
                        label
                      >

                        {realRiskData.map((_, index) => (
                          <Cell key={index} />
                        ))}

                      </Pie>

                      <Tooltip />

                    </PieChart>

                  </ResponsiveContainer>

                </div>

              </div>


              <div className="panel">

                <h3>Screening Signals</h3>

                <p className="panel-subtitle">
                  Patterns requiring contextual verification
                </p>

                <div className="summary-list">

                  <div>
                    <AlertTriangle />
                    <span>Sanction Gap</span>
                    <strong>
                      {realFinancialStats.signal_counts.signal_sanction_gap || 0}
                    </strong>
                  </div>

                  <div>
                    <FileWarning />
                    <span>High Unspent Balance</span>
                    <strong>
                      {realFinancialStats.signal_counts.signal_high_unspent_balance || 0}
                    </strong>
                  </div>

                  <div>
                    <IndianRupee />
                    <span>Excess Expenditure</span>
                    <strong>
                      {realFinancialStats.signal_counts.signal_excess_expenditure || 0}
                    </strong>
                  </div>

                  <div>
                    <AlertTriangle />
                    <span>Above Available Funds</span>
                    <strong>
                      {realFinancialStats.signal_counts.signal_expenditure_above_available || 0}
                    </strong>
                  </div>

                </div>

              </div>

            </div>

          )}


          <div className="panel">

            <div className="panel-header">

              <div>
                <h3>Highest Financial Screening Scores</h3>
                <p className="panel-subtitle">
                  Real records prioritized for verification
                </p>
              </div>

            </div>

            <div className="table-wrapper">

              <table>

                <thead>
                  <tr>
                    <th>Record</th>
                    <th>MP</th>
                    <th>Constituency</th>
                    <th>Score</th>
                    <th>Level</th>
                    <th>Explanation</th>
                  </tr>
                </thead>

                <tbody>

                  {realTopRecords.map(record => (

                    <tr
                      key={record.project_id}
                      className="clickable-row"
                      onClick={() => openRealRecord(record.project_id)}
                      title="Click to open real MPLADS record details"
                    >

                      <td>
                        <strong>{record.project_id}</strong>
                        <br />
                        <button
                          type="button"
                          className="real-view-button"
                          onClick={(event) => {
                            event.stopPropagation();
                            openRealRecord(record.project_id);
                          }}
                        >
                          View details
                        </button>
                      </td>

                      <td>{record.mp_name}</td>

                      <td>{record.constituency}</td>

                      <td>
                        <strong>
                          {Number(record.financial_rule_score || 0).toFixed(0)}
                        </strong>
                      </td>

                      <td>
                        <span
                          className={`risk-badge-small ${
                            record.financial_risk_level?.toLowerCase()
                          }`}
                        >
                          {record.financial_risk_level}
                        </span>
                      </td>

                      <td>{record.financial_explanation}</td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          </div>

          {/* =====================================================
              REAL MPLADS RECORD DETAIL
              ===================================================== */}

          {realRecordLoading && (
            <div className="real-record-detail">
              <div className="small-label">LOADING RECORD</div>
              <h3>Fetching real MPLADS financial record...</h3>
              <p className="panel-subtitle">
                Loading the selected record from the FastAPI backend.
              </p>
            </div>
          )}

          {selectedRealRecord && !realRecordLoading && (
            <section className="real-record-detail">

              <div className="real-record-header">
                <div>
                  <div className="small-label">
                    REAL MPLADS RECORD
                  </div>

                  <h3>
                    {selectedRealRecord.project_id}
                  </h3>

                  <p>
                    {selectedRealRecord.mp_name || "MP not available"}
                    {" • "}
                    {selectedRealRecord.constituency || "Constituency not available"}
                  </p>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span
                    className={`risk-badge-small ${
                      selectedRealRecord.financial_risk_level?.toLowerCase()
                    }`}
                  >
                    {selectedRealRecord.financial_risk_level || "LOW"}
                  </span>

                  <button
                    className="real-record-close"
                    onClick={() => setSelectedRealRecord(null)}
                  >
                    Close
                  </button>
                </div>
              </div>

              <div className="real-detail-grid">

                <div className="real-detail-card">
                  <h4>Identity</h4>

                  <div className="detail-row">
                    <span>MP Name</span>
                    <strong>{selectedRealRecord.mp_name || "Not available"}</strong>
                  </div>

                  <div className="detail-row">
                    <span>Constituency</span>
                    <strong>{selectedRealRecord.constituency || "Not available"}</strong>
                  </div>

                  <div className="detail-row">
                    <span>Data Source</span>
                    <strong>{selectedRealRecord.data_source || "REAL_MPLADS"}</strong>
                  </div>
                </div>

                <div className="real-detail-card">
                  <h4>Financial Position</h4>

                  <div className="detail-row">
                    <span>Entitlement</span>
                    <strong>{formatValue(selectedRealRecord.entitlement)}</strong>
                  </div>

                  <div className="detail-row">
                    <span>Funds Received</span>
                    <strong>{formatValue(selectedRealRecord.fund_received)}</strong>
                  </div>

                  <div className="detail-row">
                    <span>Amount Available</span>
                    <strong>{formatValue(selectedRealRecord.amount_available)}</strong>
                  </div>

                  <div className="detail-row">
                    <span>Unspent Balance</span>
                    <strong>{formatValue(selectedRealRecord.unspent_balance)}</strong>
                  </div>
                </div>

                <div className="real-detail-card">
                  <h4>Works & Expenditure</h4>

                  <div className="detail-row">
                    <span>Recommended Cost</span>
                    <strong>{formatValue(selectedRealRecord.works_recommended_cost)}</strong>
                  </div>

                  <div className="detail-row">
                    <span>Sanctioned Cost</span>
                    <strong>{formatValue(selectedRealRecord.work_sanctioned_cost)}</strong>
                  </div>

                  <div className="detail-row">
                    <span>Actual Expenditure</span>
                    <strong>{formatValue(selectedRealRecord.actual_expenditure)}</strong>
                  </div>

                  <div className="detail-row">
                    <span>Expenditure / Sanction</span>
                    <strong>
                      {formatValue(
                        selectedRealRecord.expenditure_to_sanction_ratio,
                        3
                      )}x
                    </strong>
                  </div>
                </div>

                <div className="real-detail-card">
                  <h4>Screening</h4>

                  <div className="detail-row">
                    <span>Screening Score</span>
                    <strong>
                      {formatValue(selectedRealRecord.financial_rule_score, 0)}
                    </strong>
                  </div>

                  <div className="detail-row">
                    <span>Risk Level</span>
                    <strong>
                      {selectedRealRecord.financial_risk_level || "LOW"}
                    </strong>
                  </div>

                  <div className="detail-row">
                    <span>Ground Truth</span>
                    <strong>
                      {selectedRealRecord.ground_truth_available ? "Available" : "Not available"}
                    </strong>
                  </div>
                </div>

              </div>

              <div className="real-record-signals">
                <h4>Detected Screening Signals</h4>

                <div className="signal-list">
                  {activeRealSignals(selectedRealRecord).length > 0 ? (
                    activeRealSignals(selectedRealRecord).map((signal, index) => {
                      const Icon = signal.icon;

                      return (
                        <div
                          className={`signal-item ${signal.type}`}
                          key={index}
                        >
                          <Icon size={17} />
                          <span>{signal.text}</span>
                        </div>
                      );
                    })
                  ) : (
                    <div className="signal-item">
                      <ClipboardCheck size={17} />
                      <span>
                        No configured financial screening signal is active for this record.
                      </span>
                    </div>
                  )}
                </div>
              </div>

              <div className="verification-box">
                <h3>Recommended Verification</h3>

                <ul>
                  <li>
                    Review the source financial records supporting the reported values.
                  </li>

                  {selectedRealRecord.signal_excess_expenditure && (
                    <li>
                      Reconcile actual expenditure with the sanctioned cost and supporting bills.
                    </li>
                  )}

                  {selectedRealRecord.signal_expenditure_above_available && (
                    <li>
                      Reconcile expenditure with reported funds available and fund-flow records.
                    </li>
                  )}

                  {selectedRealRecord.signal_sanction_gap && (
                    <li>
                      Review recommendation and sanction documentation for the observed cost gap.
                    </li>
                  )}

                  {selectedRealRecord.signal_high_unspent_balance && (
                    <li>
                      Verify the treatment, current status and reconciliation of the unspent balance.
                    </li>
                  )}
                </ul>
              </div>

              <div className="dashboard-disclaimer">
                <AlertTriangle size={16} />
                <span>
                  This is a screening view of aggregate public MPLADS financial data.
                  Signals indicate patterns requiring verification and do not establish
                  fraud, wrongdoing, or an audit finding.
                </span>
              </div>

            </section>
          )}


          <div className="dashboard-disclaimer">

            <AlertTriangle size={16} />

            <span>
              Real MPLADS records are aggregate financial data.
              Screening signals identify patterns that may require
              verification; they do not establish fraud, wrongdoing,
              or an audit finding.
            </span>

          </div>

        </section>


        {/* DISCLAIMER */}

        <div className="dashboard-disclaimer">

          <AlertTriangle size={16} />

          <span>
            Risk scores indicate potential anomalies or
            high-risk patterns requiring verification.
            They do not by themselves establish fraud or
            wrongdoing.
          </span>

        </div>

      </main>

    </div>

  );

}


export default App;