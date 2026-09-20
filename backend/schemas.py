from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class FoundItemBase(BaseModel):
    description: str
    location: str
    found_at: Optional[datetime] = None
    hidden_attribute: str
    key_terms: Optional[str] = None


class FoundItemCreate(FoundItemBase):
    pass


class FoundItemResponse(FoundItemBase):
    id: int
    photo_path: str
    status: str
    found_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LostReportBase(BaseModel):
    description: str
    location: str
    lost_at: Optional[datetime] = None
    photo_path: Optional[str] = None


class LostReportCreate(LostReportBase):
    pass


class LostReportResponse(LostReportBase):
    id: int
    status: str
    lost_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MatchResultResponse(BaseModel):
    found_item_id: int
    lost_report_id: int
    lost_report: LostReportResponse
    visual_score: float
    text_score: float
    location_score: float
    time_score: float
    fused_score: float
    has_photo: bool
    explanation: Optional[str] = None


class ChallengeResponse(BaseModel):
    id: int
    found_item_id: int
    question_text: str

    model_config = ConfigDict(from_attributes=True)


class ChallengeAnswerRequest(BaseModel):
    answer: str


class ChallengeAnswerResponse(BaseModel):
    id: int
    found_item_id: int
    question_text: str
    claimant_answer: str
    is_match: bool
    matched_keywords: List[str]
    expected_keywords: List[str]
    resolved_at: datetime
    message: str


class DashboardQueueItem(BaseModel):
    found_item: FoundItemResponse
    top_match: Optional[MatchResultResponse] = None
    matches_count: int = 0
