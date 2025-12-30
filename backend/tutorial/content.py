"""Tutorial lesson definitions."""

from backend.tutorial.models import (
    CausalLevel,
    CausalType,
    Lesson,
    StepAction,
    TutorialStep,
)

# =============================================================================
# Level 1: Association - Understanding Causal Graphs
# =============================================================================

LESSON_GRAPH_BASICS = Lesson(
    id="graph-basics",
    title="Graph Basics",
    description="Learn to build causal graphs with nodes and edges.",
    level=CausalLevel.ASSOCIATION,
    steps=[
        TutorialStep(
            instruction="Causal graphs represent cause-effect relationships.",
            prompt="Let's start simple. Add an edge from X to Y (X causes Y).",
            hint="Type: add edge X Y",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "X", "child": "Y"},
            explanation="An arrow X -> Y means X has a causal effect on Y.",
        ),
        TutorialStep(
            instruction="Graphs can have multiple edges.",
            prompt="Now add another cause of Y. Add an edge from Z to Y.",
            hint="Type: add edge Z Y",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Z", "child": "Y"},
            explanation="Y now has two parents: X and Z. Both cause Y.",
        ),
        TutorialStep(
            instruction="Check the structure with 'parents' command.",
            prompt="What are the parents of Y?",
            hint="Type: parents Y",
            expected_action=StepAction.SHOW_GRAPH,
            expected_args={"query": "parents", "node": "Y"},
            explanation="Parents are direct causes. Y has parents {X, Z}.",
        ),
        TutorialStep(
            instruction="D-separation tells us when variables are independent.",
            prompt="Are X and Z d-separated (independent)?",
            hint="Type: dsep X Z",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "X", "y": "Z", "given": []},
            explanation="X and Z are d-separated because they have no connecting path (except through their common child Y).",
        ),
    ],
)

LESSON_CONFOUNDER = Lesson(
    id="confounder",
    title="Understanding Confounders",
    description="Learn to identify and handle confounding variables.",
    level=CausalLevel.ASSOCIATION,
    causal_type=CausalType.CONFOUNDER,
    prerequisites=["graph-basics"],
    steps=[
        TutorialStep(
            instruction="A confounder is a common cause of both treatment and outcome.",
            prompt="Create the first edge: Age causes Treatment choice.",
            hint="Type: add edge Age Treatment",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Age", "child": "Treatment"},
            explanation="Older patients might prefer different treatments.",
        ),
        TutorialStep(
            instruction="Age also affects health outcomes directly.",
            prompt="Add an edge: Age causes Outcome.",
            hint="Type: add edge Age Outcome",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Age", "child": "Outcome"},
            explanation="Age independently affects health outcomes.",
        ),
        TutorialStep(
            instruction="Finally, the treatment also affects the outcome.",
            prompt="Add an edge: Treatment causes Outcome.",
            hint="Type: add edge Treatment Outcome",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Treatment", "child": "Outcome"},
            explanation="This is the causal effect we want to estimate!",
        ),
        TutorialStep(
            instruction="Now we have a confounded relationship.",
            prompt="Check if Treatment and Outcome are d-separated.",
            hint="Type: dsep Treatment Outcome",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Treatment", "y": "Outcome", "given": []},
            explanation="They're NOT d-separated! There's a backdoor path through Age.",
        ),
        TutorialStep(
            instruction="Find the backdoor path causing the spurious correlation.",
            prompt="Find backdoor paths from Treatment to Outcome.",
            hint="Type: paths Treatment Outcome",
            expected_action=StepAction.CHECK_PATHS,
            expected_args={"treatment": "Treatment", "outcome": "Outcome"},
            explanation="The path Treatment <- Age -> Outcome is a backdoor path (confounding).",
        ),
        TutorialStep(
            instruction="To estimate the causal effect, we must block the backdoor.",
            prompt="Check d-separation conditioning on Age.",
            hint="Type: dsep Treatment Outcome given Age",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Treatment", "y": "Outcome", "given": ["Age"]},
            explanation="Controlling for Age blocks the backdoor path. Now we can estimate the true causal effect of Treatment on Outcome!",
        ),
    ],
)

