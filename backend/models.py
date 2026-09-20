from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database import Base


class FoundItem(Base):
    __tablename__ = "found_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    photo_path = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String, nullable=False)
    found_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    hidden_attribute = Column(Text, nullable=False)
    key_terms = Column(String, nullable=True)  # Comma-separated key terms for challenge checking
    status = Column(String, default="open", nullable=False)  # "open", "claimed", "released"

    challenges = relationship("ClaimChallenge", back_populates="found_item", cascade="all, delete-orphan")


class LostReport(Base):
    __tablename__ = "lost_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    photo_path = Column(String, nullable=True)  # Can be null/empty if report lacks photo
    description = Column(Text, nullable=False)
    location = Column(String, nullable=False)
    lost_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, default="open", nullable=False)  # "open", "matched", "resolved"


class ClaimChallenge(Base):
    __tablename__ = "claim_challenges"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    found_item_id = Column(Integer, ForeignKey("found_items.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    claimant_answer = Column(Text, nullable=True)
    is_match = Column(Boolean, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    found_item = relationship("FoundItem", back_populates="challenges")
