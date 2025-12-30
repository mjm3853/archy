"""Data models for the tutorial system."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


class CausalLevel(Enum):
    """Pearl's causal hierarchy levels."""

    ASSOCIATION = 1  # Level 1: Observing correlations
    INTERVENTION = 2  # Level 2: do-calculus, "What if I do X?"
    COUNTERFACTUAL = 3  # Level 3: SCMs, "What would have happened?"


class CausalType(Enum):
    """Common causal structure types."""

    CONFOUNDER = "confounder"
    MEDIATOR = "mediator"
    COLLIDER = "collider"
    FRONTDOOR = "frontdoor"
    INSTRUMENTAL = "instrumental"
    M_BIAS = "m-bias"


class StepAction(Enum):
    """Types of actions users can take in a tutorial step."""

    ADD_EDGE = "add_edge"
    ADD_NODE = "add_node"
    REMOVE_EDGE = "remove_edge"
    CHECK_DSEP = "check_dsep"
    CHECK_PATHS = "check_paths"
    APPLY_DO = "apply_do"
    SHOW_GRAPH = "show_graph"
    ANSWER_QUESTION = "answer_question"


@dataclass
class TutorialStep:
    """A single step in a tutorial lesson."""

    instruction: str  # What the user should understand
    prompt: str  # The task or question
    hint: str  # Help if user is stuck
    expected_action: StepAction  # What type of action to validate
    expected_args: dict = field(default_factory=dict)  # Arguments for validation
    explanation: str = ""  # Why this matters (shown after success)
    validator: Optional[Callable] = None  # Custom validation function


@dataclass
class Lesson:
    """A complete tutorial lesson."""

    id: str
    title: str
    description: str
    level: CausalLevel
    causal_type: Optional[CausalType] = None
    steps: list[TutorialStep] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)  # Lesson IDs


@dataclass
class TutorialState:
    """Current state of a tutorial session."""

    lesson_id: str
    step_index: int = 0
    graph_state: dict = field(default_factory=dict)  # Serialized graph
    completed_steps: list[int] = field(default_factory=list)
    attempts: int = 0
    completed: bool = False

    def to_dict(self) -> dict:
        """Serialize state for persistence."""
        return {
            "lesson_id": self.lesson_id,
            "step_index": self.step_index,
            "graph_state": self.graph_state,
            "completed_steps": self.completed_steps,
            "attempts": self.attempts,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TutorialState":
        """Deserialize state from persistence."""
        return cls(
            lesson_id=data["lesson_id"],
            step_index=data.get("step_index", 0),
            graph_state=data.get("graph_state", {}),
            completed_steps=data.get("completed_steps", []),
            attempts=data.get("attempts", 0),
            completed=data.get("completed", False),
        )


@dataclass
class TutorialResponse:
    """Response from processing user input."""

    success: bool
    message: str
    show_graph: bool = False
    advance: bool = False  # Move to next step
    hint_available: bool = True
