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
            example="add edge X Y",
            explanation="An arrow X -> Y means X has a causal effect on Y.",
        ),
        TutorialStep(
            instruction="Graphs can have multiple edges.",
            prompt="Now add another cause of Y. Add an edge from Z to Y.",
            hint="Type: add edge Z Y",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Z", "child": "Y"},
            example="add edge Z Y",
            explanation="Y now has two parents: X and Z. Both cause Y.",
        ),
        TutorialStep(
            instruction="Check the structure with 'parents' command.",
            prompt="What are the parents of Y?",
            hint="Type: parents Y",
            expected_action=StepAction.SHOW_GRAPH,
            expected_args={"query": "parents", "node": "Y"},
            example="parents Y",
            explanation="Parents are direct causes. Y has parents {X, Z}.",
        ),
        TutorialStep(
            instruction="D-separation tells us when variables are independent.",
            prompt="Are X and Z d-separated (independent)?",
            hint="Type: dsep X Z",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "X", "y": "Z", "given": []},
            example="dsep X Z",
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
            example="add edge Age Treatment",
            explanation="Older patients might prefer different treatments.",
        ),
        TutorialStep(
            instruction="Age also affects health outcomes directly.",
            prompt="Add an edge: Age causes Outcome.",
            hint="Type: add edge Age Outcome",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Age", "child": "Outcome"},
            example="add edge Age Outcome",
            explanation="Age independently affects health outcomes.",
        ),
        TutorialStep(
            instruction="Finally, the treatment also affects the outcome.",
            prompt="Add an edge: Treatment causes Outcome.",
            hint="Type: add edge Treatment Outcome",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Treatment", "child": "Outcome"},
            example="add edge Treatment Outcome",
            explanation="This is the causal effect we want to estimate!",
        ),
        TutorialStep(
            instruction="Now we have a confounded relationship.",
            prompt="Check if Treatment and Outcome are d-separated.",
            hint="Type: dsep Treatment Outcome",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Treatment", "y": "Outcome", "given": []},
            example="dsep Treatment Outcome",
            explanation="They're NOT d-separated! There's a backdoor path through Age.",
        ),
        TutorialStep(
            instruction="Find the backdoor path causing the spurious correlation.",
            prompt="Find backdoor paths from Treatment to Outcome.",
            hint="Type: paths Treatment Outcome",
            expected_action=StepAction.CHECK_PATHS,
            expected_args={"treatment": "Treatment", "outcome": "Outcome"},
            example="paths Treatment Outcome",
            explanation="The path Treatment <- Age -> Outcome is a backdoor path (confounding).",
        ),
        TutorialStep(
            instruction="To estimate the causal effect, we must block the backdoor.",
            prompt="Check d-separation conditioning on Age.",
            hint="Type: dsep Treatment Outcome given Age",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Treatment", "y": "Outcome", "given": ["Age"]},
            example="dsep Treatment Outcome given Age",
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
            example="add edge Smoking Tar",
            explanation="Smoking leads to tar deposits in the lungs.",
        ),
        TutorialStep(
            instruction="The chain continues to the outcome.",
            prompt="Add: Tar causes Cancer.",
            hint="Type: add edge Tar Cancer",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Tar", "child": "Cancer"},
            example="add edge Tar Cancer",
            explanation="Tar buildup is carcinogenic.",
        ),
        TutorialStep(
            instruction="Check: are Smoking and Cancer d-separated?",
            prompt="Check d-separation between Smoking and Cancer.",
            hint="Type: dsep Smoking Cancer",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Smoking", "y": "Cancer", "given": []},
            example="dsep Smoking Cancer",
            explanation="They're NOT d-separated - Smoking affects Cancer through Tar.",
        ),
        TutorialStep(
            instruction="What happens if we condition on the mediator?",
            prompt="Check d-separation given Tar.",
            hint="Type: dsep Smoking Cancer given Tar",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Smoking", "y": "Cancer", "given": ["Tar"]},
            example="dsep Smoking Cancer given Tar",
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
            example="add edge Talent Success",
            explanation="Talented people are more likely to succeed.",
        ),
        TutorialStep(
            instruction="Luck also affects success.",
            prompt="Add: Luck causes Success.",
            hint="Type: add edge Luck Success",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Luck", "child": "Success"},
            example="add edge Luck Success",
            explanation="Lucky people also succeed (right place, right time).",
        ),
        TutorialStep(
            instruction="Success is a 'collider' - it has two causes pointing into it.",
            prompt="Are Talent and Luck d-separated?",
            hint="Type: dsep Talent Luck",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Talent", "y": "Luck", "given": []},
            example="dsep Talent Luck",
            explanation="Yes! Talent and Luck are independent - no causal connection.",
        ),
        TutorialStep(
            instruction="Here's the key insight about colliders...",
            prompt="Check d-separation given Success.",
            hint="Type: dsep Talent Luck given Success",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Talent", "y": "Luck", "given": ["Success"]},
            example="dsep Talent Luck given Success",
            explanation="Now they're DEPENDENT! Conditioning on a collider OPENS a path. Among successful people, less talent implies more luck (and vice versa). This is 'selection bias' or 'Berkson's paradox'.",
        ),
    ],
)

