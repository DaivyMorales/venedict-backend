from typing import TypedDict, Annotated, Literal
from pydantic import Field
from langgraph.graph.message import add_messages
import re


def split_into_bubbles(text: str) -> list[str]:
    if not text:
        return []
    # Split by double newlines first (paragraphs)
    paragraphs = re.split(r"\n\s*\n", text)
    bubbles = []
    for p in paragraphs:
        if not p.strip():
            continue
        # Split by sentences (. ! ?) followed by space
        sentences = re.split(r"(?<=[.!?])\s+", p.strip())
        for s in sentences:
            if s.strip():
                bubbles.append(s.strip())
    return bubbles


class RefereeDecision(TypedDict):
    winner: Literal["bull", "bear"]
    reason: str = Field(description="Reason why the winner", default="")
    risk_matrix: int = Field(
        description="Risk matrix, 10 being the highest risk, 0 being the lowest risk",
        default=0,
        ge=0,
        le=10,
    )
    fear_greed_index: int = Field(
        description="Fear and greed index, 10 being the highest fear, 0 being the lowest fear",
        default=0,
        ge=0,
        le=10,
    )
    social_interest: int = Field(
        description="Social interest percentage (Social Networks, Social Media, etc) (0-100)",
        default=0,
        ge=0,
        le=100,
    )
    level_complexity: int = Field(
        description="Level of complexity of the asset, 5 being the highest complexity to acquire (knowledge required, paperwork, etc), 0 being the lowest complexity to acquire",
        default=0,
        ge=0,
        le=5,
    )
    type_asset: Literal["conservative", "moderate", "aggressive"] = Field(
        description="Type of asset based on investment risk", default="moderate"
    )
    percentage_win_loss: int = Field(
        description="Percentage estimated of rentability win or loss based on the asset and term",
        default=0,
        ge=-1000,
        le=1000,
    )
    variants: list[dict[str, str]] = Field(
        description="List of variants of the asset, each containing a 'variant' name and an 'argument' explaining why it is a good variant",
        default_factory=list,
    )
    bull_probability: int = Field(
        description="Probability of Bull winning (0-100)", default=0, ge=0, le=100
    )
    bear_probability: int = Field(
        description="Probability of Bear winning (0-100)", default=0, ge=0, le=100
    )


class State(TypedDict):
    asset: str | None
    term: Literal["short-term", "mid-term", "long-term"] = Field(default="mid-term")
    language: Literal["English", "Spanish"] = Field(default="Spanish")
    messages: Annotated[list, add_messages]
    response_bull: str | None
    response_bear: str | None
    bull_bubbles: list[str] = Field(default_factory=list)
    bear_bubbles: list[str] = Field(default_factory=list)
    referee_decision: RefereeDecision
    debate_turns: int
