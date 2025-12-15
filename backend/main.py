# -*- coding: utf-8 -*-
# IMPORT UTF-8 CONFIG FIRST - before any other imports
import utf8_config  # noqa: F401

import sys
import io

import uuid
from datetime import datetime
from fastapi import HTTPException

"""
F&B Operations Agent - FastAPI Backend
MVP Phase 1 - Entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="F&B Operations Agent API",
    description="AI-powered staffing forecasting for restaurants",
    version="0.1.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "F&B Operations Agent API",
        "status": "Phase 1 - Backend Development",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/test/claude")
async def test_claude():
    """Test Claude API connection"""
    from utils.claude_client import ClaudeClient
    async with ClaudeClient() as client:
        return await client.test_connection()

@app.get("/test/qdrant")
async def test_qdrant():
    """Test Qdrant connection"""
    from utils.qdrant_client import QdrantManager
    client = QdrantManager()
    return await client.test_connection()

# ============================================
# PHASE 1: Prediction Endpoints
# ============================================

from models.schemas import (
    PredictionRequest,
    PredictionResponse,
    Reasoning,
    StaffRecommendation,
    StaffDelta
)
from agents.demand_predictor import get_demand_predictor

@app.post("/predict", response_model=PredictionResponse)
async def create_prediction(request: PredictionRequest):
    """
    Create a staffing prediction
    
    Phase 1: Basic prediction (mocked data)
    Phase 2: Full integration (real patterns, APIs)
    """
    try:
        # Get demand predictor
        predictor = get_demand_predictor()
        
        # Generate prediction
        result = await predictor.predict(request)
        
        # TODO Hour 3-4: Add reasoning engine + staff recommender
        # For now, return basic structure
        
        # Extract reasoning from predictor result (now includes Claude-generated reasoning)
        reasoning_data = result.get("reasoning", {})
        
        reasoning = Reasoning(
            summary=reasoning_data.get("summary", f"{int(result['confidence']*100)}% confidence"),
            patterns_used=reasoning_data.get("patterns_used", [])[:3],  # Top 3 patterns
            confidence_factors=reasoning_data.get("confidence_factors", ["Historical patterns"])
        )
        
        # Create StaffRecommendation object
        staff_recommendation = StaffRecommendation(
            servers=StaffDelta(recommended=8, usual=7, delta=1),
            hosts=StaffDelta(recommended=2, usual=2, delta=0),
            kitchen=StaffDelta(recommended=3, usual=3, delta=0)
        )
        
        # Return PredictionResponse
        return PredictionResponse(
            prediction_id=f"pred_{uuid.uuid4().hex[:8]}",
            service_date=request.service_date,
            service_type=request.service_type,
            predicted_covers=result["predicted_covers"],
            confidence=result["confidence"],
            reasoning=reasoning,
            staff_recommendation=staff_recommendation,
            created_at=datetime.utcnow().isoformat() + "Z"
        )
        
    except Exception as e:
        # Safely encode error message to avoid encoding issues
        error_detail = str(e).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        raise HTTPException(status_code=500, detail=error_detail)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)