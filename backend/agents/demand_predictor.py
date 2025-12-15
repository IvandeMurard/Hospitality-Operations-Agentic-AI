# -*- coding: utf-8 -*-
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
from datetime import datetime, date
from typing import Dict, List, Optional
import uuid
import random

from models.schemas import (
    PredictionRequest,
    Pattern,
    ServiceType
)
from utils.claude_client import get_claude_client
from agents.reasoning_engine import get_reasoning_engine


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
        
        # Step 4: Generate reasoning (NEW!)
        reasoning_engine = get_reasoning_engine()
        reasoning = await reasoning_engine.generate_reasoning(
            predicted_covers=prediction["predicted_covers"],
            confidence=prediction["confidence"],
            patterns=similar_patterns,
            context=context,
            service_date=request.service_date,
            service_type=request.service_type
        )
        
        # Combine prediction + reasoning
        prediction["reasoning"] = reasoning
        
        return prediction
    
    async def _fetch_external_context(self, request: PredictionRequest) -> Dict:
        """
        Fetch external context: events, weather, holidays
        
        Phase 1: MOCKED data (no real APIs yet)
        Phase 2: Integrate PredictHQ, Weather API
        """
        print("  [CONTEXT] Fetching external context...")
        
        # Mock data for MVP - Enhanced with realistic variety
        # Determine day type
        day_of_week = request.service_date.strftime("%A")
        is_weekend = request.service_date.weekday() in [5, 6]  # Saturday, Sunday
        is_friday = request.service_date.weekday() == 4
        
        # Generate realistic events based on day
        events = self._generate_mock_events(request.service_date, is_weekend)
        print(f"  [CONTEXT] Generated {len(events)} events")  # DEBUG
        
        # Generate realistic weather
        weather = self._generate_mock_weather(request.service_date, is_weekend)
        print(f"  [CONTEXT] Weather: {weather['condition']}, {weather['temperature']}C")  # DEBUG
        
        # Check if holiday (simplified - just mock some dates)
        is_holiday = self._is_mock_holiday(request.service_date)
        print(f"  [CONTEXT] Holiday: {is_holiday}")  # DEBUG
        
        context = {
            "day_of_week": day_of_week,
            "events": events,
            "weather": weather,
            "is_holiday": is_holiday,
            "day_type": "weekend" if is_weekend else "friday" if is_friday else "weekday"
        }
        
        print(f"  [CONTEXT] OK - {context['day_of_week']} ({context['day_type']}), {len(context['events'])} events")
        return context
    
    def _generate_mock_events(self, service_date: date, is_weekend: bool) -> List[Dict]:
        """
        Generate realistic mock events based on date
        
        Phase 1: Deterministic mock data
        Phase 2: Real PredictHQ API integration
        """
        events = []
        
        # Seed random with date for deterministic results
        random.seed(service_date.toordinal())
        
        # Weekend = higher chance of events
        event_probability = 0.7 if is_weekend else 0.3
        
        if random.random() < event_probability:
            # Event types pool
            event_types = [
                {
                    "type": "Concert",
                    "names": ["Coldplay", "Taylor Swift", "Ed Sheeran", "Beyonce"],
                    "attendance_range": (30000, 60000),
                    "distance_range": (1.5, 5.0),
                    "impact": "high"
                },
                {
                    "type": "Sports Match",
                    "names": ["PSG vs Marseille", "France vs England", "Champions League Final"],
                    "attendance_range": (40000, 80000),
                    "distance_range": (2.0, 6.0),
                    "impact": "high"
                },
                {
                    "type": "Theater Show",
                    "names": ["Hamilton", "Les Miserables", "Phantom of the Opera"],
                    "attendance_range": (1000, 3000),
                    "distance_range": (0.5, 2.0),
                    "impact": "medium"
                },
                {
                    "type": "Conference",
                    "names": ["Tech Summit", "Marketing Expo", "Healthcare Forum"],
                    "attendance_range": (500, 2000),
                    "distance_range": (0.2, 1.5),
                    "impact": "medium"
                }
            ]
            
            # Pick random event type
            event_type = random.choice(event_types)
            
            # Generate event details
            event = {
                "type": event_type["type"],
                "name": random.choice(event_type["names"]),
                "distance_km": round(random.uniform(*event_type["distance_range"]), 1),
                "expected_attendance": random.randint(*event_type["attendance_range"]),
                "start_time": "20:00" if event_type["type"] in ["Concert", "Theater Show"] else "19:00",
                "impact": event_type["impact"]
            }
            
            events.append(event)
            
            # 20% chance of second event on weekends
            if is_weekend and random.random() < 0.2:
                second_type = random.choice([t for t in event_types if t != event_type])
                second_event = {
                    "type": second_type["type"],
                    "name": random.choice(second_type["names"]),
                    "distance_km": round(random.uniform(*second_type["distance_range"]), 1),
                    "expected_attendance": random.randint(*second_type["attendance_range"]),
                    "start_time": "21:00",
                    "impact": second_type["impact"]
                }
                events.append(second_event)
        
        return events
    
    def _generate_mock_weather(self, service_date: date, is_weekend: bool) -> Dict:
        """
        Generate realistic mock weather based on date
        
        Phase 1: Deterministic mock data
        Phase 2: Real Weather API integration
        """
        random.seed(service_date.toordinal() + 1000)  # Different seed than events
        
        # Weather conditions pool with probabilities
        conditions = [
            ("Clear", 0.4),
            ("Partly Cloudy", 0.3),
            ("Cloudy", 0.15),
            ("Rain", 0.10),
            ("Heavy Rain", 0.03),
            ("Snow", 0.02)
        ]
        
        # Select weather based on probabilities
        rand = random.random()
        cumulative = 0
        selected_condition = "Clear"
        
        for condition, prob in conditions:
            cumulative += prob
            if rand <= cumulative:
                selected_condition = condition
                break
        
        # Temperature varies by month
        month = service_date.month
        if month in [12, 1, 2]:  # Winter
            temp_range = (0, 10)
        elif month in [3, 4, 5]:  # Spring
            temp_range = (10, 20)
        elif month in [6, 7, 8]:  # Summer
            temp_range = (20, 30)
        else:  # Fall
            temp_range = (10, 20)
        
        temperature = random.randint(*temp_range)
        
        # Precipitation and wind based on condition
        precipitation = {
            "Clear": 0,
            "Partly Cloudy": random.randint(0, 10),
            "Cloudy": random.randint(10, 30),
            "Rain": random.randint(40, 70),
            "Heavy Rain": random.randint(70, 100),
            "Snow": random.randint(30, 60)
        }.get(selected_condition, 0)
        
        wind_speed = random.randint(5, 25)
        
        return {
            "condition": selected_condition,
            "temperature": temperature,
            "precipitation": precipitation,
            "wind_speed": wind_speed
        }
    
    def _is_mock_holiday(self, service_date: date) -> bool:
        """
        Check if date is a holiday
        
        Phase 1: Mock major holidays
        Phase 2: Real calendar API
        """
        # Mock some major holidays (simplified)
        holidays = [
            (12, 25),  # Christmas
            (12, 31),  # New Year's Eve
            (1, 1),    # New Year's Day
            (7, 14),   # Bastille Day (France)
            (11, 11),  # Veterans Day
            (5, 1),    # Labor Day
        ]
        
        return (service_date.month, service_date.day) in holidays
    
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