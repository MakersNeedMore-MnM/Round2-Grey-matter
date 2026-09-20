# TRACE — AI Reunification & Claim Verification Engine

> **"An AI reunification engine — built to find the match, and prove it belongs to the right person."**  
> **Team Grey Matter**: Niviya Albert, Adithyan M J, Diya Paramanand  
> **Competition Track**: MakersNeedMore (MnM) — Round 2

---

## 1. Overview

**TRACE** is a decision-support platform designed for institutional lost-and-found desks (railway lost property offices, airport counters, campus security) to solve two core challenges:

1. **Multi-Modal Fusion Matching**: Finds matches even when passenger descriptions and staff wording diverge (e.g., *"navy blue backpack"* vs *"black rucksack"*), by fusing **Visual** (CLIP embeddings), **Semantic Text** (Sentence-Transformers MiniLM), **Station Zone Adjacency**, and **Time Proximity**.
2. **Anti-Fraud Claim Verification**: Eliminates fraudulent and mistaken handoffs by vaulting a hidden distinguishing detail at intake and auto-generating a challenge question that claimant responses are verified against before physical release.

---

## 2. Key Capabilities & Differentiators

- **Visible Product Differentiation (Priority 1)**: Live interactive toggle between **Legacy Keyword Search** (fails with 0 matches on vocabulary mismatches) vs **TRACE AI Fusion** (surfaces the true match with ~81% confidence).
- **100% Offline Resilience (Priority 2)**: Both CLIP and MiniLM models are cached and pre-warmed into memory at startup, requiring **zero network calls** during live judging or offline demo rehearsals.
- **Explainable AI Decision Driver (Priority 3)**: Plain-language explanation generated directly alongside component scores (e.g., *"Matched primarily on photo similarity, despite different wording"*).
- **Handover Audit Receipt**: Generates a verifiable, timestamped audit signature upon authorized release.

---

## 3. System Architecture

```
                                  +-----------------------+
                                  |   Staff Desk (Web)    |
                                  |      Streamlit        |
                                  +-----------+-----------+
                                              |
                                              v
+-----------------------------------------------------------------------------------+
|                              FastAPI REST Backend                                 |
|                                                                                   |
|  [POST /found-items]        [GET /found-items/{id}/matches]  [POST /lost-reports] |
|  [POST /found-items/{id}/challenge]   [POST /challenges/{id}/answer]              |
|  [GET /dashboard/queue]                                                           |
+------------------------------------+----------------------------------------------+
                                     |
                +--------------------+--------------------+
                |                                         |
                v                                         v
+-------------------------------+       +-----------------------------------+
|      Multi-Modal Scoring      |       |      Anti-Fraud Verification      |
|                               |       |                                   |
| • Visual: CLIP ViT-B/32 (40%) |       | • Vaulted Hidden Attribute        |
| • Text: MiniLM-L6-v2 (30%)    |       | • Generic Question Generator      |
| • Location Zone Matrix (15%)  |       | • Keyword-Presence Validator      |
| • 14-Day Time Decay (15%)     |       | • Green/Red Decision Flagging     |
| • No-Photo Weight Re-norm     |       | • Handover Audit Receipt          |
| • Keyword Baseline Toggle     |       +-----------------------------------+
| • Plain-Language Driver Line  |
+---------------+---------------+
                |
                v
+-------------------------------+
|         SQLite Storage        |
|  • Found Items                |
|  • Lost Reports               |
|  • Claim Challenges           |
+-------------------------------+
```

---

## 4. 60-Second Demo Walkthrough

1. **Intake (Screen 1)**: Click **"Demo 1: Mismatched Wording"** from the left sidebar to pre-fill a found *"Navy blue canvas backpack"* with photo and hidden detail. Click **"Log Item & Search Open Lost Reports"**.
2. **Match (Screen 2)**: 
   - Toggle to **"🔍 Legacy Keyword Search"** → Point out that it returns **0 MATCHES** due to vocabulary divergence.
   - Toggle to **"⚡ TRACE AI Multi-Modal Fusion"** → Show that Lost Report #1 (*"Black rucksack with dual straps"*) immediately surfaces as the **#1 Top Match (~81% confidence)**.
   - Point out the **AI Decision Driver**: *"Matched primarily on photo similarity, despite different wording."*
   - Click **"Proceed to Claim Verification"**.
3. **Verify (Screen 3)**:
   - Click **"Load False / Fraudulent Claim"** → Click **"Evaluate"** → See instant **Red "Flagged for Staff Review"**.
   - Click **"Load Genuine Claimant Answer"** → Click **"Evaluate"** → See instant **Green "Match Confirmed"**.
   - Click **"Authorize & Confirm Physical Release"** to generate the official audit receipt.

---

## 5. Quick Start

### Installation & Launch
```bash
# 1. Install dependencies
py -m pip install -r requirements.txt

# 2. Run both Backend and Frontend together
py run.py
```

- **Staff Dashboard**: [http://localhost:8501](http://localhost:8501)
- **FastAPI Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Run Automated Tests
```bash
py test_trace.py
```