# =============================================================================
# Level 2: Intervention - The do-operator
# =============================================================================

LESSON_DO_OPERATOR = Lesson(
    id="do-operator",
    title="The do-Operator",
    description="Learn how interventions differ from observations using do-calculus.",
    level=CausalLevel.INTERVENTION,
    prerequisites=["confounder"],
    steps=[
        TutorialStep(
            instruction="Observing vs intervening: P(Y|X) ≠ P(Y|do(X)).",
            prompt="Build a confounded graph: U causes both X and Y.",
            hint="Type: add edge U X",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "U", "child": "X"},
            example="add edge U X",
            explanation="U is an unobserved confounder affecting X.",
        ),
        TutorialStep(
            instruction="Complete the confounding structure.",
            prompt="Add: U also causes Y.",
            hint="Type: add edge U Y",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "U", "child": "Y"},
            example="add edge U Y",
            explanation="Now U confounds the X-Y relationship.",
        ),
        TutorialStep(
            instruction="Add the causal path we want to study.",
            prompt="Add: X causes Y.",
            hint="Type: add edge X Y",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "X", "child": "Y"},
            example="add edge X Y",
            explanation="Graph complete: U → X → Y ← U. X and Y are confounded.",
        ),
        TutorialStep(
            instruction="When we observe X, we see effects of both X and U on Y.",
            prompt="Check if X and Y are d-separated.",
            hint="Type: dsep X Y",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "X", "y": "Y", "given": []},
            example="dsep X Y",
            explanation="NOT d-separated! Observing X=x tells us something about U, which affects Y.",
        ),
        TutorialStep(
            instruction="The do-operator simulates an experiment: set X, breaking its causes.",
            prompt="Apply do(X) - this removes all edges INTO X.",
            hint="Type: do X",
            expected_action=StepAction.APPLY_DO,
            expected_args={"variables": ["X"]},
            example="do X",
            explanation="do(X) cuts the U → X edge. Now X is set by us, not by U!",
        ),
        TutorialStep(
            instruction="After intervention, the confounding path is broken.",
            prompt="Check d-separation in the intervened graph.",
            hint="Type: dsep X Y",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "X", "y": "Y", "given": []},
            example="dsep X Y",
            explanation="Still not d-separated, but now only through the causal path X → Y. The backdoor through U is gone!",
        ),
    ],
)

