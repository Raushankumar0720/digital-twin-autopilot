import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  MessageSquare,
  CheckCircle,
  AlertCircle,
  Clock,
  Activity,
  RefreshCw,
} from "lucide-react";
import { api } from "../lib/api";
import MasterToggle from "../components/dashboard/MasterToggle";
import PlatformToggles from "../components/dashboard/PlatformToggles";
import ActivityFeed from "../components/dashboard/ActivityFeed";

export default function Dashboard() {
  const [isMasterOn, setIsMasterOn] = useState(true);
  const [activities, setActivities] = useState([]);
  const [stats, setStats] = useState({
    messages_replied: 24,
    avg_response_time: "42s",
    active_platforms: ["telegram", "discord"],
    pending_approvals: 2,
    confidence_score: "88%",
  });
  const [config, setConfig] = useState({
    name: "Nitish",
    formality_level: 3,
    reply_delay_min: 30,
    reply_delay_max: 120,
  });
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const statsData = await api.getStats();
      const configData = await api.getConfig();
      const activityData = await api.getActivity();

      setStats(statsData);
      setConfig(configData);
      setActivities(activityData);
    } catch (err) {
      console.warn("Failed fetching dashboard data from backend server. Using mock presentation data.");
      // Load mock items for showcase
      setActivities([
        {
          id: 1,
          platform: "telegram",
          sender: "Ananya",
          query: "Bro are you free tonight?",
          reply: "yeah probably, just chilling at home. what's up?",
          verified: true,
          timestamp: "Just now",
        },
        {
          id: 2,
          platform: "discord",
          sender: "CodeRebel_9",
          query: "Hey did you run the latest migration?",
          reply: "idk about that one, ask the sysops lead",
          verified: false,
          timestamp: "5 mins ago",
        },
        {
          id: 3,
          platform: "gmail",
          sender: "hiring@innovate.co",
          query: "Hello, we reviewed your autopilot profile and wanted to follow up.",
          reply: "Dear sender,\n\nThank you for reaching out. I appreciate the follow-up.\n\nBest regards,",
          verified: true,
          timestamp: "20 mins ago",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleMasterToggle = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/autopilot/toggle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const data = await res.json();
      setIsMasterOn(data.is_active);
    } catch (err) {
      console.error("Failed to toggle autopilot:", err);
      // Fallback: toggle locally if backend is unreachable
      setIsMasterOn(!isMasterOn);
    }
  };

  const handlePlatformToggle = async (platform) => {
    if (!isMasterOn) return;
    try {
      await api.togglePlatform(platform);
      loadData();
    } catch (err) {
      const isActive = stats.active_platforms.includes(platform);
      const newPlatforms = isActive
        ? stats.active_platforms.filter((p) => p !== platform)
        : [...stats.active_platforms, platform];
      setStats({ ...stats, active_platforms: newPlatforms });
    }
  };

  const handleConfigChange = async (key, val) => {
    const updatedConfig = { ...config, [key]: parseInt(val) || val };
    setConfig(updatedConfig);
    try {
      await api.updateConfig(updatedConfig);
    } catch (err) {
      console.error("Failed updating config on server", err);
    }
  };

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
      {/* Header Banner */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-end",
          borderBottom: "2px solid var(--bmw-ink)",
          paddingBottom: "18px",
          marginBottom: "32px",
        }}
      >
        <div>
          <span className="bmw-label-uppercase" style={{ color: "var(--bmw-blue)", fontSize: "14px" }}>
            MANAGEMENT CONSOLE
          </span>
          <h1 style={{ margin: "4px 0 0 0", fontSize: "32px", fontWeight: "700", color: "var(--bmw-ink)", textTransform: "uppercase", letterSpacing: "1px" }}>
            Control Center
          </h1>
        </div>
        <button
          onClick={loadData}
          className="bmw-btn-secondary"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "10px 18px",
            fontSize: "11px",
          }}
        >
          <RefreshCw size={14} className={loading ? "spin" : ""} />
          SYNC STATUS
        </button>
      </div>

      {/* Master Autopilot Kill Switch */}
      <MasterToggle isMasterOn={isMasterOn} onToggle={handleMasterToggle} />

      {/* Stats Cards Row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "20px",
          marginBottom: "32px",
        }}
      >
        {/* Replied card */}
        <div className="bmw-card" style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div style={{ color: "var(--bmw-blue)", backgroundColor: "var(--bmw-surface-soft)", padding: "12px" }}>
            <MessageSquare size={24} />
          </div>
          <div>
            <div style={{ fontSize: "11px", textTransform: "uppercase", fontWeight: "700", color: "var(--bmw-muted)" }}>
              Replied Today
            </div>
            <div style={{ fontSize: "28px", fontWeight: "700", color: "var(--bmw-ink)", marginTop: "4px" }}>
              {stats.messages_replied}
            </div>
          </div>
        </div>

        {/* Response Delay */}
        <div className="bmw-card" style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div style={{ color: "var(--bmw-blue)", backgroundColor: "var(--bmw-surface-soft)", padding: "12px" }}>
            <Clock size={24} />
          </div>
          <div>
            <div style={{ fontSize: "11px", textTransform: "uppercase", fontWeight: "700", color: "var(--bmw-muted)" }}>
              Avg Delay
            </div>
            <div style={{ fontSize: "28px", fontWeight: "700", color: "var(--bmw-ink)", marginTop: "4px" }}>
              {stats.avg_response_time}
            </div>
          </div>
        </div>

        {/* Confidence Rate */}
        <div className="bmw-card" style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div style={{ color: "var(--bmw-blue)", backgroundColor: "var(--bmw-surface-soft)", padding: "12px" }}>
            <Activity size={24} />
          </div>
          <div>
            <div style={{ fontSize: "11px", textTransform: "uppercase", fontWeight: "700", color: "var(--bmw-muted)" }}>
              Confidence Rate
            </div>
            <div style={{ fontSize: "28px", fontWeight: "700", color: "var(--bmw-ink)", marginTop: "4px" }}>
              {stats.confidence_score}
            </div>
          </div>
        </div>

        {/* Pending Approvals */}
        <Link
          to="/approvals"
          className="bmw-card"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
            textDecoration: "none",
            color: "inherit",
          }}
        >
          <div
            style={{
              color: stats.pending_approvals > 0 ? "var(--bmw-warning)" : "var(--bmw-success)",
              backgroundColor: "var(--bmw-surface-soft)",
              padding: "12px",
            }}
          >
            {stats.pending_approvals > 0 ? <AlertCircle size={24} /> : <CheckCircle size={24} />}
          </div>
          <div>
            <div style={{ fontSize: "11px", textTransform: "uppercase", fontWeight: "700", color: "var(--bmw-muted)" }}>
              Pending Overrides
            </div>
            <div style={{ fontSize: "28px", fontWeight: "700", color: "var(--bmw-ink)", marginTop: "4px" }}>
              {stats.pending_approvals}
            </div>
          </div>
        </Link>
      </div>

      {/* Main Settings Body */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "24px", marginBottom: "32px" }}>
        {/* Left Col: Platform Toggles */}
        <PlatformToggles
          activePlatforms={stats.active_platforms}
          isMasterOn={isMasterOn}
          onTogglePlatform={handlePlatformToggle}
        />

        {/* Right Col: Personality Configuration */}
        <div className="bmw-card">
          <h2 className="bmw-label-uppercase" style={{ fontSize: "14px", marginBottom: "24px" }}>
            Autopilot Parameters
          </h2>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "24px",
              opacity: isMasterOn ? 1 : 0.45,
              pointerEvents: isMasterOn ? "auto" : "none",
              transition: "opacity 0.2s ease",
            }}
          >
            {/* Formality level */}
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                <span className="bmw-label-uppercase" style={{ fontSize: "12px" }}>
                  Formality Level Dial
                </span>
                <span style={{ fontSize: "13px", fontWeight: "700", color: "var(--bmw-blue)" }}>
                  {config.formality_level === 1
                    ? "1 (Very Casual)"
                    : config.formality_level === 3
                    ? "3 (Balanced)"
                    : config.formality_level === 5
                    ? "5 (Professional)"
                    : config.formality_level}
                </span>
              </div>
              <input
                type="range"
                min="1"
                max="5"
                value={config.formality_level}
                onChange={(e) => handleConfigChange("formality_level", e.target.value)}
                style={{ width: "100%", accentColor: "var(--bmw-blue)", cursor: "pointer" }}
              />
            </div>

            {/* Delays configurations */}
            <div style={{ display: "flex", gap: "16px" }}>
              <div style={{ flex: 1 }}>
                <label className="bmw-label-uppercase" style={{ display: "block", fontSize: "11px", marginBottom: "6px" }}>
                  Min Delay (sec)
                </label>
                <input
                  type="number"
                  className="bmw-input"
                  value={config.reply_delay_min}
                  onChange={(e) => handleConfigChange("reply_delay_min", e.target.value)}
                />
              </div>
              <div style={{ flex: 1 }}>
                <label className="bmw-label-uppercase" style={{ display: "block", fontSize: "11px", marginBottom: "6px" }}>
                  Max Delay (sec)
                </label>
                <input
                  type="number"
                  className="bmw-input"
                  value={config.reply_delay_max}
                  onChange={(e) => handleConfigChange("reply_delay_max", e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom section: Activity Feed */}
      <ActivityFeed activities={activities} />
    </div>
  );
}
