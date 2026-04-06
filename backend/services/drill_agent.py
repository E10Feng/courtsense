"""
LangGraph agent for drill generation — finds/creates drills based on weaknesses
"""
import json
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional


class DrillState(TypedDict, total=False):
    weakness: str
    sport: str
    drill_name: Optional[str]
    reps: Optional[str]
    sets: Optional[str]
    error: Optional[str]


DRILL_GENERATION_PROMPT = """You are a pickleball and tennis coach. Based on the weakness described, generate a specific drill with reps and sets.

Weakness: {weakness}
Sport: {sport}

Return ONLY valid JSON:
{{
  "drill_name": "specific name of the drill",
  "reps": "e.g., 20-30",
  "sets": "e.g., 3-4",
  "why": "1 sentence on why this drill fixes the weakness"
}}
"""


async def generate_drill(state: DrillState) -> DrillState:
    try:
        import httpx, os
        prompt = DRILL_GENERATION_PROMPT.format(
            weakness=state["weakness"],
            sport=state["sport"],
        )
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                os.getenv("OPENCLAW_API_URL", "https://api.openclaw.com/v1/chat/completions"),
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENCLAW_API_KEY', '')}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "minimax/MiniMax-M2.7",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4,
                    "max_tokens": 500,
                },
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            result = json.loads(content)
            return {
                **state,
                "drill_name": result.get("drill_name"),
                "reps": result.get("reps"),
                "sets": result.get("sets"),
            }
    except Exception as e:
        return {**state, "error": str(e)}
