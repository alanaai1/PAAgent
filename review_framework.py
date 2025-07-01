"""
LLM Reviewing Framework -- generic, best-practice prompt design
"""

from __future__ import annotations
import asyncio
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Callable, Coroutine, List, Optional
from openai import AsyncOpenAI

@dataclass
class ReviewResult:
    reviewer: str
    score: float
    verdict: str
    feedback: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "reviewer": self.reviewer,
            "score": self.score,
            "verdict": self.verdict,
            "feedback": self.feedback,
        }

@dataclass
class ReviewerConfig:
    name: str
    system_prompt: str
    weight: float = 1.0
    model: str = "gpt-4o-mini"
    temperature: float = 0.2

class Reviewer:
    def __init__(self, config: ReviewerConfig):
        self.config = config

    async def review(self, context: str, answer: str) -> ReviewResult:
        client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        rubric_query = (
            f"You are {self.config.name}. You will receive CONTEXT and an ANSWER.\n"
            "Evaluate on: accuracy, completeness, clarity, coherence, strategic relevance, practicality.\n"
            "Return score 1-10. If score < 9.5 provide one actionable improvement.\n"
            "Respond ONLY in JSON with keys: score, verdict (pass/partial/fail), feedback."
        )

        resp = await client.chat.completions.create(
            model=self.config.model,
            temperature=self.config.temperature,
            messages=[
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": f"CONTEXT:\n{context}\n\nANSWER:\n{answer}\n\n{rubric_query}"},
            ],
        )

        content = resp.choices[0].message.content.strip()
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = {"score": 0, "verdict": "invalid", "feedback": "Could not parse JSON"}

        return ReviewResult(
            reviewer=self.config.name,
            score=float(data.get("score", 0)),
            verdict=str(data.get("verdict", "invalid")),
            feedback=str(data.get("feedback", "")),
        )

class ReviewManager:
    def __init__(self, reviewers: List[ReviewerConfig], pass_threshold: float = 9.5, max_rounds: int = 7):
        self.reviewer_agents = [Reviewer(cfg) for cfg in reviewers]
        self.configs = reviewers
        self.pass_threshold = pass_threshold
        self.max_rounds = max_rounds

    async def review_only(self, context: str, answer: str) -> dict[str, Any]:
        reviews = await self._gather_reviews(context, answer)
        avg_score = self._weighted_average(reviews)
        return {
            "average_score": avg_score,
            "reviews": [r.to_dict() for r in reviews],
            "passed": avg_score >= self.pass_threshold,
        }

    async def _gather_reviews(self, context: str, answer: str) -> List[ReviewResult]:
        tasks = [agent.review(context, answer) for agent in self.reviewer_agents]
        return await asyncio.gather(*tasks)

    def _weighted_average(self, results: List[ReviewResult]) -> float:
        total, wsum = 0.0, 0.0
        for cfg, res in zip(self.configs, results):
            total += cfg.weight * res.score
            wsum += cfg.weight
        return total / wsum if wsum else 0.0

# Test function
async def test_review():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    universal_prompt = (
        "You are a Domain Coach. Evaluate text for accuracy, completeness, "
        "clarity, coherence, strategic relevance, practicality, and policy compliance."
    )
    
    reviewer_cfgs = [
        ReviewerConfig(name=f"Coach {c}", system_prompt=universal_prompt, temperature=t)
        for c, t in zip(["A", "B", "C"], [0.2, 0.5, 0.8])
    ]
    
    manager = ReviewManager(reviewer_cfgs)
    
    test_insight = "Send VAT receipt update to Alan about bonus processing."
    context = "Chief of Staff insight for executive dashboard"
    
    results = await manager.review_only(context, test_insight)
    
    print(f"Score: {results['average_score']}/10")
    print(f"Passed: {results['passed']}")
    for review in results['reviews']:
        print(f"{review['reviewer']}: {review['score']} - {review['feedback']}")

if __name__ == "__main__":
    asyncio.run(test_review())
