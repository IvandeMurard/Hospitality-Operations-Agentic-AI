# F&B Operations Agent – MVP

**Portfolio case study to gain AI product management and agentic design expertise**

## 📊 Problem

1. Hotel & restaurant teams spend **5–8h/week** building staffing plans with **limited forecast accuracy**, instead of focusing on guests and operations.  
2. Core systems (PMS, RMS, POS, WFM) are rarely well integrated, so revenue forecasts and staffing/inventory decisions live in silos rather than feeding each other.  

## 🎯 Project Vision

Build an AI **decision engine** for hotel F&B operations that:

- Connects to existing systems (PMS, RMS, POS, WFM) instead of replacing them  
- Predicts demand (covers, sales, activity) using:
  - External context: events, weather, holidays  
  - Historical patterns: vector search with Qdrant  
  - Internal hotel data: PMS occupancy, bookings, POS data (Phase 2)  
- Generates **staffing & F&B recommendations** that can be pushed into existing workforce management tools (e.g. HotSchedules)  
- Uses LLM reasoning to provide **explainable predictions and “what-if” scenarios** for managers  
- Exposes a **conversational agent** interface-first solution rather than “yet another dashboard”, with:
  - Minimal UI for traceability, audit, and multi-site monitoring
  - On-demand views only for when managers need to inspect or challenge the reasoning  

Core principle: **Augmented hospitality**. AI handles forecasting, data stitching, and suggestions; managers keep control, make the final call, and focus on high-value human interactions with guests and teams.

## 🏗️ Tech Stack

**Frontend:**
- Next.js 14 + TypeScript
- shadcn/ui + Tailwind CSS

**Backend:**
- FastAPI + Python 3.11

**AI/ML:**
- Claude Sonnet 4 (Anthropic)
- Qdrant Cloud (vector DB)
- ElevenLabs (voice)

**Data:**
- Supabase (PostgreSQL)
- Redis (session state)

## 🚀 Status

✅ **Phase 0: Strategic Preparation** (Complete - 10.5h)  
🚧 **Phase 1: Backend Development** - 64% complete (7/11 issues)
**Phase 2 - Integrations and Advanced Features**

## 📚 Documentation

- **[Problem Statement](docs/Problem_Statement.md)** - Staffing forecasting problem, persona, metrics
- **[MVP Scope](docs/MVP_SCOPE.md)** - 5 core features, 43h effort, IN/OUT scope
- **[Technical Architecture](docs/ARCHITECTURE.md)** - System design, APIs, integrations, scalability
- **[Cost Model](docs/Cost_Model.md)** - $6.65/month MVP, scale economics
- **[Phase 0 Review](docs/PHASE_0_REVIEW.md)** - Validation checklist, Go/No-Go decision

## 🔗 Links
- Linear Project: https://linear.app/ivanportfolio/project/fandb-agent-640279ce7d36
- GitHub Repo: https://github.com/IvandeMurard/fb-agent-mvp
- Figma Mockups: [Link to Figma] (to add)
- Live Demo: (Phase 1 deployment pending)

## 👨‍💻 Author

**Ivan de Murard**  
[Portfolio](https://ivandemurard.lovable.app) • [LinkedIn](https://linkedin.com/in/ivandemurard)

## 📄 License
MIT License - See LICENSE for details

## Last updated: January 7, 2026
Status: Phase 1 MVP in progress (64% complete)

---
