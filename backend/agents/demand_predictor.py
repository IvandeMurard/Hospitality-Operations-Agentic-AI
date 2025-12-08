"""
Demand Predictor Agent
Predicts restaurant covers based on patterns, events, weather
"""

# Ensure UTF-8 encoding before any prints
import sys
import io
if hasattr(sys.stdout, 'buffer') and sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer') and sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import uuid

from models.schemas import (
    PredictionRequest,
    Pattern,
    ServiceType
)
from utils.claude_client import get_claude_client


class DemandPredictorAgent:
    """
    Agent responsible for predicting restaurant demand (covers)
    
    Uses:
    - Historical pattern matching (Qdrant vector search)
    - External context (events, weather)
    - Claude AI for reasoning
    """
    
    def __init__(self):
        """Initialize predictor agent"""
        # Claude client is optional for MVP (using mocked data)
        self.claude = get_claude_client()
        # TODO: Add Qdrant client when ready
        # self.qdrant = get_qdrant_client()
    
    async def predict(self, request: PredictionRequest) -> Dict:
        """
        Main prediction method
        
        Args:
            request: PredictionRequest with restaurant_id, service_date, service_type
            
        Returns:
            Dict with predicted_covers, confidence, patterns
        """
        print(f"[PREDICT] Starting prediction for {request.restaurant_id} on {request.service_date} ({request.service_type})")
        
        # Step 1: Fetch external context
        context = await self._fetch_external_context(request)
        
        # Step 2: Find similar patterns
        similar_patterns = await self._find_similar_patterns(request, context)
        
        # Step 3: Calculate prediction
        prediction = await self._calculate_prediction(similar_patterns, context)
        
        return prediction
    
    async def _fetch_external_context(self, request: PredictionRequest) -> Dict:
        """
        Fetch external context: events, weather, holidays
        
        Phase 1: MOCKED data (no real APIs yet)
        Phase 2: Integrate PredictHQ, Weather API
        """
        print("  [CONTEXT] Fetching external context...")
        
        # Mock data for MVP
        context = {
            "day_of_week": request.service_date.strftime("%A"),
            "events": [
                {
                    "type": "Concert",
                    "name": "Coldplay Concert",
                    "distance_km": 3.2,
                    "expected_attendance": 50000
                }
            ] if request.service_date.weekday() == 5 else [],  # Saturday only
            "weather": {
                "condition": "Clear" if request.service_date.weekday() < 5 else "Rain",
                "temperature": 18
            },
            "is_holiday": False  # Could check calendar
        }
        
        print(f"  [CONTEXT] OK - {context['day_of_week']}, {len(context['events'])} events")
        return context
    
    async def _find_similar_patterns(
        self, 
        request: PredictionRequest, 
        context: Dict
    ) -> List[Pattern]:
        """
        Find similar historical patterns using vector search
        
        Phase 1: MOCKED patterns (no Qdrant yet)
        Phase 2: Real Qdrant vector search with embeddings
        """
        print("  [PATTERNS] Finding similar patterns...")
        
        # Mock patterns for MVP
        # In reality: embed context → Qdrant search → top 3 patterns
        mock_patterns = [
            Pattern(
                pattern_id="pat_001",
                date=datetime(2023, 11, 18).date(),
                event_type="Concert (Coldplay)",
                actual_covers=142,
                similarity=0.94,
                metadata={
                    "day_of_week": "Saturday",
                    "weather": "Clear",
                    "distance_km": 3.2
                }
            ),
            Pattern(
                pattern_id="pat_002",
                date=datetime(2024, 6, 15).date(),
                event_type="Concert (U2)",
                actual_covers=151,
                similarity=0.91,
                metadata={
                    "day_of_week": "Saturday",
                    "weather": "Partly cloudy",
                    "distance_km": 3.2
                }
            ),
            Pattern(
                pattern_id="pat_003",
                date=datetime(2024, 10, 12).date(),
                event_type="Rainy Saturday",
                actual_covers=138,
                similarity=0.87,
                metadata={
                    "day_of_week": "Saturday",
                    "weather": "Rain",
                    "distance_km": None
                }
            )
        ]
        
        print(f"  [PATTERNS] OK - Found {len(mock_patterns)} similar patterns")
        return mock_patterns
    
    async def _calculate_prediction(
        self,
        patterns: List[Pattern],
        context: Dict
    ) -> Dict:
        """
        Calculate weighted prediction based on similar patterns
        
        Uses:
        - Weighted average (higher similarity = higher weight)
        - Claude AI for confidence assessment
        """
        print("  [CALC] Calculating prediction...")
        
        if not patterns:
            # Fallback: no patterns found
            return {
                "predicted_covers": 120,  # Default estimate
                "confidence": 0.60,
                "method": "fallback"
            }
        
        # Weighted average calculation
        total_weight = sum(p.similarity for p in patterns)
        weighted_sum = sum(p.actual_covers * p.similarity for p in patterns)
        predicted_covers = int(weighted_sum / total_weight)
        
        # Average similarity = confidence proxy
        avg_similarity = total_weight / len(patterns)
        confidence = round(avg_similarity, 2)
        
        print(f"  [CALC] OK - Prediction: {predicted_covers} covers ({int(confidence*100)}% confidence)")
        
        return {
            "predicted_covers": predicted_covers,
            "confidence": confidence,
            "method": "weighted_average",
            "patterns_count": len(patterns)
        }


# Singleton instance
_demand_predictor = None

def get_demand_predictor() -> DemandPredictorAgent:
    """Get demand predictor singleton"""
    global _demand_predictor
    if _demand_predictor is None:
        _demand_predictor = DemandPredictorAgent()
    return _demand_predictor