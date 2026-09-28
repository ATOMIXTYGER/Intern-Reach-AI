# InternReach AI

**InternReach AI** is an AI-assisted recruiting and outreach CRM purpose-built for a **2028 graduating engineering undergraduate** to discover relevant software, data, and AI/ML internships, research legitimate early-careers recruiters from authorized public sources with verified evidence, personalize outreach messages via LLMs, and manage outreach through an uncompromising **human-in-the-loop approval workflow**.

---

## 1. What the Project Does

InternReach AI acts as an intelligent career co-pilot, not a spam bot:
- **Discovers Internship Opportunities**: Continuously scans permitted, public web sources for software, backend, full-stack, AI/ML, and data engineering internships.
- **Verifies Eligibility**: Evaluates whether opportunities are genuine, technical, location-compatible, and explicitly open to sophomore / 2028 batch candidates.
- **Researches Recruiting Contacts**: Identifies campus recruiters, technical sourcers, and hiring managers with verifiable public evidence.
- **Matches Profiles & Resumes**: Analyzes technical skills, projects, and coursework against job requirements for internal prioritization.
- **Personalizes Outreach**: Drafts customized LinkedIn connection requests, InMails, emails, and follow-up notes adhering strictly to anti-spam constraints.
- **Enforces Human-in-the-Loop**: **Nothing is ever sent automatically.** The student reviews, edits, and approves every message, then manually delivers it via permitted channels.
- **Manages Outreach & Follow-Ups**: Warns against duplicate outreach, tracks application stages, and triggers a respectful single 7-day follow-up reminder.

---

## 2. Architecture & LangGraph Pipeline

InternReach AI is organized into a modular monorepo:

```
/internreach-ai
├── /frontend          # Next.js 16 (App Router), TypeScript, Tailwind CSS, Lucide icons
├── /backend           # Python 3.13 FastAPI, Pydantic v2, SQLAlchemy 2.0 Async
│   └── /app
│       ├── /api       # Typed REST routers
│       ├── /agents    # LangGraph StateGraph orchestration & node implementations
│       ├── /core      # Settings, security, bcrypt hashing, logging, prompt boundaries
│       ├── /db        # Async session, models, seed data
│       ├── /models    # 16 SQLAlchemy ORM tables with UUIDs
│       ├── /providers # LLM & Search provider abstractions
│       ├── /schemas   # Strict Pydantic input/output schemas
│       ├── /services  # Domain business logic & parsing
│       └── /utils     # SSRF filter, prompt injection guard, HTML sanitizer
├── /infra             # Dockerfiles & docker-compose configurations
└── /tests             # Comprehensive unit, integration, security, and e2e tests
```

### 10-Node LangGraph StateGraph:
```
START
  ↓
[LoadCandidateProfile]   → Verifies 2028 target graduation & skills
  ↓
[DiscoverOpportunities]  → Scans permitted public job portals
  ↓
[Deduplicate]            → Deterministic URL & (company, title) hashing
  ↓
[VerifyOpportunity]      → Verifies active listing & tech domain
  ↓
[EligibilityCheck]       → Strict graduation cohort compatibility
  ↓
[ResearchContacts]       → Finds campus recruiters with evidence proof
  ↓
[MatchCandidate]         → Calculates skills & project alignment
  ↓
[GenerateOutreach]       → Drafts message using strict base prompt
  ↓
[ValidateOutput]         → Pydantic validation & prompt injection check
  ↓
[HumanApproval]          → Places draft into review queue (Never auto-sent)
  ↓
END
```

---

## 3. Tech Stack

- **Frontend**: Next.js 16 (Turbopack, App Router), React 19, TypeScript, Tailwind CSS, Lucide React, clsx, tailwind-merge.
- **Backend**: Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), `greenlet`, `aiosqlite`, `asyncpg`, `passlib[bcrypt]`, `python-jose`, `bleach`, `pypdf`, `python-docx`.
- **AI Layer**: Provider abstraction (`LLMProvider`) supporting Anthropic Claude (Claude 3.5 Sonnet), Google Gemini (Gemini 1.5 Pro), and MockLLMProvider for offline execution.
- **Agent Orchestration**: LangGraph StateGraph.
- **Search Layer**: Provider abstraction (`SearchProvider`) supporting Tavily Web Search and MockSearchProvider with SSRF protections.
- **Database**: PostgreSQL (Production/Docker) with automatic zero-config SQLite (`sqlite+aiosqlite`) fallback for local development.

