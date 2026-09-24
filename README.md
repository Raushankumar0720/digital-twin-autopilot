# Digital Twin Autopilot 🚀

**Digital Twin Autopilot** is a personal AI clone that integrates with popular communication platforms (Telegram, Discord, Gmail) to automatically reply to messages on your behalf. The system mimics your voice texture, casual slang, catchphrases, and typing patterns by utilizing a hybrid orchestration of LLMs, local slang engines, and personality configuration dials.

Designed with a premium, corporate **BMW-inspired design system** (clean cream canvas background, corporate blue CTAs, sharp layout grids, and dark navy elevated displays), it provides a complete control center to monitor and audit your digital clone.

---

## 📸 Screenshots

### 1. Management Console (Dashboard)
The dashboard provides a central control panel to override the clone, monitor response stats, configure delays, and view a live conversation feed.
![Management Console Dashboard](assets/management_console.png)

### 2. Telegram Autopilot Credentials & Configuration
Allows you to safely enter your API credentials, phone number, and Groq LLM API Key to connect the client.
![Telegram Autopilot Credentials & Configuration](assets/credentials_config.png)

---

## 🏗️ Architecture & Event Flow

The system is designed around an asynchronous, decoupled event-driven pipeline ensuring low latency and non-blocking I/O across communication channels:

`mermaid
flowchart LR
    A([Telegram Event / User]) -->|1. Inbound Webhook / Message| B[FastAPI Gateway]
    B -->|2. Async Event Dispatch| C[Background Worker Daemon]
    C -->|3. Persona & Slang Analysis| D[Groq LPU / LLM Engine]
    D -->|4. Synthesized Stream Response| C
    C -->|5. Simulated Typing & Dispatch| E([Client / Telegram API])

    subgraph State & Management Plane
        F[React + Vite Console] <-->|REST API & Real-time Logs| B
        C <-->|Sync State & Telemetry| G[(State & Contacts DB)]
    end

    style A fill:#0284c7,stroke:#0369a1,stroke-width:2px,color:#fff
    style B fill:#059669,stroke:#047857,stroke-width:2px,color:#fff
    style C fill:#4f46e5,stroke:#4338ca,stroke-width:2px,color:#fff
    style D fill:#dc2626,stroke:#b91c1c,stroke-width:2px,color:#fff
    style E fill:#0284c7,stroke:#0369a1,stroke-width:2px,color:#fff
    style F fill:#d97706,stroke:#b45309,stroke-width:2px,color:#fff
    style G fill:#475569,stroke:#334155,stroke-width:2px,color:#fff
`

### Event Processing Pipeline:
1. **Telegram Ingestion**: Incoming messages and metadata are received via the Telethon client / Telegram MTProto protocol.
2. **FastAPI Gateway & Routing**: Handles configuration toggles, rate limits, contact whitelist/blacklist policies, and state controls.
3. **Async Autopilot Worker**: Evaluates relationship scores, calculates realistic typing delays, and injects user-specific slang/vocabulary through a contextual matching engine.
4. **Groq LPU Inference**: Leverages Groq's high-speed inference engine (Llama-3) for ultra-low latency response generation matching the user's authentic tone.
5. **Client Dispatch**: Simulates organic human typing intervals before transmitting the synthetic response back to the client.

### Core Architecture Components:
* **Frontend Console (Vite + React 18)**: Single-page control center featuring telemetry monitoring, manual overrides, response delays, and whitelist controls.
* **Backend API (FastAPI)**: Asynchronous REST service managing state persistence, metrics, and authentication.
* **Autopilot Daemon (Telethon / Asyncio Worker)**: Persistent background daemon with custom persona matching, sentiment weighting, and Groq LLM orchestration.

---

## 🛠️ Installation & Setup

### Prerequisites
* **Node.js (v18+)** & NPM
* **Python (3.10+)**
* *(Optional)* Docker & Docker Compose

### Step 1: Clone and Set up Environment Variables
1. Clone the repository and navigate to the project directory:
   ```bash
   cd digital-twin-autopilot
   ```
2. Duplicate `.env.example` to create your local `.env` file:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and fill in your keys:
   * **`GROQ_API_KEY`**: Obtain from [console.groq.com](https://console.groq.com/).
   * **`API_ID` & `API_HASH`**: Obtain from [my.telegram.org](https://my.telegram.org/).
   * **`PHONE_NUMBER`**: The phone number connected to your Telegram account (e.g., `+1234567890`).

---

### Step 2: Native Manual Installation (Recommended for Local Dev)

#### A. Backend Setup
1. Move to the `backend/` folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   * **PowerShell**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * **Command Prompt (CMD) / Git Bash**:
     ```bash
     python -m venv venv
     source venv/Scripts/activate
     ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the **FastAPI Server** (Terminal 1):
   ```bash
   uvicorn app.main_api:app --reload --port 8000
   ```
5. Start the **Telegram Listener Daemon** (Terminal 2):
   ```bash
   python app/main.py
   ```
   *(Note: On the first run, the daemon will ask you to enter the login code sent to your Telegram app to authenticate and generate `session.session`.)*

#### B. Frontend Setup
1. Open a new terminal (Terminal 3) and move to the `frontend/` folder:
   ```bash
   cd frontend
   ```
2. Install Node packages:
   ```bash
   npm install
   ```
3. Start the Vite React development server:
   ```bash
   npm run dev
   ```
4. Open **`http://localhost:5173`** in your browser.

---

## 🔌 API Endpoints Reference

### Dashboard REST APIs
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/stats` | Fetches system stats (autopilot status, reply count, avg delay, active platforms). |
| `POST` | `/api/toggle` | Master Kill Switch to globally activate or pause the autopilot. |
| `POST` | `/api/platforms/{platform}/toggle` | Toggle individual channel states (e.g. Telegram). |
| `GET` | `/api/contacts` | Fetches synced contacts list and whitelist/blacklist configuration. |
| `POST` | `/api/contacts/whitelist` | Enables/disables autopilot replies for a specific contact. |

---

## 🎮 Demo
To test your clone locally:
1. Open the UI at `http://localhost:5173`.
2. Go to the **Control Center** dashboard and verify that **Autopilot Status** is showing as **"ONLINE"**.
3. Toggle the Telegram channel to **Online**.
4. Send a private Telegram message to yourself or have a whitelisted contact send you a message.
5. The terminal running `python app/main.py` will print the incoming message, execute the slang engine, and stream/respond using your digital twin clone.
6. The updated reply and activity statistics will immediately appear on the **Live Activity Feed** on the dashboard.

---

## 🔮 Future Improvements
* 🔄 **Database Integration**: Migrate local JSON state engines (`autopilot_state.json`, `activity_log.json`) to SQLite/PostgreSQL for production reliability.
* 🎙️ **Voice Replication**: Support sending audio/voice note responses using ElevenLabs cloning.
* 🤖 **Multi-Channel Integrations**: Full active client daemons for Discord and Gmail (currently under progress).
* 📈 **Advanced Analytics**: Interactive charts showing response time distributions, sentiment matching levels, and memory usage.

---

## 📄 License
This project is licensed under the **MIT License**. Feel free to use, modify, and distribute it.