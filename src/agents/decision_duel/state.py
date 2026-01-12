from typing import TypedDict, Annotated, Literal
from pydantic import Field
from langgraph.graph.message import add_messages


class RefereeDecision(TypedDict):
    winner: Literal["bull", "bear"]
    reason: str = Field(description="Reason why the winner", default="")
    risk_matrix: int = Field(
        description="Risk matrix, 10 being the highest risk, 0 being the lowest risk",
        default=0,
        ge=0,
        le=10,
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
    referee_decision: RefereeDecision
    debate_turns: int
