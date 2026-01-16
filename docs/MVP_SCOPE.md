# F&B Operations Agent - MVP Scope

## RÈGLE D'OR MVP

=="If it's not essential to demonstrate value, it's OUT OF SCOPE."==

## IN SCOPE (Must-Have for MVP)

### 1. Prediction Display avec Confidence
- **Description:** Dashboard affiche predicted covers, confidence score (0-100%), et staff recommendation (servers, hosts, kitchen)
- **User flow:** Manager ouvre dashboard → voit "Saturday Nov 30 Dinner: 145 covers (88%)" → voit "Recommended: 8 servers, 2 hosts, 3 kitchen"
- **Critère validation:** Prediction card claire, confidence visualisée (progress bar), staff numbers calculés
- **Effort estimé:** 6h (backend /predict endpoint + frontend PredictionCard component)
- **Pourquoi P0:** Core value prop - sans prediction, pas de produit

### 2. Reasoning Simplifié (Collapsible)
- **Description:** Agent explique confidence score avec raison principale (NOT 3 patterns détaillés)
- **User flow:** Manager voit "88% confidence based on similar Saturday dinners with events nearby" → [View Details] → expand pour voir top 3 patterns
- **Critère validation:** Reasoning par défaut = 1 ligne simple, expand optional
- **Effort estimé:** 4h (au lieu de 6h)
- **Pourquoi SIMPLIFIÉ:** Discovery montre que trop de détails = too complex pour usage quotidien

### 3. Manager Approval Flow
- **Description:** Manager peut approve, reject, ou adjust prediction
- **User flow:** Manager voit prediction → click [Approve] → feedback saved in Supabase → confirmation toast
- **Critère validation:** 3 boutons fonctionnels, feedback enregistré en DB, UI feedback immédiat
- **Effort estimé:** 4h (POST /feedback endpoint + UI buttons + Supabase save)
- **Pourquoi P0:** Human-in-the-loop - démontre "augmented" not "automated"

### 4. Voice Input (Voice-AVAILABLE, pas voice-FIRST)
- **Description:** Manager PEUT parler au lieu de taper (opt-in, pas default)
- **User flow:** Manager voit search bar + floating mic button → click mic si besoin → parle → transcription → agent traite
- **Critère validation:** Voice fonctionne QUAND utilisé, mais keyboard est option par défaut (pas voice overlay auto-open)
- **Effort estimé:** 5h (au lieu de 6h, car pas overlay complexe)
- **Pourquoi ADJUSTED:** Discovery flag environnement bruyant = voice doit être fallback, pas primary

### 5. Command Palette (Ctrl + K Modern UX)
- **Description:** Keyboard-first navigation pour power users (Linear-style)
- **User flow:** Manager press ⌘K → palette opens → type "predict" → fuzzy search → select action → executes
- **Critère validation:** ⌘K shortcut works, fuzzy search functional, 4-5 core actions (predict, view patterns, settings, etc)
- **Effort estimé:** 4h (shadcn/ui Command component + action routing)
- **Pourquoi P1:** Modern UX signal (démontre design thinking), mais pas critique pour core value

**TOTAL IN SCOPE:** 26 heures coding + 20h setup/tests/deploy = **~45-50 heures total**

---

## OUT OF SCOPE (Later Versions)

### Phase 2 (V1 - Post-MVP - 1-2 semaines additional)
- ❌ **Patterns Library (read/write):** Manager peut voir, archiver, weight patterns
- ❌ **Historical Accuracy Dashboard:** Chart predicted vs actual (builds trust over time)
- ❌ **Settings Page:** Restaurant config, notification preferences
- ❌ **Email/Slack notifications:** "New prediction ready for Saturday"

### Phase 3 (V2 - 2-3 semaines additional)
- ❌ **Auto-push to 7shifts:** Approved predictions → auto-create shifts (requires 7shifts API integration)
- ❌ **F&B Inventory Integration:** Extend predictions to food/beverage ordering (MarketMan API)
- ❌ **Multi-day predictions:** "Predict next week" (7 predictions at once)
- ❌ **Weather integration:** Real-time weather impact (OpenWeather API)