LESSON_MEDIATOR = Lesson(
    id="mediator",
    title="Understanding Mediators",
    description="Learn how causal effects flow through intermediate variables.",
    level=CausalLevel.ASSOCIATION,
    causal_type=CausalType.MEDIATOR,
    prerequisites=["graph-basics"],
    steps=[
        TutorialStep(
            instruction="A mediator is a variable on the causal path between treatment and outcome.",
            prompt="Create a chain: Smoking causes Tar buildup.",
            hint="Type: add edge Smoking Tar",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Smoking", "child": "Tar"},
            explanation="Smoking leads to tar deposits in the lungs.",
        ),
        TutorialStep(
            instruction="The chain continues to the outcome.",
            prompt="Add: Tar causes Cancer.",
            hint="Type: add edge Tar Cancer",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Tar", "child": "Cancer"},
            explanation="Tar buildup is carcinogenic.",
        ),
        TutorialStep(
            instruction="Check: are Smoking and Cancer d-separated?",
            prompt="Check d-separation between Smoking and Cancer.",
            hint="Type: dsep Smoking Cancer",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Smoking", "y": "Cancer", "given": []},
            explanation="They're NOT d-separated - Smoking affects Cancer through Tar.",
        ),
        TutorialStep(
            instruction="What happens if we condition on the mediator?",
            prompt="Check d-separation given Tar.",
            hint="Type: dsep Smoking Cancer given Tar",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Smoking", "y": "Cancer", "given": ["Tar"]},
            explanation="Now they ARE d-separated! Conditioning on a mediator blocks the causal path. WARNING: Don't control for mediators when estimating total effects!",
        ),
    ],
)

LESSON_COLLIDER = Lesson(
    id="collider",
    title="Understanding Colliders",
    description="Learn why conditioning on common effects creates bias.",
    level=CausalLevel.ASSOCIATION,
    causal_type=CausalType.COLLIDER,
    prerequisites=["graph-basics"],
    steps=[
        TutorialStep(
            instruction="A collider is a common effect of two variables.",
            prompt="Talent contributes to Success. Add that edge.",
            hint="Type: add edge Talent Success",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Talent", "child": "Success"},
            explanation="Talented people are more likely to succeed.",
        ),
        TutorialStep(
            instruction="Luck also affects success.",
            prompt="Add: Luck causes Success.",
            hint="Type: add edge Luck Success",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Luck", "child": "Success"},
            explanation="Lucky people also succeed (right place, right time).",
        ),
        TutorialStep(
            instruction="Success is a 'collider' - it has two causes pointing into it.",
            prompt="Are Talent and Luck d-separated?",
            hint="Type: dsep Talent Luck",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Talent", "y": "Luck", "given": []},
            explanation="Yes! Talent and Luck are independent - no causal connection.",
        ),
        TutorialStep(
            instruction="Here's the key insight about colliders...",
            prompt="Check d-separation given Success.",
            hint="Type: dsep Talent Luck given Success",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Talent", "y": "Luck", "given": ["Success"]},
            explanation="Now they're DEPENDENT! Conditioning on a collider OPENS a path. Among successful people, less talent implies more luck (and vice versa). This is 'selection bias' or 'Berkson's paradox'.",
        ),
    ],
)

# =============================================================================
# Lesson Registry
# =============================================================================

ALL_LESSONS = [
    LESSON_GRAPH_BASICS,
    LESSON_CONFOUNDER,
    LESSON_MEDIATOR,
    LESSON_COLLIDER,
]


def get_all_lessons() -> list[Lesson]:
    """Get all available lessons."""
    return ALL_LESSONS.copy()


def get_lessons_by_level(level: CausalLevel) -> list[Lesson]:
    """Get lessons for a specific causal hierarchy level."""
    return [lesson for lesson in ALL_LESSONS if lesson.level == level]


def get_lesson_by_id(lesson_id: str) -> Lesson | None:
    """Get a specific lesson by ID."""
    for lesson in ALL_LESSONS:
        if lesson.id == lesson_id:
            return lesson
    return None