LESSON_BACKDOOR = Lesson(
    id="backdoor",
    title="Backdoor Adjustment",
    description="Learn to identify and block backdoor paths for causal inference.",
    level=CausalLevel.INTERVENTION,
    prerequisites=["do-operator"],
    steps=[
        TutorialStep(
            instruction="The backdoor criterion: control for variables that block all backdoor paths.",
            prompt="Build graph: Smoking causes Cancer.",
            hint="Type: add edge Smoking Cancer",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Smoking", "child": "Cancer"},
            example="add edge Smoking Cancer",
            explanation="This is the causal effect we want to estimate.",
        ),
        TutorialStep(
            instruction="Add a confounder: Genetics affects both behaviors.",
            prompt="Add: Genetics causes Smoking.",
            hint="Type: add edge Genetics Smoking",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Genetics", "child": "Smoking"},
            example="add edge Genetics Smoking",
            explanation="Some genetic factors influence smoking behavior.",
        ),
        TutorialStep(
            instruction="Complete the confounding.",
            prompt="Add: Genetics also causes Cancer.",
            hint="Type: add edge Genetics Cancer",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Genetics", "child": "Cancer"},
            example="add edge Genetics Cancer",
            explanation="Genetics independently affects cancer risk.",
        ),
        TutorialStep(
            instruction="Find the backdoor path creating spurious correlation.",
            prompt="Find backdoor paths from Smoking to Cancer.",
            hint="Type: paths Smoking Cancer",
            expected_action=StepAction.CHECK_PATHS,
            expected_args={"treatment": "Smoking", "outcome": "Cancer"},
            example="paths Smoking Cancer",
            explanation="Backdoor path: Smoking ← Genetics → Cancer. This confounds our estimate!",
        ),
        TutorialStep(
            instruction="To estimate causal effect without do(), we can adjust for confounders.",
            prompt="Check d-separation controlling for Genetics.",
            hint="Type: dsep Smoking Cancer given Genetics",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Smoking", "y": "Cancer", "given": ["Genetics"]},
            example="dsep Smoking Cancer given Genetics",
            explanation="Backdoor blocked! P(Cancer|do(Smoking)) = Σ P(Cancer|Smoking,G) P(G). This is the backdoor adjustment formula.",
        ),
        TutorialStep(
            instruction="Alternative: use do() to simulate the experiment directly.",
            prompt="Apply do(Smoking).",
            hint="Type: do Smoking",
            expected_action=StepAction.APPLY_DO,
            expected_args={"variables": ["Smoking"]},
            example="do Smoking",
            explanation="do(Smoking) removes Genetics → Smoking. In an RCT, we assign smoking randomly, breaking confounding.",
        ),
    ],
)

LESSON_FRONTDOOR = Lesson(
    id="frontdoor",
    title="Frontdoor Criterion",
    description="Learn an alternative to backdoor adjustment when confounders are unobserved.",
    level=CausalLevel.INTERVENTION,
    causal_type=CausalType.FRONTDOOR,
    prerequisites=["backdoor"],
    steps=[
        TutorialStep(
            instruction="Sometimes confounders are unmeasured. The frontdoor criterion can help.",
            prompt="Build: Smoking causes Tar deposits.",
            hint="Type: add edge Smoking Tar",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Smoking", "child": "Tar"},
            example="add edge Smoking Tar",
            explanation="Tar is a mediator - it's on the causal path.",
        ),
        TutorialStep(
            instruction="Complete the causal chain.",
            prompt="Add: Tar causes Cancer.",
            hint="Type: add edge Tar Cancer",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Tar", "child": "Cancer"},
            example="add edge Tar Cancer",
            explanation="Smoking → Tar → Cancer is the causal pathway.",
        ),
        TutorialStep(
            instruction="Add an UNMEASURED confounder (we can't control for it!).",
            prompt="Add: Genotype causes Smoking.",
            hint="Type: add edge Genotype Smoking",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Genotype", "child": "Smoking"},
            example="add edge Genotype Smoking",
            explanation="Genotype influences smoking behavior.",
        ),
        TutorialStep(
            instruction="Complete the unmeasured confounding.",
            prompt="Add: Genotype causes Cancer.",
            hint="Type: add edge Genotype Cancer",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Genotype", "child": "Cancer"},
            example="add edge Genotype Cancer",
            explanation="Now we have: Smoking ← Genotype → Cancer (backdoor) AND Smoking → Tar → Cancer (frontdoor).",
        ),
        TutorialStep(
            instruction="Check: can we block the backdoor by conditioning?",
            prompt="Find backdoor paths from Smoking to Cancer.",
            hint="Type: paths Smoking Cancer",
            expected_action=StepAction.CHECK_PATHS,
            expected_args={"treatment": "Smoking", "outcome": "Cancer"},
            example="paths Smoking Cancer",
            explanation="Backdoor: Smoking ← Genotype → Cancer. But Genotype is unmeasured - we CAN'T adjust for it!",
        ),
        TutorialStep(
            instruction="Frontdoor criterion: Use the mediator Tar. It has no backdoor from Smoking!",
            prompt="Check paths from Smoking to Tar.",
            hint="Type: paths Smoking Tar",
            expected_action=StepAction.CHECK_PATHS,
            expected_args={"treatment": "Smoking", "outcome": "Tar"},
            example="paths Smoking Tar",
            explanation="No backdoor! We can identify Smoking → Tar directly.",
        ),
        TutorialStep(
            instruction="And Tar → Cancer can be identified by adjusting for Smoking.",
            prompt="Check d-separation: Tar and Cancer given Smoking.",
            hint="Type: dsep Tar Cancer given Smoking",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Tar", "y": "Cancer", "given": ["Smoking"]},
            example="dsep Tar Cancer given Smoking",
            explanation="The backdoor Tar ← Smoking ← Genotype → Cancer is blocked by Smoking! Frontdoor formula: P(Y|do(X)) = Σ P(M|X) Σ P(Y|M,X') P(X')",
        ),
    ],
)

