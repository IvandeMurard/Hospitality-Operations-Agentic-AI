# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**F&B Operations Agent** - An AI-powered staffing prediction system for restaurant and hospitality F&B managers.

### Core Problem
Transforms manual staffing forecasting (70% accuracy, 5-8h/week) into AI-powered predictions (85%+ accuracy, <2h/week) by integrating:
- Historical pattern analysis via vector similarity (Qdrant)
- Local events data (PredictHQ API)
- Weather forecasts
- Seasonal and temporal patterns

### Primary Persona
F&B/Operations Manager at mid-high end restaurants (80-150 covers/service), moderately tech-savvy, needs confident data-backed staffing decisions before major events.

### North Star Metric
**Staffing prediction accuracy:** 85%+ (vs 70% baseline with manual methods)
- Measured by comparing predicted covers vs actual POS data

## Architecture Vision

### MVP Phase (Current)
Voice-first conversational interface for staffing forecasting:
- **Voice Interface:** ElevenLabs Conversational AI
- **LLM:** Mistral (cost-efficient: $1/1M tokens)
- **Vector DB:** Qdrant (pattern similarity matching)
- **External APIs:** PredictHQ (events), Weather API
- **Data Source:** POS system integration for historical covers

### Future Phases
- **Phase 2:** F&B inventory optimization (demand prediction, waste reduction)
- **Phase 3:** Multi-domain operations platform (logistics, equipment, rooms)

## Key Design Principles

### Explainable AI
Never use black-box predictions. Always show reasoning:
- Display 3-5 similar historical patterns
- Explain which factors influenced the prediction (events, weather, seasonality)
- Show confidence levels with predictions

### Augmented Human Decision-Making
Manager retains final control:
- Predictions are suggestions, not automatic actions
- One-click approval with manual adjustment capability
- Build trust through transparency

### Voice-First UX
Manager can interact hands-free during service:
- Natural language queries: "predict Saturday dinner"
- Conversational explanations of reasoning
- Quick validation/approval flow

### Hospitality-Specific
Not generic forecasting:
- Understands restaurant-specific patterns (day of week, service type)
- Factors in proximity-based event impact (5km radius)
- Accounts for guest behavior patterns unique to F&B

## Data Flow Architecture

### Prediction Pipeline
1. **Historical Pattern Retrieval:** Query Qdrant for similar past scenarios using vector embeddings (day type, season, occupancy)
2. **Event Enrichment:** PredictHQ API for concerts, festivals, sports events within 5km
3. **Weather Context:** Weather API for forecast conditions
4. **LLM Synthesis:** Mistral generates prediction with confidence score and reasoning
5. **Manager Review:** Voice/visual interface presents prediction with explainability
6. **Validation Loop:** Post-service POS data updates accuracy metrics

### Data Privacy
- No sensitive guest PII stored
- Only aggregate metrics (covers, timestamps, revenue bands)
- Manager identity and restaurant metadata kept minimal

## Development Notes

### Cost Optimization
Target <$10/restaurant/month for MVP viability:
- Prefer Mistral over OpenAI for LLM calls
- Use Qdrant free tier (generous for single-restaurant use case)
- Cache weather/event data aggressively
- Batch POS data syncs (daily, not real-time)

### Accuracy Measurement
Implement systematic tracking:
- Store predictions with timestamps and confidence scores
- Compare against actual POS covers post-service
- Calculate rolling accuracy metrics (weekly, monthly)
- Flag prediction errors >20% for model refinement

### Event API Integration
PredictHQ critical for accuracy:
- Focus on attended events (concerts, sports) not virtual
- Use PHQ Rank/attendance estimates for weighting
- 5km radius configurable per restaurant location
- Cache events for cost control

### Vector Similarity Design
Qdrant embeddings should capture:
- Temporal features: day of week, month, holiday proximity
- Operational features: covers, service type, duration
- External features: event presence, weather conditions, season
- Use cosine similarity to find top 5 historical matches

## Testing Strategy

### Accuracy Validation
- Requires real historical POS data for meaningful testing
- Minimum 6 months of historical data for pattern recognition
- Test against known scenarios (major past events)
- Compare agent predictions vs manager's original decisions

### Voice Interface Testing
- Test interruption handling during busy service times
- Verify multi-turn conversation flow for clarifications
- Ensure hands-free usability with background noise
- Test error recovery when API calls fail

### API Resilience
- Handle PredictHQ rate limits gracefully
- Cache weather forecasts (update 2x daily max)
- Fallback to historical-only predictions if APIs unavailable
- Never block manager workflow on external API failures

## Integration Points

### POS Systems (Future)
Target integrations for cover data:
- Toast, Square, Lightspeed, Clover (common mid-market)
- Daily batch sync sufficient (not real-time)
- Only need: covers count, timestamp, revenue band

### Scheduling Tools (Phase 2)
Post-MVP auto-push to:
- 7shifts, When I Work, Homebase
- Requires staffing ratio logic (covers → headcount)

### Manager Communication
- Voice interface primary (ElevenLabs)
- Dashboard/web view secondary for detailed review
- Mobile-first design (managers on the floor)

## Current Repository State

This repository is in the initial planning phase. The Problem_Statement.md in docs/ contains the full product vision, market analysis, and success metrics.

When beginning implementation, prioritize:
1. POS data ingestion pipeline (historical covers)
2. Qdrant vector store setup with embedding strategy
3. LLM prompt engineering for explainable predictions
4. Simple CLI/voice prototype before full interface
