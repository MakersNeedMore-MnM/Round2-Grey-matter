import os
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backend.database import get_db, BASE_DIR
from backend.models import FoundItem, LostReport, ClaimChallenge
from backend.schemas import (
    FoundItemCreate,
    FoundItemResponse,
    LostReportCreate,
    LostReportResponse,
    MatchResultResponse,
    ChallengeResponse,
    ChallengeAnswerRequest,
    ChallengeAnswerResponse,
    DashboardQueueItem,
)
from backend.scoring import compute_fused_score
from backend.verification import generate_challenge_question, verify_claim_answer
from backend.embeddings import warmup_embeddings
from backend.seed import init_db as run_seed_init

app = FastAPI(
    title="TRACE Backend API",
    description="AI-powered lost-and-found matching and claim verification engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOADS_DIR = os.path.join(BASE_DIR, "data", "uploads")
SEED_IMAGES_DIR = os.path.join(BASE_DIR, "data", "seed", "images")
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(SEED_IMAGES_DIR, exist_ok=True)

app.mount("/static/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.mount("/static/seed", StaticFiles(directory=SEED_IMAGES_DIR), name="seed_images")


@app.on_event("startup")
def on_startup():
    run_seed_init()
    warmup_embeddings()


# 1. POST /found-items
@app.post("/found-items", response_model=FoundItemResponse, status_code=status.HTTP_201_CREATED)
async def create_found_item(
    description: str = Form(...),
    location: str = Form(...),
    hidden_attribute: str = Form(...),
    key_terms: Optional[str] = Form(None),
    found_at: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    photo_preset_path: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Log a found item with photo upload, description, location, time, and hidden attribute."""
    saved_photo_path = ""
    if photo and photo.filename:
        filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{photo.filename}"
        saved_photo_path = os.path.join(UPLOADS_DIR, filename)
        with open(saved_photo_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
    elif photo_preset_path and os.path.exists(photo_preset_path):
        saved_photo_path = photo_preset_path
    else:
        saved_photo_path = os.path.join(SEED_IMAGES_DIR, "found_navy_backpack.jpg")

    parsed_found_at = datetime.utcnow()
    if found_at:
        try:
            parsed_found_at = datetime.fromisoformat(found_at.replace("Z", "+00:00"))
        except Exception:
            parsed_found_at = datetime.utcnow()

    item = FoundItem(
        photo_path=saved_photo_path,
        description=description,
        location=location,
        found_at=parsed_found_at,
        hidden_attribute=hidden_attribute,
        key_terms=key_terms,
        status="open",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# 2. GET /found-items/{id}/matches
@app.get("/found-items/{id}/matches", response_model=List[MatchResultResponse])
def get_found_item_matches(id: int, db: Session = Depends(get_db)):
    """Returns top 5 ranked MatchResult list against open lost reports with broken-out component scores."""
    found_item = db.query(FoundItem).filter(FoundItem.id == id).first()
    if not found_item:
        raise HTTPException(status_code=404, detail=f"Found item with id {id} not found")

    lost_reports = db.query(LostReport).filter(LostReport.status == "open").all()
    results = []

    for lr in lost_reports:
        scores = compute_fused_score(
            found_description=found_item.description,
            found_location=found_item.location,
            found_at=found_item.found_at,
            found_photo_path=found_item.photo_path,
            lost_description=lr.description,
            lost_location=lr.location,
            lost_at=lr.lost_at,
            lost_photo_path=lr.photo_path,
        )

        match_res = MatchResultResponse(
            found_item_id=found_item.id,
            lost_report_id=lr.id,
            lost_report=LostReportResponse.model_validate(lr),
            visual_score=scores["visual_score"],
            text_score=scores["text_score"],
            location_score=scores["location_score"],
            time_score=scores["time_score"],
            fused_score=scores["fused_score"],
            keyword_score=scores.get("keyword_score", 0.0),
            has_photo=scores["has_photo"],
            explanation=scores["explanation"],
            driver_explanation=scores.get("driver_explanation", ""),
        )
        results.append(match_res)

    # Sort descending by fused_score and take top 5
    results.sort(key=lambda m: m.fused_score, reverse=True)
    return results[:5]


# 3. POST /lost-reports
@app.post("/lost-reports", response_model=LostReportResponse, status_code=status.HTTP_201_CREATED)
def create_lost_report(report_in: LostReportCreate, db: Session = Depends(get_db)):
    """Log a lost report."""
    report = LostReport(
        photo_path=report_in.photo_path,
        description=report_in.description,
        location=report_in.location,
        lost_at=report_in.lost_at or datetime.utcnow(),
        status="open",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


# 4. POST /found-items/{id}/challenge
@app.post("/found-items/{id}/challenge", response_model=ChallengeResponse)
def create_item_challenge(id: int, db: Session = Depends(get_db)):
    """Auto-generate a challenge question from the hidden attribute."""
    found_item = db.query(FoundItem).filter(FoundItem.id == id).first()
    if not found_item:
        raise HTTPException(status_code=404, detail=f"Found item with id {id} not found")

    question_text = generate_challenge_question(
        hidden_attribute=found_item.hidden_attribute,
        item_description=found_item.description,
    )

    challenge = ClaimChallenge(
        found_item_id=found_item.id,
        question_text=question_text,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge


# 5. POST /challenges/{id}/answer
@app.post("/challenges/{id}/answer", response_model=ChallengeAnswerResponse)
def answer_challenge(id: int, answer_data: ChallengeAnswerRequest, db: Session = Depends(get_db)):
    """Submit claimant's answer and perform deterministic keyword-presence claim verification."""
    challenge = db.query(ClaimChallenge).filter(ClaimChallenge.id == id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail=f"Challenge with id {id} not found")

    found_item = db.query(FoundItem).filter(FoundItem.id == challenge.found_item_id).first()
    if not found_item:
        raise HTTPException(status_code=404, detail="Associated found item not found")

    verification_result = verify_claim_answer(
        claimant_answer=answer_data.answer,
        hidden_attribute=found_item.hidden_attribute,
        pre_tagged_terms=found_item.key_terms,
    )

    challenge.claimant_answer = answer_data.answer
    challenge.is_match = verification_result["is_match"]
    challenge.resolved_at = datetime.utcnow()

    # Update item status if claimant verified
    if challenge.is_match:
        found_item.status = "claimed"

    db.commit()
    db.refresh(challenge)

    return ChallengeAnswerResponse(
        id=challenge.id,
        found_item_id=found_item.id,
        question_text=challenge.question_text,
        claimant_answer=challenge.claimant_answer or "",
        is_match=challenge.is_match,
        matched_keywords=verification_result["matched_keywords"],
        expected_keywords=verification_result["expected_keywords"],
        resolved_at=challenge.resolved_at,
        message=verification_result["message"],
    )


# 6. GET /dashboard/queue
@app.get("/dashboard/queue", response_model=List[DashboardQueueItem])
def get_dashboard_queue(db: Session = Depends(get_db)):
    """Returns all open found items with their top match for the staff queue view."""
    found_items = db.query(FoundItem).order_by(FoundItem.found_at.desc()).all()
    queue = []

    for item in found_items:
        matches = get_found_item_matches(item.id, db)
        top_match = matches[0] if matches else None
        queue.append(
            DashboardQueueItem(
                found_item=FoundItemResponse.model_validate(item),
                top_match=top_match,
                matches_count=len(matches),
            )
        )

    return queue