---

## 4. Local Setup

### Prerequisites
- Python 3.11+ (Tested on Python 3.13)
- Node.js 18+ (Tested on Node.js 22)
- npm 9+

### Backend Setup
1. Open terminal and navigate to the project root:
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
2. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Initialize database and load rich demo data:
   ```bash
   python -m app.db.seed
   ```
4. Start FastAPI server:
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   API Docs available at: `http://localhost:8000/docs`

### Frontend Setup
1. In a separate terminal, navigate to `frontend`:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
2. Open your browser at `http://localhost:3000`.

---

## 5. Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

| Variable | Description | Default in Mock Mode |
|---|---|---|
| `DATABASE_URL` | Async database URL | `sqlite+aiosqlite:///./internreach.db` |
| `MOCK_MODE` | Runs locally without paid API keys | `true` |
| `PRIMARY_LLM_PROVIDER` | `claude`, `gemini`, or `mock` | `claude` (falls back to mock if key absent) |
| `ANTHROPIC_API_KEY` | Anthropic Claude API Key | Optional in mock mode |
| `GEMINI_API_KEY` | Google Gemini API Key | Optional in mock mode |
| `SEARCH_PROVIDER` | `tavily`, `serp`, or `mock` | `tavily` |
| `SEARCH_PROVIDER_API_KEY`| Tavily Search API Key | Optional in mock mode |
| `JWT_SECRET` | Secret key for JWT session tokens | Configured default |
| `NEXT_PUBLIC_API_URL` | Backend URL for frontend client | `http://localhost:8000/api/v1` |

---

## 6. Database Setup

- **Local Zero-Config (Default)**: SQLite via `sqlite+aiosqlite:///./internreach.db` requires zero installation and is created automatically on backend startup.
- **PostgreSQL**: Set `DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/internreach_db`. Tables are automatically initialized through SQLAlchemy asynchronous migrations.
- **Seed Data**: Run `python -m app.db.seed` to populate 10 companies, 20 verified opportunities, 15 contacts, 10 outreach messages, and 10 tracked applications (all clearly labeled as DEMO DATA).

---

## 7. Docker Setup

To launch the full production-grade stack (PostgreSQL, Redis, FastAPI backend, Next.js frontend):

```bash
docker compose up --build
```

Healthchecks ensure PostgreSQL and Redis are healthy before backend and frontend boot up.
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

---

## 8. LLM Setup

InternReach AI uses a pluggable LLM provider architecture:
- **Anthropic Claude**: Set `PRIMARY_LLM_PROVIDER=claude` and provide `ANTHROPIC_API_KEY`.
- **Google Gemini**: Set `PRIMARY_LLM_PROVIDER=gemini` and provide `GEMINI_API_KEY`.
- **Mock Mode**: When `MOCK_MODE=true` or API keys are omitted, `MockLLMProvider` generates deterministic, high-quality responses that comply strictly with the prompt rules.

---

## 9. Search Provider Setup

- **Tavily Web Search**: Set `SEARCH_PROVIDER=tavily` and provide `SEARCH_PROVIDER_API_KEY`.
- **Mock Search**: When in mock mode, `MockSearchProvider` delivers verified software engineering listings for top tech companies (Razorpay, CRED, Swiggy, Microsoft, Postman, Zomato, etc.).

---

## 10. Running Automated Tests

Run the full automated test suite:

```bash
# From workspace root:
.\.venv\Scripts\python -m pytest tests -v
```

