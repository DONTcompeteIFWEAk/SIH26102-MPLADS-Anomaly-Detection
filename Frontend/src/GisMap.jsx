import React, { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import {
  ShieldAlert, AlertTriangle, IndianRupee, MapPin,
  ExternalLink, Layers, RefreshCw, ZoomIn, ZoomOut, Compass, Info
} from "lucide-react";

export default function GisMap({ stateData = [], onSelectStateForExplorer }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersGroupRef = useRef(null);

  const [activeMetric, setActiveMetric] = useState("flagged"); // "flagged", "tenders", "allocation"
  const [mapTheme, setMapTheme] = useState("dark"); // "dark", "streets"
  const [selectedState, setSelectedState] = useState(null);

  // Default to first state (e.g., Uttar Pradesh) as selected initially
  useEffect(() => {
    if (stateData && stateData.length > 0 && !selectedState) {
      setSelectedState(stateData[0]);
    }
  }, [stateData]);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (mapInstanceRef.current) return;

    // India geographic center
    const map = L.map(mapContainerRef.current, {
      center: [22.8, 80.0],
      zoom: 4.8,
      minZoom: 4,
      maxZoom: 10,
      zoomControl: false,
      attributionControl: false
    });

    // Helper to get reliable, watermark-free tiles with zero API key requirement
    const getTileUrl = (theme) => {
      if (theme === "streets") {
        return "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
      }
      if (theme === "satellite") {
        return "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
      }
      // Default: Esri World Dark Gray Base (Clean, high-performance dark theme, ZERO API key needed)
      return "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}";
    };

    const tileLayer = L.tileLayer(getTileUrl(mapTheme), {
      maxZoom: 19,
      attribution: "Map data &copy; OpenStreetMap contributors, Esri"
    }).addTo(map);

    map.tileLayerInstance = tileLayer;

    // Layer group for circle markers
    const markersGroup = L.layerGroup().addTo(map);
    markersGroupRef.current = markersGroup;
    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update Tile Layer on Theme Change
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !map.tileLayerInstance) return;

    map.removeLayer(map.tileLayerInstance);

    const getTileUrl = (theme) => {
      if (theme === "streets") {
        return "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
      }
      if (theme === "satellite") {
        return "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
      }
      return "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}";
    };

    const newTileLayer = L.tileLayer(getTileUrl(mapTheme), {
      maxZoom: 19,
      attribution: "Map data &copy; OpenStreetMap contributors, Esri"
    }).addTo(map);

    map.tileLayerInstance = newTileLayer;
  }, [mapTheme]);

  // Render State Markers
  useEffect(() => {
    const map = mapInstanceRef.current;
    const markersGroup = markersGroupRef.current;
    if (!map || !markersGroup || !stateData || stateData.length === 0) return;

    markersGroup.clearLayers();

    stateData.forEach((state) => {
      if (!state.lat || !state.lng) return;

      // Determine radius and color based on activeMetric
      let radius = 12;
      let fillColor = "#38bdf8";
      let strokeColor = "#0284c7";

      if (activeMetric === "flagged") {
        radius = Math.max(10, Math.min(32, Math.sqrt(state.flagged_works || 0) * 1.5 + 8));
        if (state.critical_works > 10) {
          fillColor = "#ef4444";
          strokeColor = "#b91c1c";
        } else if (state.flagged_works > 100) {
          fillColor = "#f97316";
          strokeColor = "#c2410c";
        } else if (state.flagged_works > 30) {
          fillColor = "#f59e0b";
          strokeColor = "#b45309";
        } else {
          fillColor = "#10b981";
          strokeColor = "#047857";
        }
      } else if (activeMetric === "tenders") {
        radius = Math.max(10, Math.min(32, Math.sqrt(state.split_tenders || 0) * 1.2 + 8));
        fillColor = (state.split_tenders || 0) > 200 ? "#ec4899" : "#a855f7";
        strokeColor = "#7e22ce";
      } else if (activeMetric === "allocation") {
        radius = Math.max(10, Math.min(32, Math.sqrt(state.total_allocation_cr || 0) * 1.0 + 8));
        fillColor = "#3b82f6";
        strokeColor = "#1d4ed8";
      }

      // Outer glow circle
      const halo = L.circleMarker([state.lat, state.lng], {
        radius: radius + 6,
        color: fillColor,
        weight: 1,
        opacity: 0.35,
        fillColor: fillColor,
        fillOpacity: 0.12
      });

      // Core interactive circle marker
      const marker = L.circleMarker([state.lat, state.lng], {
        radius,
        color: strokeColor,
        weight: 2,
        opacity: 0.9,
        fillColor,
        fillOpacity: 0.75
      });

      // HTML Tooltip Card
      const tooltipContent = `
        <div style="font-family: 'Plus Jakarta Sans', sans-serif; min-width: 210px; color: #0f172a; padding: 4px;">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; margin-bottom: 8px;">
            <strong style="font-size: 14px; color: #0f172a;">${state.state}</strong>
            <span style="font-size: 10px; background: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 4px; font-weight: 700;">${state.zone || "State"}</span>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 12px; margin-bottom: 8px;">
            <div>
              <span style="color: #64748b; font-size: 10px; display: block;">FLAGGED WORKS</span>
              <strong style="color: #ef4444; font-size: 14px;">${Number(state.flagged_works || 0).toLocaleString()}</strong>
            </div>
            <div>
              <span style="color: #64748b; font-size: 10px; display: block;">CRITICAL RISKS</span>
              <strong style="color: #b91c1c; font-size: 14px;">${Number(state.critical_works || 0).toLocaleString()}</strong>
            </div>
            <div>
              <span style="color: #64748b; font-size: 10px; display: block;">TOTAL WORKS</span>
              <span style="font-weight: 600;">${Number(state.total_works || 0).toLocaleString()}</span>
            </div>
            <div>
              <span style="color: #64748b; font-size: 10px; display: block;">ALLOCATION</span>
              <span style="font-weight: 600; color: #0284c7;">₹${state.total_allocation_cr || 0} Cr</span>
            </div>
          </div>
          <div style="background: #f1f5f9; padding: 4px 8px; border-radius: 4px; font-size: 11px; color: #334155;">
            ✂️ <strong>${state.split_tenders || 0}</strong> Tender-Splits • 🔁 <strong>${state.cluster_works || 0}</strong> Clusters
          </div>
          <div style="text-align: center; margin-top: 6px; font-size: 10px; color: #0284c7; font-weight: 700;">
            Click to Inspect State Dossier →
          </div>
        </div>
      `;

      marker.bindTooltip(tooltipContent, {
        direction: "top",
        offset: [0, -10],
        opacity: 0.98,
        className: "custom-leaflet-tooltip"
      });

      marker.on("click", () => {
        setSelectedState(state);
        map.flyTo([state.lat, state.lng], 6.5, { duration: 1.0 });
      });

      halo.addTo(markersGroup);
      marker.addTo(markersGroup);
    });
  }, [stateData, activeMetric]);

  // Handle State Select from dropdown
  const handleSelectStateDropdown = (stateName) => {
    const found = stateData.find((s) => s.state === stateName);
    if (found) {
      setSelectedState(found);
      if (mapInstanceRef.current) {
        mapInstanceRef.current.flyTo([found.lat, found.lng], 6.5, { duration: 1.0 });
      }
    }
  };

  // Reset View
  const handleResetView = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([22.8, 80.0], 4.8, { duration: 1.0 });
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      {/* Map Control Header */}
      <div className="panel" style={{ padding: "16px 20px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "14px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
              <span className="section-tag" style={{ margin: 0 }}>GEOSPATIAL AUDIT INTELLIGENCE</span>
              <span className="badge" style={{ background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8", border: "1px solid rgba(56, 189, 248, 0.3)" }}>
                36 States & UTs • 105,000 Works Mapped
              </span>
            </div>
            <h2 style={{ margin: 0, fontSize: "18px", color: "#fff", fontWeight: 700 }}>
              All-India MPLADS Procurement Anomaly Heatmap
            </h2>
          </div>

          {/* Metric Selector & State Quick Jump */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
            <div style={{ display: "flex", background: "rgba(255,255,255,0.05)", padding: "3px", borderRadius: "8px", border: "1px solid var(--border-subtle)" }}>
              <button
                className={`btn-audit-view ${activeMetric === "flagged" ? "active-metric" : ""}`}
                style={{ padding: "6px 12px", fontSize: "12px", background: activeMetric === "flagged" ? "var(--cyan)" : "transparent", color: activeMetric === "flagged" ? "#000" : "var(--text-secondary)", fontWeight: 700 }}
                onClick={() => setActiveMetric("flagged")}
              >
                🚨 Anomaly Density
              </button>
              <button
                className={`btn-audit-view ${activeMetric === "tenders" ? "active-metric" : ""}`}
                style={{ padding: "6px 12px", fontSize: "12px", background: activeMetric === "tenders" ? "#a855f7" : "transparent", color: activeMetric === "tenders" ? "#fff" : "var(--text-secondary)", fontWeight: 700 }}
                onClick={() => setActiveMetric("tenders")}
              >
                ✂️ Tender-Splits
              </button>
              <button
                className={`btn-audit-view ${activeMetric === "allocation" ? "active-metric" : ""}`}
                style={{ padding: "6px 12px", fontSize: "12px", background: activeMetric === "allocation" ? "#3b82f6" : "transparent", color: activeMetric === "allocation" ? "#fff" : "var(--text-secondary)", fontWeight: 700 }}
                onClick={() => setActiveMetric("allocation")}
              >
                💰 Allocation (₹ Cr)
              </button>
            </div>

            <select
              className="filter-select"
              style={{ width: "190px", fontSize: "12px", padding: "7px 10px" }}
              value={selectedState ? selectedState.state : ""}
              onChange={(e) => handleSelectStateDropdown(e.target.value)}
            >
              <option value="">Jump to State...</option>
              {stateData.map((s) => (
                <option key={s.state} value={s.state}>
                  {s.state} ({s.flagged_works} flagged)
                </option>
              ))}
            </select>

            <button
              className="btn-audit-view"
              style={{ padding: "7px 12px", fontSize: "12px" }}
              onClick={() => setMapTheme(mapTheme === "dark" ? "streets" : mapTheme === "streets" ? "satellite" : "dark")}
              title="Toggle Dark GIS / Street View / Satellite Tiles"
            >
              <Layers size={14} /> {mapTheme === "dark" ? "Dark GIS" : mapTheme === "streets" ? "Streets" : "Satellite"}
            </button>

            <button
              className="btn-audit-view"
              style={{ padding: "7px 12px", fontSize: "12px" }}
              onClick={handleResetView}
              title="Reset India View"
            >
              <Compass size={14} /> Reset
            </button>
          </div>
        </div>
      </div>

      {/* Main Map + Inspection Drawer Layout */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: "16px", minHeight: "620px" }}>
        {/* Leaflet Map Card */}
        <div
          className="panel"
          style={{
            padding: 0,
            overflow: "hidden",
            position: "relative",
            minHeight: "620px",
            background: "#0a0f1d",
            border: "1px solid var(--border-subtle)"
          }}
        >
          {/* Map Target Container */}
          <div ref={mapContainerRef} style={{ width: "100%", height: "100%", minHeight: "620px", zIndex: 1 }} />

          {/* Floating Map Legend Overlay */}
          <div
            style={{
              position: "absolute",
              bottom: "16px",
              left: "16px",
              zIndex: 500,
              background: "rgba(15, 23, 42, 0.88)",
              backdropFilter: "blur(8px)",
              border: "1px solid rgba(255, 255, 255, 0.12)",
              borderRadius: "8px",
              padding: "10px 14px",
              fontSize: "11px",
              color: "var(--text-secondary)",
              maxWidth: "260px"
            }}
          >
            <div style={{ fontWeight: 700, color: "#fff", marginBottom: "6px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
              Geospatial Risk Classification
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#ef4444", boxShadow: "0 0 6px #ef4444" }}></span>
                <span>Critical Priority Hotspot (&gt;10 Critical)</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#f97316" }}></span>
                <span>High Anomaly Concentration (&gt;100 Flagged)</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#f59e0b" }}></span>
                <span>Moderate Risk Variance (&gt;30 Flagged)</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#10b981" }}></span>
                <span>Baseline Regularity (&lt;30 Flagged)</span>
              </div>
            </div>
          </div>
        </div>

        {/* State Detail Inspection Drawer */}
        <div className="panel" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
          {selectedState ? (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
                <div>
                  <span className="section-tag" style={{ margin: 0 }}>STATE AUDIT PROFILE</span>
                  <h3 style={{ margin: "4px 0 2px 0", fontSize: "20px", color: "#fff", fontWeight: 700 }}>
                    {selectedState.state}
                  </h3>
                  <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    {selectedState.zone || "National"} Zone • Coordinate: {selectedState.lat?.toFixed(2)}°N, {selectedState.lng?.toFixed(2)}°E
                  </span>
                </div>
                <div
                  className={`risk-badge ${selectedState.critical_works > 10 ? "critical" : selectedState.flagged_works > 100 ? "high" : "medium"}`}
                  style={{ fontSize: "12px", padding: "4px 10px" }}
                >
                  {selectedState.critical_works > 10 ? "CRITICAL" : selectedState.flagged_works > 100 ? "HIGH RISK" : "ROUTINE"}
                </div>
              </div>

              {/* 4 Key Stat Cards */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "16px" }}>
                <div style={{ background: "rgba(239, 68, 68, 0.08)", border: "1px solid rgba(239, 68, 68, 0.25)", padding: "10px", borderRadius: "8px" }}>
                  <span style={{ fontSize: "11px", color: "var(--text-secondary)", display: "block" }}>Flagged Anomalies</span>
                  <strong style={{ fontSize: "20px", color: "#ef4444" }}>
                    {Number(selectedState.flagged_works || 0).toLocaleString()}
                  </strong>
                </div>

                <div style={{ background: "rgba(185, 28, 28, 0.08)", border: "1px solid rgba(185, 28, 28, 0.25)", padding: "10px", borderRadius: "8px" }}>
                  <span style={{ fontSize: "11px", color: "var(--text-secondary)", display: "block" }}>Critical Inquiries</span>
                  <strong style={{ fontSize: "20px", color: "#f87171" }}>
                    {Number(selectedState.critical_works || 0).toLocaleString()}
                  </strong>
                </div>

                <div style={{ background: "rgba(255, 255, 255, 0.03)", border: "1px solid var(--border-subtle)", padding: "10px", borderRadius: "8px" }}>
                  <span style={{ fontSize: "11px", color: "var(--text-secondary)", display: "block" }}>Total Monitored</span>
                  <strong style={{ fontSize: "18px", color: "#fff" }}>
                    {Number(selectedState.total_works || 0).toLocaleString()}
                  </strong>
                </div>

                <div style={{ background: "rgba(56, 189, 248, 0.08)", border: "1px solid rgba(56, 189, 248, 0.25)", padding: "10px", borderRadius: "8px" }}>
                  <span style={{ fontSize: "11px", color: "var(--text-secondary)", display: "block" }}>Total Budget</span>
                  <strong style={{ fontSize: "18px", color: "var(--cyan)" }}>
                    ₹{selectedState.total_allocation_cr} Cr
                  </strong>
                </div>
              </div>

              {/* Hindi & Easy Explanation Box */}
              <div style={{ background: "rgba(6, 182, 212, 0.05)", border: "1px solid rgba(6, 182, 212, 0.25)", borderRadius: "8px", padding: "12px", marginBottom: "16px" }}>
                <div style={{ fontSize: "11px", fontWeight: 700, color: "var(--cyan)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "6px", display: "flex", alignItems: "center", gap: "6px" }}>
                  <span>🇮🇳</span> राज्य स्तरीय कैग ऑडिट विश्लेषण (State Audit in Hindi)
                </div>
                <p style={{ margin: "0 0 6px 0", fontSize: "12px", color: "var(--text-primary)", lineHeight: "1.5" }}>
                  <strong>{selectedState.state}</strong> में कुल <strong>{Number(selectedState.flagged_works || 0).toLocaleString()}</strong> विकास कार्य संदिग्ध पाए गए हैं, जिनमें से <strong>{selectedState.critical_works || 0}</strong> कामों में तत्काल ऑन-साइट जांच जरूरी है।
                </p>
                <div style={{ fontSize: "11px", color: "var(--text-secondary)", lineHeight: "1.4" }}>
                  {selectedState.split_tenders > 50 && `• ${selectedState.split_tenders} कामों में ई-टेंडर से बचने के लिए बजट को ₹5 लाख से ठीक नीचे रखा गया है। `}
                  {selectedState.cluster_works > 500 && `• ${selectedState.cluster_works} कामों में एक ही गांव में बार-बार वही काम दिखाकर बिल पास किए गए हैं। `}
                  जिला प्रशासन को मौके पर जाकर भौतिक सत्यापन (Physical Site Inspection) कराने के निर्देश दिए गए हैं।
                </div>
              </div>

              {/* Statutory Diagnostic Meters */}
              <div style={{ marginBottom: "16px" }}>
                <h4 style={{ fontSize: "12px", textTransform: "uppercase", color: "var(--cyan)", letterSpacing: "0.5px", margin: "0 0 10px 0" }}>
                  Detected Forensic Red Flags
                </h4>

                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "4px" }}>
                      <span style={{ color: "var(--text-secondary)" }}>GFR 149 Tender-Splitting Avoidance</span>
                      <strong style={{ color: "#ec4899" }}>{selectedState.split_tenders || 0} works</strong>
                    </div>
                    <div style={{ height: "6px", background: "rgba(255,255,255,0.06)", borderRadius: "3px", overflow: "hidden" }}>
                      <div
                        style={{
                          height: "100%",
                          width: `${Math.min(100, ((selectedState.split_tenders || 0) / 750) * 100)}%`,
                          background: "#ec4899"
                        }}
                      />
                    </div>
                  </div>

                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "4px" }}>
                      <span style={{ color: "var(--text-secondary)" }}>Localized Village Repeat Clusters</span>
                      <strong style={{ color: "#a855f7" }}>{selectedState.cluster_works || 0} works</strong>
                    </div>
                    <div style={{ height: "6px", background: "rgba(255,255,255,0.06)", borderRadius: "3px", overflow: "hidden" }}>
                      <div
                        style={{
                          height: "100%",
                          width: `${Math.min(100, ((selectedState.cluster_works || 0) / 3500) * 100)}%`,
                          background: "#a855f7"
                        }}
                      />
                    </div>
                  </div>

                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "4px" }}>
                      <span style={{ color: "var(--text-secondary)" }}>Average Anomaly Score</span>
                      <strong style={{ color: "#38bdf8" }}>{selectedState.avg_risk_score} / 100</strong>
                    </div>
                    <div style={{ height: "6px", background: "rgba(255,255,255,0.06)", borderRadius: "3px", overflow: "hidden" }}>
                      <div
                        style={{
                          height: "100%",
                          width: `${selectedState.avg_risk_score || 0}%`,
                          background: "#38bdf8"
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Directive */}
              <div style={{ background: "rgba(255,255,255,0.02)", padding: "10px", borderRadius: "8px", border: "1px solid var(--border-subtle)", fontSize: "11px", color: "var(--text-secondary)", marginBottom: "8px" }}>
                <Info size={14} style={{ display: "inline", marginRight: "6px", color: "var(--cyan)" }} />
                District Authorities in <strong>{selectedState.state}</strong> have {selectedState.flagged_works} works pending field voucher reconciliation and milestone inspection.
              </div>

              {/* Hindi State Audit Summary */}
              <div style={{ background: "rgba(249, 115, 22, 0.08)", padding: "10px 12px", borderRadius: "8px", border: "1px solid rgba(249, 115, 22, 0.25)", fontSize: "11px", color: "#ffedd5", marginBottom: "14px", lineHeight: "1.5" }}>
                <span style={{ fontWeight: 700, color: "#fdba74", display: "block", marginBottom: "2px" }}>
                  🇮🇳 राज्य ऑडिट सारांश (State Audit Summary):
                </span>
                {selectedState.state} में कुल <strong>{selectedState.flagged_works}</strong> कार्यों में गड़बड़ी के संकेत हैं। अधिकारियों को इनके भौतिक सत्यापन और खर्च बिलों की निष्पक्ष जांच का निर्देश दिया गया है।
              </div>
            </div>
          ) : (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)" }}>
              <Compass size={32} style={{ margin: "0 auto 12px auto", opacity: 0.5 }} />
              <div>Select any state circle on the GIS map to inspect audit metrics.</div>
            </div>
          )}

          {/* Direct Bridge Button to Works Explorer */}
          {selectedState && (
            <button
              className="btn-simulate"
              style={{ width: "100%", padding: "12px" }}
              onClick={() => {
                if (onSelectStateForExplorer) {
                  onSelectStateForExplorer(selectedState.state);
                }
              }}
            >
              <ExternalLink size={16} /> Inspect {selectedState.state} Works ({selectedState.flagged_works} Flagged)
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
