# Mingle (v0.1)

Mingle is an interactive game + agent observability platform. 
The v0.1 milestone focuses on **Tic-Tac-Toe**, enabling users to play matches against different search agents while inspecting their real-time decision telemetry and move replays.

---

## 🚀 Key Features

- **Interactive Tic-Tac-Toe Game**: Play against AI search agents or run agent-vs-agent matches.
- **Agent Decision Inspector**: Telemetry panel exposing search metrics per decision (decision duration, nodes explored, search depth, terminal nodes, deep copies, pruning cutoffs).
- **Match Replay Timeline**: Step backward and forward through past moves to inspect historical game states and their corresponding decision metrics.
- **Supported Agents**:
  - `human` — Interactive human player input
  - `random` — Uniform random move selector
  - `minimax` — Full Minimax search algorithm
  - `alphabeta` — Minimax search with Alpha-Beta pruning

---

## 🛠 Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic
- **Frontend**: React 18, TypeScript, Vite, Vanilla CSS
- **Design System**: Dark technical minimalism with restrained violet accents and responsive grid layout

---

## 📁 Repository Structure

```text
Mingle/
├── game_sandbox/              # Python FastAPI Backend
│   ├── agents/                # Agent implementations (Minimax, AlphaBeta, Random, Human)
│   ├── api/                   # FastAPI routes & schemas
│   ├── core/                  # Game & Agent protocol definitions
│   ├── games/                 # Game rule engine (Tic-Tac-Toe)
│   ├── observability/         # Decision & search metrics collectors
│   └── session/               # Session runtime orchestration
├── frontend/                  # React + TypeScript Frontend
│   ├── src/
│   │   ├── api/               # HTTP client for backend endpoints
│   │   ├── components/        # UI components (GameBoard, DecisionPanel, ReplayTimeline, etc.)
│   │   ├── features/          # Domain types & state mapping
│   │   ├── hooks/             # Custom React hooks (useGame, useReplay)
│   │   └── types/             # TypeScript API interfaces
│   └── index.html
├── main.py
├── pyproject.toml
└── README.md
```

---

## 🏁 Getting Started

### Prerequisites

- **Python**: `>= 3.11`
- **Node.js**: `>= 18`

---

### 1. Start the Backend

1. Install Python dependencies:
   ```bash
   pip install -e .
   ```

2. Run the FastAPI dev server:
   ```bash
   python -m uvicorn game_sandbox.api.app:app --host 127.0.0.1 --port 8000 --reload
   ```
   The backend API will run on `http://127.0.0.1:8000`. You can inspect the interactive OpenAPI documentation at `http://127.0.0.1:8000/docs`.

---

### 2. Start the Frontend

1. Navigate to the frontend directory and install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the Vite development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | API health check |
| `POST` | `/games` | Create a new game session with selected player agents |
| `GET` | `/games/{session_id}` | Retrieve current game state |
| `POST` | `/games/{session_id}/actions` | Submit a move for the current player |
| `GET` | `/games/{session_id}/replay` | Retrieve complete move history and replay states |
| `GET` | `/games/{session_id}/decisions/{decision_id}` | Retrieve decision telemetry for a specific agent move |

---

## 🧪 Testing & Verification

### Running Backend Tests
```bash
pytest
```

### Building Frontend for Production
```bash
cd frontend
npm run build
```