# =============================================================================
# Level 3: Counterfactual - What-if reasoning
# =============================================================================

LESSON_SCM_INTRO = Lesson(
    id="scm-intro",
    title="Structural Causal Models",
    description="Learn how SCMs enable counterfactual reasoning beyond interventions.",
    level=CausalLevel.COUNTERFACTUAL,
    prerequisites=["frontdoor"],
    steps=[
        TutorialStep(
            instruction="Level 3 goes beyond 'what if we do X' to 'what would have happened'.",
            prompt="Build a simple SCM: Education causes Income.",
            hint="Type: add edge Education Income",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Education", "child": "Income"},
            example="add edge Education Income",
            explanation="In an SCM, we write: Income = f(Education, U_income).",
        ),
        TutorialStep(
            instruction="Add background factors that influence education.",
            prompt="Add: Background causes Education.",
            hint="Type: add edge Background Education",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Background", "child": "Education"},
            example="add edge Background Education",
            explanation="Background factors (family, opportunities) affect education level.",
        ),
        TutorialStep(
            instruction="Background also directly affects income.",
            prompt="Add: Background causes Income.",
            hint="Type: add edge Background Income",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Background", "child": "Income"},
            example="add edge Background Income",
            explanation="Now we have confounding. SCM: Income = f(Education, Background, U).",
        ),
        TutorialStep(
            instruction="Interventional query: P(Income | do(Education=college))",
            prompt="Apply do(Education) to see the causal effect.",
            hint="Type: do Education",
            expected_action=StepAction.APPLY_DO,
            expected_args={"variables": ["Education"]},
            example="do Education",
            explanation="This answers: 'What would happen if we SET education to college?'",
        ),
        TutorialStep(
            instruction="But counterfactuals ask about SPECIFIC individuals...",
            prompt="Check if Education and Income are d-separated after do().",
            hint="Type: dsep Education Income",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Education", "y": "Income", "given": []},
            example="dsep Education Income",
            explanation="Counterfactual: 'For Alice who didn't go to college and earns $40K, what WOULD she earn if she HAD gone?' This requires knowing Alice's specific U values.",
        ),
    ],
)

LESSON_COUNTERFACTUAL_STEPS = Lesson(
    id="counterfactual-steps",
    title="The Three-Step Process",
    description="Learn abduction, action, and prediction for counterfactual reasoning.",
    level=CausalLevel.COUNTERFACTUAL,
    prerequisites=["scm-intro"],
    steps=[
        TutorialStep(
            instruction="Counterfactuals use a 3-step process: Abduction → Action → Prediction.",
            prompt="Build: Treatment causes Recovery.",
            hint="Type: add edge Treatment Recovery",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Treatment", "child": "Recovery"},
            example="add edge Treatment Recovery",
            explanation="We'll ask: 'Would patient X have recovered if treated differently?'",
        ),
        TutorialStep(
            instruction="Add patient-specific factors.",
            prompt="Add: Severity causes Recovery.",
            hint="Type: add edge Severity Recovery",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Severity", "child": "Recovery"},
            example="add edge Severity Recovery",
            explanation="Recovery depends on both treatment AND disease severity.",
        ),
        TutorialStep(
            instruction="Doctors choose treatment based on severity.",
            prompt="Add: Severity causes Treatment.",
            hint="Type: add edge Severity Treatment",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Severity", "child": "Treatment"},
            example="add edge Severity Treatment",
            explanation="Now we have confounding: Severity → Treatment, Severity → Recovery.",
        ),
        TutorialStep(
            instruction="Step 1 - ABDUCTION: Given observed data, infer individual's error terms.",
            prompt="Find backdoor paths from Treatment to Recovery.",
            hint="Type: paths Treatment Recovery",
            expected_action=StepAction.CHECK_PATHS,
            expected_args={"treatment": "Treatment", "outcome": "Recovery"},
            example="paths Treatment Recovery",
            explanation="Abduction: If patient didn't recover despite treatment, we infer their U_recovery was unfavorable (perhaps underlying condition).",
        ),
        TutorialStep(
            instruction="Step 2 - ACTION: Apply the counterfactual intervention.",
            prompt="Apply do(Treatment) - the hypothetical different choice.",
            hint="Type: do Treatment",
            expected_action=StepAction.APPLY_DO,
            expected_args={"variables": ["Treatment"]},
            example="do Treatment",
            explanation="Action: 'What if we had given the OTHER treatment?' We cut Severity → Treatment.",
        ),
        TutorialStep(
            instruction="Step 3 - PREDICTION: Compute outcome using individual's U values.",
            prompt="Check d-separation in the counterfactual world.",
            hint="Type: dsep Treatment Recovery",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Treatment", "y": "Recovery", "given": []},
            example="dsep Treatment Recovery",
            explanation="Prediction: With the patient's SAME Severity and U values, but DIFFERENT treatment, would they recover? This is the individual causal effect.",
        ),
    ],
)

