import React, { useState, useEffect } from "react";
import { Shield, Radio } from "lucide-react";
import { api } from "../../lib/api";

export default function Navbar() {
  const [profile, setProfile] = useState({ name: "Raushan Kumar", initials: "RK" });

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const config = await api.getConfig();
        if (config && config.name) {
          setProfile({
            name: config.name,
            initials: config.initials || "RK"
          });
        }
      } catch (err) {
        console.warn("Failed fetching profile name from API. Using defaults.");
      }
    };

    fetchProfile();

    const handleConfigUpdate = (e) => {
      if (e.detail && e.detail.name) {
        setProfile({
          name: e.detail.name,
          initials: e.detail.initials || "RK"
        });
      }
    };

    window.addEventListener("configUpdated", handleConfigUpdate);
    return () => window.removeEventListener("configUpdated", handleConfigUpdate);
  }, []);

  return (
    <header className="bmw-navbar">
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        {/* BMW inspired clean branding */}
        <div
          style={{
            width: "36px",
            height: "36px",
            borderRadius: "50%",
            border: "2px solid var(--bmw-blue)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "var(--bmw-blue)",
            fontWeight: "800",
            fontSize: "16px",
          }}
        >
          D
        </div>
        <div>
          <span
            className="bmw-label-uppercase"
            style={{ fontSize: "14px", color: "var(--bmw-ink)" }}
          >
            DIGITAL TWIN
          </span>
          <span
            style={{
              fontSize: "14px",
              fontWeight: "300",
              color: "var(--bmw-muted)",
              marginLeft: "6px",
            }}
          >
            | Autopilot Autonomy
          </span>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
        {/* Autopilot Status Indicator */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <Radio size={16} color="var(--bmw-success)" className="pulse" />
          <span
            className="bmw-label-uppercase"
            style={{ fontSize: "11px", color: "var(--bmw-success)" }}
          >
            Autopilot Online
          </span>
        </div>

        <div
          style={{
            borderLeft: "1px solid var(--bmw-hairline)",
            height: "24px",
          }}
        />

        {/* User profile */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              width: "32px",
              height: "32px",
              backgroundColor: "var(--bmw-surface-strong)",
              borderRadius: "0",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: "700",
              fontSize: "13px",
              color: "var(--bmw-ink)",
            }}
          >
            {profile.initials}
          </div>
          <span
            className="bmw-label-uppercase"
            style={{ fontSize: "12px", color: "var(--bmw-ink)" }}
          >
            {profile.name}
          </span>
        </div>
      </div>
    </header>
  );
}