### Phase 4 (Enterprise - 2-3 mois)
- ❌ **Multi-restaurant support:** Tenant isolation, billing (Stripe), admin dashboard
- ❌ **Learning loop automation:** Post-service data collection → model retraining
- ❌ **White-label options:** Custom branding for hotel chains
- ❌ **SSO / RBAC:** Enterprise auth (manager vs owner roles)
- ❌ **API for 3rd parties:** Public API for integrations

---

## SCOPE CONSTRAINTS

**Technical constraints:**
- 1 restaurant only (no multi-tenancy)
- Mock data acceptable for PredictHQ (real API = nice-to-have)
- No real 7shifts integration (display recommendations only)
- Desktop-first (mobile responsive = stretch goal)

**Time constraints:**
- Total dev time: 3 semaines (45-50 heures effort)
- Must be demo-able by [DATE: +3 semaines from today]
- Must be portfolio-ready (GitHub public, README, demo video)

**Resource constraints:**
- Solo developer (toi)
- Budget: <$50/month (APIs, hosting free tiers)
- Tools: Cursor Pro, Warp Pro, Figma Free, Supabase Free, Qdrant Free, Vercel Free

---

## DECISION FRAMEWORK

Pour chaque feature idea, ask:

1. **Is it essential to demonstrate value?**
   - YES → Consider for MVP
   - NO → Backlog

2. **Can I build it in <8 hours?**
   - YES → Consider for MVP
   - NO → Break down or defer

3. **Does it need real APIs?**
   - YES → Can I mock it? If yes, mock. If no, defer.
   - NO → Include in MVP

4. **Will Mews PM be impressed by this?**
   - YES → Prioritize
   - NO → Backlog

---

## MVP FEATURES FINAL LIST (Ranked)

| Priority | Feature | Effort | Impact | Decision |
|----------|---------|--------|--------|----------|
| P0 | Prediction Display | 6h | HIGH | ✅ IN |
| P0 | Reasoning & Sources | 6h | HIGH | ✅ IN |
| P0 | Approval Flow | 4h | HIGH | ✅ IN |
| P1 | Voice Input | 6h | HIGH | ✅ IN |
| P1 | Command Palette ⌘K | 4h | MEDIUM | ✅ IN |
| P2 | Patterns Library | 4h | MEDIUM | ❌ OUT (V2) |
| P2 | Historical Accuracy | 4h | MEDIUM | ❌ OUT (V2) |
| P2 | Settings Page | 3h | LOW | ❌ OUT (V2) |
| P3 | Auto-push 7shifts | 12h | HIGH | ❌ OUT (V2) |
| P3 | Multi-restaurant | 20h | HIGH | ❌ OUT (V3) |
| P3 | Learning loop | 15h | HIGH | ❌ OUT (V3) |

**Total MVP effort (IN SCOPE):** 26h coding + 20h setup/polish = **45-50 heures**

---

## COMMITMENT & ACCOUNTABILITY

**Je m'engage à :**
- ✅ Ne PAS ajouter features pendant développement (scope creep = ennemi #1)
- ✅ Si feature prend >8h → break down ou defer to V2
- ✅ Tester chaque feature individuellement (pas Big Bang integration)
- ✅ Déployer early & often (backend Jour 9, frontend Jour 19)

**Success criteria:**
- MVP demo-able en 3 semaines
- Core value prop claire (staffing prediction + reasoning)
- Voice-first UX démontrée (différentiation)
- Code quality suffisante pour portfolio (tests, docs, clean structure)
```

---

## ✅ CHECKPOINT FINAL TASK 1.2
```
□ IN SCOPE limité à 5 features (P0 + P1)
□ Effort total estimé: 45-50 heures (réaliste pour 3 semaines)
□ OUT OF SCOPE clairement documenté (V2, V3, Enterprise)
□ Decision framework défini (4 questions)
□ Feature table avec priorités remplie
□ Commitment section signée mentalement
□ Git commit fait