LESSON_ETT_VS_ATE = Lesson(
    id="ett-vs-ate",
    title="Individual vs Population Effects",
    description="Understand the difference between ATE (Average Treatment Effect) and ETT (Effect of Treatment on Treated).",
    level=CausalLevel.COUNTERFACTUAL,
    prerequisites=["counterfactual-steps"],
    steps=[
        TutorialStep(
            instruction="ATE = E[Y(1)] - E[Y(0)] averages over everyone. ETT focuses on the treated.",
            prompt="Build a job training scenario: Training causes Employment.",
            hint="Type: add edge Training Employment",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Training", "child": "Employment"},
            example="add edge Training Employment",
            explanation="We want to know: Does training help? But for whom?",
        ),
        TutorialStep(
            instruction="Motivation affects who signs up for training.",
            prompt="Add: Motivation causes Training.",
            hint="Type: add edge Motivation Training",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Motivation", "child": "Training"},
            example="add edge Motivation Training",
            explanation="Motivated people are more likely to enroll.",
        ),
        TutorialStep(
            instruction="Motivation also directly affects employment.",
            prompt="Add: Motivation causes Employment.",
            hint="Type: add edge Motivation Employment",
            expected_action=StepAction.ADD_EDGE,
            expected_args={"parent": "Motivation", "child": "Employment"},
            example="add edge Motivation Employment",
            explanation="Selection bias! The trained group is already more motivated.",
        ),
        TutorialStep(
            instruction="ATE asks: 'What's the average effect if we randomly assigned training?'",
            prompt="Apply do(Training) for the ATE.",
            hint="Type: do Training",
            expected_action=StepAction.APPLY_DO,
            expected_args={"variables": ["Training"]},
            example="do Training",
            explanation="ATE = E[Employment | do(Training=1)] - E[Employment | do(Training=0)]",
        ),
        TutorialStep(
            instruction="ETT asks: 'For those who GOT training, did it help THEM?'",
            prompt="Check paths - ETT requires counterfactual reasoning about the treated.",
            hint="Type: dsep Training Employment",
            expected_action=StepAction.CHECK_DSEP,
            expected_args={"x": "Training", "y": "Employment", "given": []},
            example="dsep Training Employment",
            explanation="ETT = E[Y(1) - Y(0) | Treated=1]. 'Would the trained have been employed WITHOUT training?' This needs individual counterfactuals, not just interventions!",
        ),
    ],
)

# =============================================================================
# Lesson Registry
# =============================================================================

ALL_LESSONS = [
    # Level 1: Association
    LESSON_GRAPH_BASICS,
    LESSON_CONFOUNDER,
    LESSON_MEDIATOR,
    LESSON_COLLIDER,
    # Level 2: Intervention
    LESSON_DO_OPERATOR,
    LESSON_BACKDOOR,
    LESSON_FRONTDOOR,
    # Level 3: Counterfactual
    LESSON_SCM_INTRO,
    LESSON_COUNTERFACTUAL_STEPS,
    LESSON_ETT_VS_ATE,
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
