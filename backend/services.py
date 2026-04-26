import os
import json
from dotenv import load_dotenv
from groq import Groq
from typing import List

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def predict_rankings(org_data: dict) -> dict:
    """
    Use Groq AI to predict top ambassadors for next week based on historical data.
    
    Args:
        org_data: {
            "current_rankings": [...],
            "historical_data": [...],
            "streak_info": [...],
            "org_name": "..."
        }
    
    Returns:
        {
            "predictions": [
                {"ambassador_id": 1, "predicted_rank": 1, "confidence": 0.95},
                ...
            ],
            "reasoning": "..."
        }
    """
    if not client:
        return {
            "predictions": [
                {"ambassador_id": i, "predicted_rank": i, "confidence": 0.5}
                for i in range(3)
            ],
            "reasoning": "AI unavailable, returning mock data"
        }
    
    prompt = f"""
    Based on the following ambassador performance data, predict the top 3 ambassadors for next week:
    
    Current Rankings: {json.dumps(org_data.get('current_rankings', []), indent=2)}
    Historical Data (past 14 days): {json.dumps(org_data.get('historical_data', []), indent=2)}
    Streak Information: {json.dumps(org_data.get('streak_info', []), indent=2)}
    
    Consider:
    1. Current momentum and scoring trajectory
    2. Completion consistency
    3. Streak counts (longer streaks indicate sustained engagement)
    4. Recent activity patterns
    
    Respond ONLY with valid JSON (no markdown, no code blocks):
    {{
        "predictions": [
            {{"ambassador_id": <int>, "predicted_rank": 1, "confidence": 0.90, "reasoning": "..."}},
            {{"ambassador_id": <int>, "predicted_rank": 2, "confidence": 0.85, "reasoning": "..."}},
            {{"ambassador_id": <int>, "predicted_rank": 3, "confidence": 0.80, "reasoning": "..."}}
        ],
        "overall_reasoning": "..."
    }}
    """
    
    try:
        message = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        response_text = message.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        result = json.loads(response_text)
        return result
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return {
            "predictions": [
                {"ambassador_id": i, "predicted_rank": i+1, "confidence": 0.5, "reasoning": f"Mock data due to error"}
                for i in range(3)
            ],
            "overall_reasoning": f"API error: {str(e)}"
        }

def get_task_recommendations(ambassador_history: dict) -> dict:
    """
    Recommend tasks to ambassador based on their history.
    """
    if not client:
        return {
            "recommended_task_types": ["referral", "content"],
            "reasoning": "Mock recommendations"
        }
    
    prompt = f"""
    Based on this ambassador's task completion history, recommend which task types they should focus on:
    
    History: {json.dumps(ambassador_history, indent=2)}
    
    Respond ONLY with valid JSON:
    {{
        "recommended_task_types": ["referral", "content"],
        "reasoning": "...",
        "confidence": 0.85
    }}
    """
    
    try:
        message = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        
        response_text = message.choices[0].message.content.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        return json.loads(response_text)
    except Exception as e:
        return {
            "recommended_task_types": ["custom"],
            "reasoning": "Error generating recommendations",
            "error": str(e)
        }

def generate_org_insights(org_data: dict) -> dict:
    """
    Generate manager insights about the organization.
    """
    if not client:
        return {
            "top_performers": [],
            "insights": ["Mock insights"],
            "recommendations": ["Mock recommendations"]
        }
    
    prompt = f"""
    As an ambassador program analyst, analyze this organization's performance and provide insights:
    
    Organization Data: {json.dumps(org_data, indent=2)}
    
    Respond ONLY with valid JSON:
    {{
        "top_performers": ["Ambassador Name"],
        "insights": ["..."],
        "recommendations": ["..."],
        "churn_risk": ["Ambassador Name"]
    }}
    """
    
    try:
        message = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        response_text = message.choices[0].message.content.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        return json.loads(response_text)
    except Exception as e:
        return {
            "insights": ["Unable to generate insights"],
            "error": str(e)
        }
