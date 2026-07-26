from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel
from app.upload import app as upload_app

app = FastAPI()

# --- CORS Configuration (Crucial for React) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the upload router from Phase 2
app.include_router(upload_app.router)

# File paths
STATE_FILE = "autopilot_state.json"
ACTIVITY_FILE = "activity_log.json"
CONTACTS_FILE = "data/contacts.json"

def read_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"is_active": True, "platforms": {"telegram": True}}

def write_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def read_activity(limit=50):
    try:
        with open(ACTIVITY_FILE, "r") as f:
            data = json.load(f)
            return data[-limit:]
    except:
        return []

@app.get("/")
def root():
    return {"status": "Digital Twin API is running"}

# ---------- MAIN DASHBOARD ENDPOINTS ----------
@app.get("/api/autopilot/status")
def get_status():
    state = read_state()
    platforms_dict = state.get("platforms", {"telegram": True})
    active_platforms = [k for k, v in platforms_dict.items() if v]
    activity_data = read_activity(200)
    return {
        "is_active": state.get("is_active", True),
        "platforms": platforms_dict,
        "active_platforms": active_platforms,
        "recent_activity": activity_data[:10],
        "messages_replied": len(activity_data),
        "avg_response_time": "15s",
        "pending_approvals": 0,
        "confidence_score": "95%"
    }

# --- THIS FIXES YOUR FRONTEND ERROR (Alias for /api/stats) ---
@app.get("/api/stats")
def get_stats_alias():
    return get_status()

@app.post("/api/autopilot/toggle")
def toggle_autopilot():
    state = read_state()
    state["is_active"] = not state["is_active"]
    write_state(state)
    return {"is_active": state["is_active"]}

# --- THIS FIXES YOUR FRONTEND ERROR (Alias for /api/toggle) ---
@app.post("/api/toggle")
def toggle_alias():
    return toggle_autopilot()

@app.post("/api/autopilot/platform/toggle")
def toggle_platform(platform: str = "telegram"):
    state = read_state()
    if "platforms" not in state:
        state["platforms"] = {}
    if platform in state["platforms"]:
        state["platforms"][platform] = not state["platforms"][platform]
    else:
        state["platforms"][platform] = True
    write_state(state)
    return {"platforms": state["platforms"], "is_active": state["platforms"][platform]}

# --- THIS FIXES YOUR FRONTEND ERROR (Alias for /api/platforms/{platform}/toggle) ---
@app.post("/api/platforms/{platform}/toggle")
def toggle_platform_path(platform: str):
    return toggle_platform(platform)

@app.get("/api/autopilot/feed")
def get_feed(limit: int = 50):
    return {"activity": read_activity(limit)}

# ---------- CONTACTS & WHITELIST ----------
@app.get("/api/contacts")
def get_contacts():
    try:
        with open(CONTACTS_FILE, "r") as f:
            contacts = json.load(f)
    except:
        contacts = []
        
    state = read_state()
    whitelist = state.get("whitelist", {})
    
    return {
        "contacts": contacts,
        "whitelist": whitelist
    }

class WhitelistToggleRequest(BaseModel):
    contact_id: str
    is_enabled: bool

@app.post("/api/contacts/whitelist")
def toggle_whitelist(req: WhitelistToggleRequest):
    state = read_state()
    if "whitelist" not in state:
        state["whitelist"] = {}
        
    state["whitelist"][req.contact_id] = req.is_enabled
    write_state(state)
    return {"whitelist": state["whitelist"]}