### Test Coverage:
1. `tests/test_auth_and_candidate.py`: Registration, password hashing, JWT authorization, profile editing, and safe PDF resume parsing.
2. `tests/test_eligibility_and_dedup.py`: 2028 graduate verification, non-technical role rejection, and opportunity deduplication.
3. `tests/test_scoring_and_matching.py`: Multi-dimensional matching algorithm (skills, role, eligibility, location, project).
4. `tests/test_message_and_approval.py`: Base prompt compliance, duplicate outreach warnings, human approval, sent tracking, and 7-day follow-up creation.
5. `tests/test_security_hardening.py`: SSRF private IP blocking, XSS sanitization, upload format validation, and prompt injection defense.
6. `tests/test_langgraph_pipeline_e2e.py`: Complete 10-node LangGraph execution test.

---

## 11. Security Hardening

- **SSRF Defense (`app/utils/ssrf.py`)**: Validates every external URL, resolves DNS, and blocks private/loopback/cloud metadata ranges (`127.0.0.0/8`, `169.254.169.254`, `10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12`).
- **Prompt Injection Boundaries (`app/utils/prompt_guard.py`)**: Wraps untrusted external data (job postings, recruiter profiles, resumes) in strict boundary tags (`<SYSTEM_INSTRUCTIONS>`, `<CANDIDATE_DATA>`, `<EXTERNAL_WEB_DATA>`). Neutralizes injection triggers like "ignore previous instructions".
- **Upload Validation (`app/utils/sanitizer.py`)**: Verifies MIME types, file size limits (10MB), and magic byte headers (`%PDF-`, `PK\x03\x04`).
- **XSS & HTML Sanitization**: Uses `bleach` to clean untrusted input.
- **Passwords**: Hashed with bcrypt (12 rounds) and validated via JWT.

---

## 12. Responsible Automation Limitations

InternReach AI enforces strict ethical and legal boundaries:
1. **Never Automates Sending**: The user must explicitly click "Copy Message" and manually send via permitted channels.
2. **No Scraping of Prohibited Platforms**: Contacts and job postings are queried exclusively through permitted, public search endpoints.
3. **No Hallucinations**: Recruiter titles and job requirements must have verified public proof.
4. **Anti-Spam Follow-Up Rules**: Outreach paused for 7 days before generating a single follow-up reminder, followed by outreach closure.

---

## 13. How to Add Another LLM Provider

1. Create a class inheriting from `app.providers.llm.base.LLMProvider`:
   ```python
   # backend/app/providers/llm/mistral_provider.py
   from app.providers.llm.base import LLMProvider

   class MistralProvider(LLMProvider):
       provider_name = "mistral"
       async def generate_text(self, system_prompt, user_prompt, temperature=0.3, max_tokens=1500) -> str:
           # Call Mistral API
           ...
       async def generate_structured(self, system_prompt, user_prompt, schema_class, temperature=0.2):
           # Return validated Pydantic model
           ...
   ```
2. Register the provider in `app/providers/llm/factory.py`.

---

## 14. How to Add Another Search Provider

1. Create a class inheriting from `app.providers.search.base.SearchProvider`:
   ```python
   # backend/app/providers/search/bing_provider.py
   from app.providers.search.base import SearchProvider

   class BingSearchProvider(SearchProvider):
       provider_name = "bing"
       async def search_opportunities(self, roles, locations, companies=None, keywords=None, limit=10):
           ...
       async def search_contacts(self, company_name, target_roles=None, limit=5):
           ...
   ```
2. Register the provider in `app/providers/search/factory.py`.

---

## 15. First Run Experience

1. Start backend and frontend (or launch Docker Compose).
2. Open `http://localhost:3000`. The demo account (`demo.student2028@internreach.ai`) is pre-authenticated.
3. Click **"Find Opportunities"** on the Dashboard or Opportunities page.
4. View verified 2028 eligible internship cards.
5. Click **"View Details & Verification"** on any opportunity to inspect the verification reasons and linked recruiters.
6. Click **"Draft Outreach"** to generate an AI draft.
7. Open **Outreach CRM**: click **"Edit"** or **"Approve"**, then copy the message to send via your authorized LinkedIn account.
8. Click **"Mark Sent"** to record transmission and schedule the 7-day follow-up reminder.
9. Track progress in the **Application Tracker** and **Analytics** dashboard!
