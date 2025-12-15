# -*- coding: utf-8 -*-
"""
Data schemas for F&B Operations Agent
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum


class ServiceType(str, Enum):
    """Service type enum"""
    LUNCH = "lunch"
    DINNER = "dinner"
    BRUNCH = "brunch"


class PredictionRequest(BaseModel):
    """Request model for prediction endpoint"""
    restaurant_id: str = Field(..., description="Restaurant identifier")
    service_date: date = Field(..., description="Date of service (YYYY-MM-DD)")
    service_type: ServiceType = Field(..., description="Type of service")
    
    class Config:
        json_schema_extra = {
            "example": {
                "restaurant_id": "resto_123",
                "service_date": "2024-12-15",
                "service_type": "dinner"
            }
        }


class Pattern(BaseModel):
    """Similar pattern from history"""
    pattern_id: str
    date: date
    event_type: Optional[str] = None
    actual_covers: int
    similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity score 0-1")
    metadata: dict = Field(default_factory=dict)


class Reasoning(BaseModel):
    """Reasoning explanation for prediction"""
    summary: str = Field(..., description="One-line explanation")
    patterns_used: List[Pattern] = Field(default_factory=list)
    confidence_factors: List[str] = Field(default_factory=list)


class StaffDelta(BaseModel):
    """Staff delta comparison"""
    recommended: int
    usual: int
    delta: int
    rationale: Optional[str] = None


class StaffRecommendation(BaseModel):
    """Staff recommendation breakdown"""
    servers: StaffDelta
    hosts: StaffDelta
    kitchen: StaffDelta


class PredictionResponse(BaseModel):
    """Response model for prediction endpoint"""
    prediction_id: str
    service_date: date
    service_type: ServiceType
    predicted_covers: int
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: Reasoning
    staff_recommendation: StaffRecommendation
    created_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "prediction_id": "pred_abc123",
                "service_date": "2024-12-15",
                "service_type": "dinner",
                "predicted_covers": 145,
                "confidence": 0.88,
                "reasoning": {
                    "summary": "88% confidence based on similar Saturday dinners with events nearby",
                    "patterns_used": [],
                    "confidence_factors": ["Similar day of week", "Nearby event"]
                },
                "staff_recommendation": {
                    "servers": {"recommended": 8, "usual": 7, "delta": 1},
                    "hosts": {"recommended": 2, "usual": 2, "delta": 0},
                    "kitchen": {"recommended": 3, "usual": 3, "delta": 0}
                },
                "created_at": "2024-12-02T18:00:00Z"
            }
        }