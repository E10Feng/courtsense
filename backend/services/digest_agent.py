"""
LangGraph agent for weekly digest generation.

Flow:
1. Analyze sessions → identify weakness patterns
2. Search drills DB for relevant drills
3. Generate personalized drill recommendations
"""
import json
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
import os


class DigestState(TypedDict, total=False):
    sessions: list[dict]
    weakness_summary: Optional[str]
    top_weaknesses: list[dict]
    drill_recommendations: list[dict]
    error: Optional[str]


DIGEST_PROMPT = """You are a pickleball and tennis coach. Analyze this player's last 7 sessions and return ONLY valid JSON.

Player sessions (last 7 days):
{sessions}

Return this exact JSON (no markdown, no commentary):
{{
  "weakness_summary": "2-3 sentence narrative of the player's main patterns and struggles",
  "top_weaknesses": [
    {{
      "area": "specific weakness area (e.g., 'backhand return', 'net play', 'serve placement')",
      "percent": estimated percent of points lost due to this weakness as a float,
      "evidence": "specific session data that shows this (e.g., 'lost 8/10 points where backhand was used in session 2026-04-03')"
    }}
  ],
  "drill_recommendations": [
    {{
      "drill": "name of drill",
      "why": "1 sentence explaining how this drill fixes the weakness",
      "reps": "e.g., 20-30",
      "sets": "e.g., 3-4"
    }}
  ]
}}

Rules:
- Reference specific sessions, scores, and drill notes in evidence
- Prioritize the 3 highest-impact weaknesses
- If no sessions exist, return null for all fields
- If sessions exist but patterns are unclear, make reasonable inferences from the data
"""


async def analyze_weaknesses(state: DigestState) -> DigestState:
    """Call MiniMax M2.7 to analyze sessions and extract weaknesses."""
    sessions = state.get("sessions", [])
    if not sessions:
        return {**state, "weakness_summary": None, "top_weaknesses": [], "drill_recommendations": []}

    try:
        import httpx
        api_key = os.getenv("OPENCLAW_API_KEY", "")
        api_url = os.getenv("OPENCLAW_API_URL", "https://api.openclaw.com/v1/chat/completions")

        prompt = DIGEST_PROMPT.format(sessions=json.dumps(sessions, indent=2))

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "minimax/MiniMax-M2.7",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2000,
                },
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()

            # Strip markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            result = json.loads(content)
            return {
                **state,
                "weakness_summary": result.get("weakness_summary"),
                "top_weaknesses": result.get("top_weaknesses", []),
                "drill_recommendations": result.get("drill_recommendations", []),
            }
    except Exception as e:
        return {**state, "error": str(e)}


def build_digest_graph():
    graph = StateGraph(DigestState)
    graph.add_node("analyze_weaknesses", analyze_weaknesses)
    graph.set_entry_point("analyze_weaknesses")
    graph.add_edge("analyze_weaknesses", END)
    return graph.compile()


_async_graph = None

async def generate_digest_graph(sessions: list[dict]) -> dict:
    global _async_graph
    if _async_graph is None:
        _async_graph = build_digest_graph()

    state = await _async_graph.ainvoke({"sessions": sessions})
    if state.get("error"):
        # Fallback: return a simple summary without LLM
        return {
            "weakness_summary": f"Analyzed {len(sessions)} sessions. Specific LLM analysis unavailable: {state['error']}",
            "top_weaknesses": [],
            "drill_recommendations": [],
        }
    return {
        "weakness_summary": state.get("weakness_summary"),
        "top_weaknesses": state.get("top_weaknesses", []),
        "drill_recommendations": state.get("drill_recommendations", []),
    }
