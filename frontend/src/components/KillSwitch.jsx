import React, { useState, useEffect } from 'react';
import { Inbox, User, Key, Save, Power, ShieldAlert, Activity, Users } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

function KillSwitch() {
  const [activeTab, setActiveTab] = useState('inbox');
  const [isActive, setIsActive] = useState(true);
  const [loading, setLoading] = useState(false);
  const [activity, setActivity] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [whitelist, setWhitelist] = useState({});

  // Forms state for placeholders
  const [profile, setProfile] = useState({
    name: "Autopilot Twin",
    formality: "3",
    tone: "Balanced & Helpful",
    instructions: "Never commit to meetings without asking first."
  });

  const [credentials, setCredentials] = useState({
    api_id: "",
    api_hash: "",
    phone_number: "",
    groq_api_key: ""
  });

  // Fetch current status
  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/autopilot/status`);
      if (!res.ok) throw new Error('Network error');
      const data = await res.json();
      setIsActive(data.platforms?.telegram !== false);
      setActivity(data.recent_activity || []);
    } catch (err) {
      console.error('Fetch error:', err);
      try {
        const res = await fetch(`${API_BASE}/api/stats`);
        const data = await res.json();
        setIsActive(data.platforms?.telegram !== false);
        setActivity(data.recent_activity || []);
      } catch (e) {
        // Silent catch for polling
      }
    }
  };

  // Toggle the autopilot
  const toggleAutopilot = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/autopilot/platform/toggle?platform=telegram`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await res.json();
      setIsActive(data.platforms?.telegram !== false);
    } catch (err) {
      try {
        const res = await fetch(`${API_BASE}/api/platforms/telegram/toggle`, { method: 'POST' });
        const data = await res.json();
        setIsActive(data.platforms?.telegram !== false);
      } catch (e) {
        alert('Toggle failed. Check backend.');
      }
    }
    setLoading(false);
  };

  const fetchContacts = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/contacts`);
      if (res.ok) {
        const data = await res.json();
        setContacts(data.contacts || []);
        setWhitelist(data.whitelist || {});
      }
    } catch (err) {
      console.error("Failed to fetch contacts", err);
    }
  };

  const handleToggleWhitelist = async (contactId, currentState) => {
    const newState = !currentState;
    setWhitelist({ ...whitelist, [contactId]: newState });
    try {
      await fetch(`${API_BASE}/api/contacts/whitelist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contact_id: contactId, is_enabled: newState })
      });
    } catch (err) {
      console.error("Failed to toggle whitelist", err);
      setWhitelist({ ...whitelist, [contactId]: currentState });
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchContacts();
    const interval = setInterval(() => {
      fetchStatus();
      fetchContacts();
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleProfileSubmit = (e) => {
    e.preventDefault();
    alert("Profile saved locally! (Backend wiring needed for persistence)");
  };

  const handleCredentialsSubmit = (e) => {
    e.preventDefault();
    alert("Credentials saved locally! (Backend wiring needed to update .env)");
  };

  return (
    <div style={{ maxWidth: "1000px", margin: "0 auto", paddingBottom: "60px" }}>
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
            TELEGRAM CONFIGURATION
          </span>
          <h1 style={{ margin: "4px 0 0 0", fontSize: "32px", fontWeight: "700", color: "var(--bmw-ink)", textTransform: "uppercase", letterSpacing: "1px" }}>
            Telegram Autopilot
          </h1>
        </div>
      </div>

      {/* Tab Navigation */}
      <div style={{ display: "flex", gap: "2px", marginBottom: "32px", borderBottom: "1px solid var(--bmw-hairline)" }}>
        <button
          onClick={() => setActiveTab('inbox')}
          style={{
            padding: "16px 24px",
            backgroundColor: activeTab === 'inbox' ? "var(--bmw-surface-strong)" : "transparent",
            border: "none",
            borderBottom: activeTab === 'inbox' ? "3px solid var(--bmw-blue)" : "3px solid transparent",
            color: activeTab === 'inbox' ? "var(--bmw-ink)" : "var(--bmw-muted)",
            fontWeight: "700",
            fontSize: "13px",
            textTransform: "uppercase",
            letterSpacing: "1px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            transition: "all 0.2s ease"
          }}
        >
          <Inbox size={18} />
          Inbox & Feed
        </button>
        <button
          onClick={() => setActiveTab('profile')}
          style={{
            padding: "16px 24px",
            backgroundColor: activeTab === 'profile' ? "var(--bmw-surface-strong)" : "transparent",
            border: "none",
            borderBottom: activeTab === 'profile' ? "3px solid var(--bmw-blue)" : "3px solid transparent",
            color: activeTab === 'profile' ? "var(--bmw-ink)" : "var(--bmw-muted)",
            fontWeight: "700",
            fontSize: "13px",
            textTransform: "uppercase",
            letterSpacing: "1px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            transition: "all 0.2s ease"
          }}
        >
          <User size={18} />
          Personality Profile
        </button>
        <button
          onClick={() => setActiveTab('contacts')}
          style={{
            padding: "16px 24px",
            backgroundColor: activeTab === 'contacts' ? "var(--bmw-surface-strong)" : "transparent",
            border: "none",
            borderBottom: activeTab === 'contacts' ? "3px solid var(--bmw-blue)" : "3px solid transparent",
            color: activeTab === 'contacts' ? "var(--bmw-ink)" : "var(--bmw-muted)",
            fontWeight: "700",
            fontSize: "13px",
            textTransform: "uppercase",
            letterSpacing: "1px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            transition: "all 0.2s ease"
          }}
        >
          <Users size={18} />
          Contacts
        </button>
        <button
          onClick={() => setActiveTab('credentials')}
          style={{
            padding: "16px 24px",
            backgroundColor: activeTab === 'credentials' ? "var(--bmw-surface-strong)" : "transparent",
            border: "none",
            borderBottom: activeTab === 'credentials' ? "3px solid var(--bmw-blue)" : "3px solid transparent",
            color: activeTab === 'credentials' ? "var(--bmw-ink)" : "var(--bmw-muted)",
            fontWeight: "700",
            fontSize: "13px",
            textTransform: "uppercase",
            letterSpacing: "1px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            transition: "all 0.2s ease"
          }}
        >
          <Key size={18} />
          Credentials & Data
        </button>
      </div>

      {/* TAB CONTENT: INBOX */}
      {activeTab === 'inbox' && (
        <div style={{ animation: "fadeIn 0.3s ease" }}>
          {/* Master Toggle Area */}
          <div className="bmw-card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", backgroundColor: isActive ? "var(--bmw-surface-card)" : "#fff5f5", borderColor: isActive ? "var(--bmw-hairline)" : "var(--bmw-error)" }}>
            <div>
              <h2 className="bmw-label-uppercase" style={{ fontSize: "16px", margin: "0 0 8px 0" }}>Telegram Listener Status</h2>
              <p className="bmw-body-sm" style={{ margin: 0, color: isActive ? "var(--bmw-body)" : "var(--bmw-error)" }}>
                {isActive ? "🟢 Active. The autopilot is currently monitoring Telegram and auto-replying." : "🔴 Paused. The autopilot is currently disconnected and will not reply."}
              </p>
            </div>
            <button
              onClick={toggleAutopilot}
              disabled={loading}
              className="bmw-btn-primary"
              style={{
                backgroundColor: isActive ? "var(--bmw-error)" : "var(--bmw-success)",
                display: "flex",
                alignItems: "center",
                gap: "8px"
              }}
            >
              <Power size={16} />
              {loading ? "..." : isActive ? "Pause Telegram Bot" : "Resume Telegram Bot"}
            </button>
          </div>

          <h3 className="bmw-label-uppercase" style={{ marginTop: "32px", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
            <Activity size={18} /> Recent Activity Feed
          </h3>
          <div className="bmw-card" style={{ padding: 0 }}>
            {activity.length === 0 ? (
              <div style={{ padding: "32px", textAlign: "center", color: "var(--bmw-muted)" }}>
                No recent activity recorded for Telegram.
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column" }}>
                {activity.map((item, idx) => (
                  <div key={idx} style={{ 
                    borderBottom: idx !== activity.length - 1 ? "1px solid var(--bmw-hairline)" : "none",
                    padding: "20px 24px",
                    display: "flex",
                    flexDirection: "column",
                    gap: "12px"
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span className="bmw-label-uppercase" style={{ color: "var(--bmw-blue)" }}>{item.sender}</span>
                      <span style={{ fontSize: "12px", color: "var(--bmw-muted-soft)" }}>{item.timestamp}</span>
                    </div>
                    <div style={{ backgroundColor: "var(--bmw-surface-soft)", padding: "12px 16px", borderLeft: "3px solid var(--bmw-hairline-strong)" }}>
                      <span style={{ fontSize: "12px", color: "var(--bmw-muted)", display: "block", marginBottom: "4px" }}>Received:</span>
                      <span className="bmw-body-md">{item.text}</span>
                    </div>
                    <div style={{ padding: "8px 16px" }}>
                      <span style={{ fontSize: "12px", color: "var(--bmw-success)", display: "block", marginBottom: "4px", fontWeight: "700", textTransform: "uppercase" }}>AI Reply:</span>
                      <span className="bmw-body-md">{item.reply}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB CONTENT: PERSONALITY PROFILE */}
      {activeTab === 'profile' && (
        <div style={{ animation: "fadeIn 0.3s ease" }}>
          <div className="bmw-card">
            <h2 className="bmw-label-uppercase" style={{ fontSize: "16px", margin: "0 0 24px 0" }}>Bot Personality Settings</h2>
            <form onSubmit={handleProfileSubmit} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
                <div>
                  <label className="bmw-label-uppercase" style={{ fontSize: "11px", display: "block", marginBottom: "8px" }}>Display Name / Persona</label>
                  <input 
                    type="text" 
                    className="bmw-input" 
                    value={profile.name} 
                    onChange={e => setProfile({...profile, name: e.target.value})} 
                  />
                </div>
                <div>
                  <label className="bmw-label-uppercase" style={{ fontSize: "11px", display: "block", marginBottom: "8px" }}>Conversational Tone</label>
                  <input 
                    type="text" 
                    className="bmw-input" 
                    value={profile.tone} 
                    onChange={e => setProfile({...profile, tone: e.target.value})} 
                  />
                </div>
              </div>

              <div>
                <label className="bmw-label-uppercase" style={{ fontSize: "11px", display: "block", marginBottom: "8px" }}>
                  Formality Level (1-5)
                </label>
                <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                  <input 
                    type="range" 
                    min="1" max="5" 
                    value={profile.formality}
                    onChange={e => setProfile({...profile, formality: e.target.value})}
                    style={{ flex: 1, accentColor: "var(--bmw-blue)" }}
                  />
                  <span style={{ fontWeight: "700", color: "var(--bmw-ink)" }}>{profile.formality}</span>
                </div>
              </div>

              <div>
                <label className="bmw-label-uppercase" style={{ fontSize: "11px", display: "block", marginBottom: "8px" }}>Custom Instructions (Prompt Injection)</label>
                <textarea 
                  className="bmw-input" 
                  rows="4" 
                  value={profile.instructions}
                  onChange={e => setProfile({...profile, instructions: e.target.value})}
                  style={{ resize: "vertical" }}
                ></textarea>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "12px" }}>
                <button type="submit" className="bmw-btn-primary" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <Save size={16} /> Save Profile Settings
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* TAB CONTENT: CONTACTS */}
      {activeTab === 'contacts' && (
        <div style={{ animation: "fadeIn 0.3s ease" }}>
          <div className="bmw-card">
            <h2 className="bmw-label-uppercase" style={{ fontSize: "16px", margin: "0 0 24px 0" }}>Contact List & Whitelist</h2>
            <p className="bmw-body-sm" style={{ marginBottom: "24px" }}>
              Select which contacts the Autopilot is allowed to reply to. If a contact is disabled, the bot will completely ignore their messages.
            </p>
            
            <div style={{ border: "1px solid var(--bmw-hairline)" }}>
              {contacts.length === 0 ? (
                <div style={{ padding: "32px", textAlign: "center", color: "var(--bmw-muted)" }}>
                  No contacts found. Make sure the Telegram Listener is running!
                </div>
              ) : (
                contacts.map((contact, idx) => {
                  const isEnabled = whitelist[contact.id] !== false;
                  return (
                    <div key={contact.id} style={{ 
                      display: "flex", 
                      justifyContent: "space-between", 
                      alignItems: "center",
                      padding: "16px 24px",
                      borderBottom: idx < contacts.length - 1 ? "1px solid var(--bmw-hairline)" : "none",
                      backgroundColor: !isEnabled ? "var(--bmw-surface-soft)" : "transparent"
                    }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                        <div style={{ 
                          width: "36px", height: "36px", borderRadius: "50%", 
                          backgroundColor: "var(--bmw-surface-strong)",
                          display: "flex", alignItems: "center", justifyContent: "center",
                          color: "var(--bmw-muted)",
                          flexShrink: 0
                        }}>
                          <User size={18} />
                        </div>
                        <div>
                          <div style={{ fontWeight: "600", fontSize: "14px", color: "var(--bmw-ink)" }}>{contact.name}</div>
                          <div style={{ fontSize: "12px", color: "var(--bmw-muted)" }}>Last active: {contact.last_active}</div>
                        </div>
                      </div>
                      
                      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                        <span style={{ fontSize: "11px", fontWeight: "700", textTransform: "uppercase", color: !isEnabled ? "var(--bmw-muted)" : "var(--bmw-success)" }}>
                          {!isEnabled ? "Disabled" : "Autopilot Active"}
                        </span>
                        <button 
                          onClick={() => handleToggleWhitelist(contact.id, isEnabled)}
                          className="bmw-btn-secondary" 
                          style={{ padding: "6px 12px", fontSize: "11px", borderColor: !isEnabled ? "var(--bmw-hairline-strong)" : "var(--bmw-error)", color: !isEnabled ? "var(--bmw-ink)" : "var(--bmw-error)" }}>
                          {!isEnabled ? "Enable" : "Disable"}
                        </button>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT: CREDENTIALS */}
      {activeTab === 'credentials' && (
        <div style={{ animation: "fadeIn 0.3s ease" }}>
          
          <div style={{ backgroundColor: "rgba(34, 158, 217, 0.1)", border: "1px solid rgba(34, 158, 217, 0.3)", padding: "20px", marginBottom: "24px", display: "flex", gap: "16px" }}>
            <ShieldAlert size={24} color="var(--bmw-blue)" style={{ flexShrink: 0 }} />
            <div>
              <h3 style={{ margin: "0 0 8px 0", color: "var(--bmw-ink)", fontSize: "16px" }}>Why is this data required?</h3>
              <p style={{ margin: 0, fontSize: "14px", color: "var(--bmw-body)" }}>
                To connect as a "Digital Twin", the autopilot must log in as a real user using the official Telegram API, rather than a standard bot API. 
                This requires your unique <strong>API ID</strong> and <strong>API Hash</strong> obtained from <a href="https://my.telegram.org" target="_blank" rel="noreferrer" style={{ color: "var(--bmw-blue)", textDecoration: "none", fontWeight: "600" }}>my.telegram.org</a>, 
                as well as a fast LLM API Key (like Groq) to generate the responses.
              </p>
            </div>
          </div>

          <div className="bmw-card">
            <h2 className="bmw-label-uppercase" style={{ fontSize: "16px", margin: "0 0 24px 0" }}>API Credentials</h2>
            <form onSubmit={handleCredentialsSubmit} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
                <div>
                  <label className="bmw-label-uppercase" style={{ fontSize: "11px", display: "block", marginBottom: "8px" }}>Telegram API ID</label>
                  <input 
                    type="text" 
                    className="bmw-input" 
                    placeholder="e.g. 1234567"
                    value={credentials.api_id} 
                    onChange={e => setCredentials({...credentials, api_id: e.target.value})} 
                  />
                </div>
                <div>
                  <label className="bmw-label-uppercase" style={{ fontSize: "11px", display: "block", marginBottom: "8px" }}>Telegram Phone Number</label>
                  <input 
                    type="text" 
                    className="bmw-input" 
                    placeholder="e.g. +91XXXXXXXXXX"
                    value={credentials.phone_number} 
                    onChange={e => setCredentials({...credentials, phone_number: e.target.value})} 
                  />
                </div>
              </div>

              <div>
                <label className="bmw-label-uppercase" style={{ fontSize: "11px", display: "block", marginBottom: "8px" }}>Telegram API Hash</label>
                <input 
                  type="password" 
                  className="bmw-input" 
                  placeholder="e.g. abcdef1234567890"
                  value={credentials.api_hash}
                  onChange={e => setCredentials({...credentials, api_hash: e.target.value})}
                />
              </div>

              <div style={{ borderTop: "1px solid var(--bmw-hairline)", margin: "8px 0" }}></div>

              <div>
                <label className="bmw-label-uppercase" style={{ fontSize: "11px", display: "block", marginBottom: "8px" }}>Groq API Key (Llama-3 LLM)</label>
                <input 
                  type="password" 
                  className="bmw-input" 
                  placeholder="gsk_..."
                  value={credentials.groq_api_key}
                  onChange={e => setCredentials({...credentials, groq_api_key: e.target.value})}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "12px" }}>
                <button type="submit" className="bmw-btn-primary" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <Save size={16} /> Save Credentials
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(5px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}

export default KillSwitch;
