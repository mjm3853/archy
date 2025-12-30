"""Tutorial engine - manages lesson flow and user state."""

import re
from typing import Optional

from backend.graph import CausalGraph
from backend.tutorial.models import (
    Lesson,
    StepAction,
    TutorialResponse,
    TutorialState,
    TutorialStep,
)


class TutorialEngine:
    """Manages tutorial flow, state, and user input processing."""

    def __init__(self) -> None:
        self.graph: Optional[CausalGraph] = None
        self.state: Optional[TutorialState] = None
        self.current_lesson: Optional[Lesson] = None
        self._lessons: dict[str, Lesson] = {}

    def register_lesson(self, lesson: Lesson) -> None:
        """Register a lesson for use."""
        self._lessons[lesson.id] = lesson

    def list_lessons(self) -> list[Lesson]:
        """Get all available lessons."""
        return list(self._lessons.values())

    def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        """Get a specific lesson by ID."""
        return self._lessons.get(lesson_id)

    def start_lesson(self, lesson_id: str) -> bool:
        """Start a new lesson, resetting state."""
        lesson = self._lessons.get(lesson_id)
        if not lesson:
            return False

        self.current_lesson = lesson
        self.graph = CausalGraph(edges=[])
        self.state = TutorialState(lesson_id=lesson_id)
        return True

    def get_current_step(self) -> Optional[TutorialStep]:
        """Get the current step in the lesson."""
        if not self.current_lesson or not self.state:
            return None
        if self.state.step_index >= len(self.current_lesson.steps):
            return None
        return self.current_lesson.steps[self.state.step_index]

    def get_hint(self) -> str:
        """Get hint for current step."""
        step = self.get_current_step()
        if not step:
            return "No active lesson."
        return step.hint

    def handle_input(self, user_input: str) -> TutorialResponse:
        """Process user input and return response."""
        if not self.state or not self.current_lesson:
            return TutorialResponse(
                success=False,
                message="No active lesson. Use 'archy learn <lesson>' to start.",
            )

        user_input = user_input.strip().lower()

        # Handle navigation commands
        if user_input == "hint":
            return TutorialResponse(success=True, message=self.get_hint())
        if user_input == "skip":
            return self._advance_step(skipped=True)
        if user_input == "show":
            return TutorialResponse(
                success=True, message="Current graph:", show_graph=True
            )
        if user_input in ("quit", "exit", "q"):
            return TutorialResponse(
                success=True, message="Tutorial paused. Use --resume to continue."
            )

        # Parse and execute command
        return self._execute_command(user_input)

    def _execute_command(self, cmd: str) -> TutorialResponse:
        """Parse and execute a tutorial command."""
        step = self.get_current_step()
        if not step:
            return TutorialResponse(
                success=False, message="Lesson complete!", advance=False
            )

        # Parse command
        parsed = self._parse_command(cmd)
        if not parsed:
            return TutorialResponse(
                success=False,
                message=f"Unknown command. Try: {self._get_expected_command_hint(step)}",
            )

        action, args = parsed

        # Execute action on graph
        result = self._apply_action(action, args)
        if not result.success:
            return result

        # Validate against expected
        if not self.state:
            return TutorialResponse(success=False, message="No active lesson.")

        if self._validate_step(step, action, args):
            self.state.attempts = 0
            return self._advance_step()
        else:
            self.state.attempts += 1
            hint_msg = ""
            if self.state.attempts >= 2:
                hint_msg = f"\n\nHint: {step.hint}"
            return TutorialResponse(
                success=False,
                message=f"Not quite. {step.prompt}{hint_msg}",
                show_graph=True,
            )

    def _parse_command(self, cmd: str) -> Optional[tuple[StepAction, dict]]:
        """Parse user command into action and arguments."""
        # add edge X Y
        match = re.match(r"add\s+edge\s+(\w+)\s+(\w+)", cmd)
        if match:
            return StepAction.ADD_EDGE, {
                "parent": match.group(1),
                "child": match.group(2),
            }

        # add node X
        match = re.match(r"add\s+node\s+(\w+)", cmd)
        if match:
            return StepAction.ADD_NODE, {"node": match.group(1)}

        # remove edge X Y
        match = re.match(r"remove\s+edge\s+(\w+)\s+(\w+)", cmd)
        if match:
            return StepAction.REMOVE_EDGE, {
                "parent": match.group(1),
                "child": match.group(2),
            }

        # dsep X Y [given Z [W ...]]
        match = re.match(r"dsep\s+(\w+)\s+(\w+)(?:\s+given\s+(.+))?", cmd)
        if match:
            given: list[str] = []
            if match.group(3):
                given = match.group(3).split()
            return StepAction.CHECK_DSEP, {
                "x": match.group(1),
                "y": match.group(2),
                "given": given,
            }

        # paths X Y
        match = re.match(r"paths\s+(\w+)\s+(\w+)", cmd)
        if match:
            return StepAction.CHECK_PATHS, {
                "treatment": match.group(1),
                "outcome": match.group(2),
            }

        # do X [Y ...]
        match = re.match(r"do\s+(.+)", cmd)
        if match:
            variables = match.group(1).split()
            return StepAction.APPLY_DO, {"variables": variables}

        # parents X / children X
        match = re.match(r"parents\s+(\w+)", cmd)
        if match:
            return StepAction.SHOW_GRAPH, {"query": "parents", "node": match.group(1)}

        match = re.match(r"children\s+(\w+)", cmd)
        if match:
            return StepAction.SHOW_GRAPH, {"query": "children", "node": match.group(1)}

        return None

    def _apply_action(self, action: StepAction, args: dict) -> TutorialResponse:
        """Apply an action to the current graph."""
        if not self.graph:
            self.graph = CausalGraph(edges=[])

        try:
            if action == StepAction.ADD_EDGE:
                self.graph.add_edge(args["parent"], args["child"])
                return TutorialResponse(
                    success=True,
                    message=f"Added edge: {args['parent']} -> {args['child']}",
                    show_graph=True,
                )

            elif action == StepAction.ADD_NODE:
                # Add isolated node by adding to graph
                self.graph._graph.add_node(args["node"])
                return TutorialResponse(
                    success=True, message=f"Added node: {args['node']}", show_graph=True
                )

            elif action == StepAction.REMOVE_EDGE:
                self.graph.remove_edge(args["parent"], args["child"])
                return TutorialResponse(
                    success=True,
                    message=f"Removed edge: {args['parent']} -> {args['child']}",
                    show_graph=True,
                )

            elif action == StepAction.CHECK_DSEP:
                x_set = {args["x"]}
                y_set = {args["y"]}
                z_set = set(args.get("given", []))
                is_sep = self.graph.is_d_separated(x_set, y_set, z_set)
                symbol = "\u2aeb" if is_sep else "\u2aeb\u0338"  # ⫫ or ⫫̸
                given_str = f" | {{{', '.join(z_set)}}}" if z_set else ""
                return TutorialResponse(
                    success=True,
                    message=f"{args['x']} {symbol} {args['y']}{given_str}",
                )

            elif action == StepAction.CHECK_PATHS:
                paths = self.graph.get_backdoor_paths(
                    args["treatment"], args["outcome"]
                )
                if not paths:
                    msg = f"No backdoor paths from {args['treatment']} to {args['outcome']}"
                else:
                    path_strs = [" -> ".join(p) for p in paths]
                    msg = "Backdoor paths:\n" + "\n".join(
                        f"  {i + 1}. {p}" for i, p in enumerate(path_strs)
                    )
                return TutorialResponse(success=True, message=msg)

            elif action == StepAction.SHOW_GRAPH:
                if args.get("query") == "parents":
                    parents = self.graph.get_parents(args["node"])
                    return TutorialResponse(
                        success=True,
                        message=f"Parents of {args['node']}: {{{', '.join(sorted(parents))}}}",
                    )
                elif args.get("query") == "children":
                    children = self.graph.get_children(args["node"])
                    return TutorialResponse(
                        success=True,
                        message=f"Children of {args['node']}: {{{', '.join(sorted(children))}}}",
                    )

            return TutorialResponse(success=True, message="OK")

        except Exception as e:
            return TutorialResponse(success=False, message=f"Error: {e}")

    def _validate_step(
        self, step: TutorialStep, action: StepAction, args: dict
    ) -> bool:
        """Check if the action matches what's expected for this step."""
        # Custom validator takes precedence
        if step.validator:
            return step.validator(self.graph, action, args)

        # Check action type matches
        if action != step.expected_action:
            return False

        # Check arguments match (case-insensitive for node names)
        expected = step.expected_args
        for key, value in expected.items():
            if key not in args:
                return False
            if isinstance(value, str):
                if args[key].lower() != value.lower():
                    return False
            elif isinstance(value, list):
                if sorted(a.lower() for a in args[key]) != sorted(
                    v.lower() for v in value
                ):
                    return False
            elif args[key] != value:
                return False

        return True

    def _advance_step(self, skipped: bool = False) -> TutorialResponse:
        """Move to the next step in the lesson."""
        if not self.state or not self.current_lesson:
            return TutorialResponse(success=False, message="No active lesson.")

        step = self.get_current_step()
        explanation = ""
        if step and step.explanation and not skipped:
            explanation = f"\n\n{step.explanation}"

        self.state.completed_steps.append(self.state.step_index)
        self.state.step_index += 1

        # Check if lesson complete
        if self.state.step_index >= len(self.current_lesson.steps):
            self.state.completed = True
            return TutorialResponse(
                success=True,
                message=f"Lesson complete!{explanation}",
                advance=False,
            )

        return TutorialResponse(
            success=True,
            message=f"{'Skipped.' if skipped else 'Correct!'}{explanation}",
            advance=True,
            show_graph=True,
        )

    def _get_expected_command_hint(self, step: TutorialStep) -> str:
        """Generate hint for expected command format."""
        hints = {
            StepAction.ADD_EDGE: "add edge X Y",
            StepAction.ADD_NODE: "add node X",
            StepAction.REMOVE_EDGE: "remove edge X Y",
            StepAction.CHECK_DSEP: "dsep X Y [given Z]",
            StepAction.CHECK_PATHS: "paths X Y",
            StepAction.APPLY_DO: "do X",
            StepAction.SHOW_GRAPH: "show, parents X, or children X",
        }
        return hints.get(step.expected_action, "hint")

    def save_state(self) -> dict:
        """Serialize current state for persistence."""
        if not self.state:
            return {}
        state_dict = self.state.to_dict()
        if self.graph:
            state_dict["graph_state"] = self.graph.to_dict()
        return state_dict

    def load_state(self, data: dict) -> bool:
        """Restore state from persistence."""
        if not data or "lesson_id" not in data:
            return False

        lesson_id = data["lesson_id"]
        if lesson_id not in self._lessons:
            return False

        self.current_lesson = self._lessons[lesson_id]
        self.state = TutorialState.from_dict(data)

        if data.get("graph_state"):
            self.graph = CausalGraph.from_dict(data["graph_state"])
        else:
            self.graph = CausalGraph(edges=[])

        return True
