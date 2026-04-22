# Kimijang Console

## The AI-Native Developer Operations Platform

> **"You're the CTO, agents are your team."**

Kimijang Console is a **project-local dashboard** for managing AI coding agents. Inspired by [Paperclip](https://github.com/paperclipai/paperclip) but built specifically for software engineers, it transforms chaotic terminal sessions into organized, trackable, and measurable development workflows.

---

## 🎯 Vision

### The Problem

Current AI coding tools suffer from:
- **Ephemeral sessions** - Lose context on every restart
- **Invisible costs** - No idea how much you're spending
- **No accountability** - Can't track what agents did
- **Lost knowledge** - Session insights disappear
- **Manual coordination** - Managing multiple agents is painful

### The Solution

Kimijang Console brings **structure to AI-assisted development**:

```
Traditional AI Coding          Kimijang Console
─────────────────────        ─────────────────────
$ kimi "fix this"     →     Project: api-refactor
Chat, chat, chat...         ├─ Task: Fix auth middleware
Restart → lose everything   │  ├─ Assigned: Backend Agent
                             │  ├─ Branch: feat/fix-auth
                             │  ├─ Cost: $2.40
                             │  └─ Status: In Review
                             ├─ Knowledge: Auth decisions
                             └─ 3 other tasks queued
```

---

## 🏗️ Architecture

### Project-Local Design

```
my-project/
├── src/
├── tests/
├── .git/
└── .kimijang/              ← Console lives here
    ├── console.db          ← SQLite database
    ├── config.toml         ← Project config
    ├── knowledge/          ← Markdown knowledge base
    │   ├── decisions/
    │   ├── sessions/
    │   └── docs/
    └── agents/             ← Agent configurations
```

**Why project-local?**
- ✅ Self-contained - travels with your code
- ✅ Version controllable - commit `.kimijang/config.toml`
- ✅ Git-ignored data - `console.db` stays local
- ✅ Multiple projects - each has own console

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python + FastAPI |
| **Database** | SQLite |
| **Real-time** | WebSocket |
| **Frontend** | React + TypeScript |
| **Styling** | TailwindCSS + Violet Theme |
| **State** | Zustand + React Query |

---

## 📊 Core Modules

### 1. Dashboard (Mission Control)

```
┌─────────────────────────────────────────────────────────────┐
│  KIMIJANG CONSOLE > my-api                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Sessions │  │   Cost   │  │  Tasks   │                  │
│  │    3     │  │  $12.45  │  │   2 done │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│                                                              │
│  🤖 ACTIVE AGENTS                                            │
│  ├─ Backend Dev    working    Task #234   $2.40            │
│  └─ Code Reviewer  idle       -            $0.00            │
│                                                              │
│  📋 RECENT TASKS                                             │
│  ├─ [doing] Refactor auth        🤖 Backend Dev   $2.40    │
│  ├─ [review] Fix tests           👀 Reviewer      $0.80    │
│  └─ [done]  Update README        ✅ Done          $0.30    │
│                                                              │
│  📝 LATEST KNOWLEDGE                                         │
│  └─ Auth Refactor Decision (2h ago)                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Real-time stats (sessions, costs, tasks)
- Active agent monitoring
- Recent activity feed
- Quick actions (new task, new session)

---

### 2. Task Board (Kanban)

Project management for AI tasks:

```
[Todo]        [Doing]         [Review]        [Done]
──────────    ──────────      ──────────      ──────────
┌────────┐    ┌────────┐       ┌────────┐      ┌────────┐
│Setup CI│    │🤖      │       │👀      │      │✅      │
│        │    │Refactor│       │Review  │      │README  │
│        │    │auth    │       │auth    │      │update  │
│$0.00   │    │$2.40   │       │$0.80   │      │$0.30   │
│[Start] │    │[View]  │       │[Done]  │      │        │
└────────┘    └────────┘       └────────┘      └────────┘
```

**Features:**
- Drag-and-drop kanban
- Git branch auto-creation (`feat/fix-auth-a1b2`)
- Cost tracking per task
- Assignment to agents
- Status workflow: `todo → doing → review → done`

**Task Properties:**
```typescript
{
  id: string,
  title: string,
  description: string,
  status: 'todo' | 'doing' | 'review' | 'done',
  assignee_id: string,       // Agent
  branch: string,            // Auto-generated
  estimated_cost: number,    // Budget
  actual_cost: number,        // Tracked
  created_at: Date,
  completed_at: Date
}
```

---

### 3. Agents (Team Management)

Your AI employee directory:

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ 🤖 Backend  │  │ 👀 Code     │  │ 🎨 UI       │
│    Dev      │  │  Reviewer   │  │ Designer    │
├─────────────┤  ├─────────────┤  ├─────────────┤
│ Status: 🟢  │  │ Status: ⚪  │  │ Status: 🟡  │
│ Working     │  │ Idle        │  │ Paused      │
├─────────────┤  ├─────────────┤  ├─────────────┤
│ Model:      │  │ Model:      │  │ Model:      │
│ claude-3-5  │  │ claude-3-5  │  │ gpt-4       │
├─────────────┤  ├─────────────┤  ├─────────────┤
│ Today: $2.40│  │ Today: $0.00│  │ Today: $1.20│
│ Total: $45  │  │ Total: $12  │  │ Total: $28  │
├─────────────┤  ├─────────────┤  ├─────────────┤
│ [Pause]     │  │ [Assign]    │  │ [Resume]    │
└─────────────┘  └─────────────┘  └─────────────┘
```

**Agent Types:**
| Role | Purpose | Model |
|------|---------|-------|
| **Coder** | Write code, refactor, debug | claude-3-5-sonnet |
| **Reviewer** | Code review, security checks | claude-3-5-haiku |
| **Architect** | Design decisions, planning | o1-preview |
| **Tester** | Write tests, coverage | claude-3-5-sonnet |

**Agent Config:**
```typescript
{
  id: string,
  name: string,
  role: 'coder' | 'reviewer' | 'architect' | 'tester',
  model: string,
  status: 'idle' | 'working',
  yolo_mode: boolean,        // Auto-approve safe actions
  max_cost_per_task: number,
  cost_today: number,
  cost_total: number,
  current_task_id?: string
}
```

---

### 4. Knowledge Base (Wiki)

Persistent memory across sessions:

```
📁 knowledge/
├─ 📁 decisions/
│  ├─ 001-auth-strategy.md
│  └─ 002-database-choice.md
├─ 📁 sessions/
│  ├─ 2025-04-22-auth-refactor.md
│  └─ 2025-04-21-api-setup.md
└─ 📁 docs/
   ├─ API-Contract.md
   └─ Deployment.md
```

**Note Types:**
- **Session Summaries** - Auto-generated from agent sessions
- **Decisions** - Architecture Decision Records (ADRs)
- **Docs** - Project documentation
- **Patterns** - Reusable code patterns

**Auto-Generation:**
After each session, Kimijang auto-creates:
```markdown
# Session Summary: Auth Refactor

## Task
Refactor authentication middleware (Task #234)

## Actions Taken
- Switched to JWT with bcrypt
- Added rate limiting
- Updated tests

## Key Decisions
- Use 24h token expiry (stateless)
- Rotate tokens on password change

## Code Changes
- `src/auth/jwt.ts` - New implementation
- `src/auth/bcrypt.ts` - Hashing utility
- `tests/auth/*` - Updated tests

## Cost: $2.40 | Tokens: 12,450
```

---

### 5. MCP Toolkit

Visual MCP server management:

```
┌─────────────────────────────────────────────────────────────┐
│  MCP SERVERS                                    [+ Add]    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🔧 Filesystem                              [ON] [⚙️] [🗑️] │
│     Tools: read_file, write_file, list_directory...         │
│                                                              │
│  🐙 GitHub                                  [ON] [⚙️] [🗑️] │
│     Tools: create_pr, merge, comment, list_issues...      │
│                                                              │
│  🐳 Docker                                  [OFF] [▶️] [🗑️]│
│     Status: Connection failed                               │
│     Last error: Container not found                        │
│                                                              │
│  📊 PostgreSQL                              [ON] [⚙️] [🗑️] │
│     Tools: query, schema, migrate...                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Toggle servers on/off
- View available tools
- Test connections
- Configure per-project

---

## 🔄 Workflows

### Workflow 1: Start New Feature

```bash
# 1. Enter project
cd my-api

# 2. Initialize console (first time)
kimijang console init

# 3. Start console
kimijang console
# → Opens http://localhost:8080
```

In the UI:
1. Click "New Task"
2. Title: "Add OAuth2 login"
3. Assign to: Backend Dev
4. Auto-creates branch: `feat/add-oauth2-a1b2`
5. Agent starts working...

### Workflow 2: Agent Works

```
Agent receives task → Creates session
     ↓
Works on branch `feat/add-oauth2-a1b2`
     ↓
Live updates in Console:
  - Status: "Working on OAuth2..."
  - Cost: $1.20
  - Files changed: 5
     ↓
Auto-commits with message
     ↓
Moves task to "Review"
```

### Workflow 3: Code Review

```
Task appears in [Review] column
     ↓
Code Reviewer agent assigned
     ↓
Reviews diff, comments, suggestions
     ↓
Human reviews in Console UI
     ↓
Approve → Task moves to [Done]
     ↓
Optional: Auto-create PR
```

### Workflow 4: Knowledge Capture

```
Session completes
     ↓
Auto-generate summary
     ↓
Save to .kimijang/knowledge/sessions/
     ↓
Link related decisions
     ↓
Searchable in Console
```

---

## 📈 Analytics

Track everything:

| Metric | Description |
|--------|-------------|
| **Cost per Task** | Individual task spending |
| **Agent Efficiency** | $/token ratio |
| **Project Budget** | Monthly spend vs limit |
| **Session Duration** | Time to complete tasks |
| **Tool Usage** | Most-used MCP tools |

```
┌─────────────────────────────────────────────────────────────┐
│  ANALYTICS                                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  This Month: $45.20 / $100.00                               │
│  ████████████████████░░░░░░░░░  45%                       │
│                                                              │
│  Cost by Agent:                                             │
│  Backend Dev    ████████████████████ $28.50              │
│  Code Reviewer  ██████ $12.30                              │
│  UI Designer    ████ $4.40                               │
│                                                              │
│  Top Tasks:                                                 │
│  1. Refactor auth (Task #234)        $4.20                │
│  2. Add tests (Task #235)            $2.80                │
│  3. Update docs (Task #236)          $0.50                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Technical Implementation

### Database Schema

```sql
-- Projects (one per folder)
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    git_remote TEXT,
    budget REAL DEFAULT 50.0
);

-- Agents (AI employees)
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    name TEXT NOT NULL,
    role TEXT CHECK(role IN ('coder', 'reviewer')),
    model TEXT,
    status TEXT,
    cost_today REAL DEFAULT 0.0,
    cost_total REAL DEFAULT 0.0
);

-- Tasks (Kanban cards)
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    title TEXT NOT NULL,
    status TEXT CHECK(status IN ('todo', 'doing', 'review', 'done')),
    assignee_id TEXT,
    branch TEXT,
    actual_cost REAL DEFAULT 0.0
);

-- Sessions (agent runs)
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    task_id TEXT,
    agent_id TEXT,
    status TEXT,
    cost REAL DEFAULT 0.0,
    tokens INTEGER DEFAULT 0
);

-- Knowledge (markdown notes)
CREATE TABLE notes (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    title TEXT NOT NULL,
    content TEXT,
    type TEXT,
    file_path TEXT
);
```

### API Endpoints

```
GET    /api/dashboard           # Stats & overview
GET    /api/agents              # List agents
POST   /api/agents              # Create agent
PATCH  /api/agents/:id/status  # Update status

GET    /api/tasks               # List tasks
POST   /api/tasks               # Create task
PATCH  /api/tasks/:id/status    # Update status

GET    /api/notes               # List knowledge
POST   /api/notes               # Create note
PATCH  /api/notes/:id           # Update note

WS     /ws                      # Real-time updates
```

### WebSocket Events

```javascript
// Client receives:
{ type: "agent_created", data: { id, name, status } }
{ type: "task_updated", data: { id, status, cost } }
{ type: "session_started", data: { id, task_id, agent_id } }
{ type: "cost_incurred", data: { amount, total } }
```

---

## 🚀 Usage

### Installation

```bash
# Install kimijang
uv tool install --editable .

# Or from PyPI (future)
pip install kimijang-cli
```

### Commands

```bash
# Initialize console in project
cd my-project
kimijang console init

# Start console
kimijang console                    # Default port 8080
kimijang console --port 3000       # Custom port
kimijang console --no-open         # Don't open browser

# Quick commands (future)
kimijang task create "Fix bug"     # Create task from CLI
kimijang agent list                # List agents
kimijang cost report               # Show spending
```

---

## 🗺️ Roadmap

### Phase 1: MVP ✅
- [x] Dashboard with stats
- [x] Kanban task board
- [x] Agent management
- [x] Knowledge base
- [x] Real-time updates

### Phase 2: Enhanced
- [ ] Git integration (auto-branch, PR creation)
- [ ] Session replay
- [ ] Cost budgets & alerts
- [ ] Task templates
- [ ] Agent skills marketplace

### Phase 3: Advanced
- [ ] Multi-agent pods (teams)
- [ ] Scheduled tasks (cron-like)
- [ ] Integration with GitHub/GitLab
- [ ] Slack notifications
- [ ] Mobile-responsive UI

### Phase 4: Enterprise
- [ ] Multi-user support
- [ ] Team workspaces
- [ ] SSO & RBAC
- [ ] Audit logs
- [ ] Analytics API

---

## 🎨 Design Philosophy

### 1. Project-First
Everything is scoped to a project. No global state, no confusion.

### 2. Git-Native
Branches, commits, PRs are first-class citizens.

### 3. Cost-Visible
Every action shows its price. No surprise bills.

### 4. Knowledge-Persistent
Sessions end, knowledge remains.

### 5. Agent-Accountable
Clear ownership: who did what, when, at what cost.

---

## 🤝 Comparison

| Feature | Claude Code | Cursor | Kimijang Console |
|---------|-------------|--------|------------------|
| Interface | Terminal | IDE | Web Dashboard |
| Sessions | Ephemeral | Ephemeral | Persistent |
| Cost Tracking | ❌ | ❌ | ✅ |
| Task Management | ❌ | ❌ | ✅ Kanban |
| Multi-Agent | ❌ | ❌ | ✅ |
| Knowledge Base | ❌ | ❌ | ✅ |
| MCP Tools | ❌ | ✅ | ✅ |
| Self-Hosted | ✅ | ❌ | ✅ |
| Open Source | ❌ | ❌ | ✅ |

---

## 🛠️ Contributing

### Development Setup

```bash
# Clone
git clone https://github.com/KJ-AIML/kimi-jang-cli.git
cd kimi-jang-cli

# Install backend
uv sync

# Install frontend
cd web-console
npm install
npm run build
cd ..

# Run console
uv run kimijang console
```

### Project Structure

```
src/kimi_cli/console/
├── __init__.py          # Module init
├── app.py               # FastAPI app
├── cli.py               # CLI commands
├── db.py                # SQLite models
├── api/                 # API routes
└── static/              # Built frontend

web-console/
├── src/
│   ├── pages/           # Dashboard, Tasks, Agents, Knowledge
│   ├── components/      # Reusable UI
│   └── lib/             # Utilities
├── package.json
└── vite.config.ts
```

---

## 📜 License

MIT © 2025 Kimijang Contributors

---

## 🙏 Acknowledgments

- **Paperclip** - Inspiration for multi-agent orchestration
- **Kimi Code CLI** - Foundation codebase
- **FastAPI** - Backend framework
- **React** - Frontend library

---

> **"The future of coding is not chatbots. It's organized, measurable, and collaborative AI teams."**
>
> — Kimijang Console Vision
