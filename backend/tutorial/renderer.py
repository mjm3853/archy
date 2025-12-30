"""Rich terminal rendering for tutorials."""

from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from backend.graph import CausalGraph
from backend.tutorial.models import (
    CausalLevel,
    Lesson,
    TutorialResponse,
    TutorialState,
    TutorialStep,
)

console = Console()


def render_welcome() -> None:
    """Render tutorial welcome message."""
    console.print()
    console.print(
        Panel(
            "[bold cyan]Archy Tutorial[/bold cyan]\n\n"
            "Learn causal inference interactively!\n\n"
            "[dim]Pearl's Causal Hierarchy:[/dim]\n"
            "  [green]Level 1[/green]: Association - Understanding graphs\n"
            "  [yellow]Level 2[/yellow]: Intervention - do-calculus\n"
            "  [red]Level 3[/red]: Counterfactuals - What-if reasoning",
            title="Welcome",
            border_style="cyan",
        )
    )
    console.print()


def render_lesson_list(lessons: list[Lesson]) -> None:
    """Render available lessons as a table."""
    table = Table(title="Available Lessons", show_header=True)
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Level", style="green")
    table.add_column("Type", style="yellow")

    for lesson in lessons:
        level_str = {
            CausalLevel.ASSOCIATION: "[green]1: Association[/green]",
            CausalLevel.INTERVENTION: "[yellow]2: Intervention[/yellow]",
            CausalLevel.COUNTERFACTUAL: "[red]3: Counterfactual[/red]",
        }.get(lesson.level, str(lesson.level))

        type_str = lesson.causal_type.value if lesson.causal_type else "-"

        table.add_row(lesson.id, lesson.title, level_str, type_str)

    console.print(table)
    console.print()
    console.print("[dim]Start a lesson with:[/dim] archy learn <lesson-id>")
    console.print()


def render_lesson_start(lesson: Lesson) -> None:
    """Render lesson introduction."""
    level_color = {
        CausalLevel.ASSOCIATION: "green",
        CausalLevel.INTERVENTION: "yellow",
        CausalLevel.COUNTERFACTUAL: "red",
    }.get(lesson.level, "white")

    console.print()
    console.print(
        Panel(
            f"[bold]{lesson.title}[/bold]\n\n"
            f"{lesson.description}\n\n"
            f"[dim]Level {lesson.level.value}: {lesson.level.name.title()}[/dim]",
            title=f"[{level_color}]Lesson[/{level_color}]",
            border_style=level_color,
        )
    )
    console.print()


def render_step(step: TutorialStep, step_num: int, total_steps: int) -> None:
    """Render a tutorial step."""
    console.print()
    console.print(
        f"[dim]Step {step_num}/{total_steps}[/dim]",
    )
    console.print(f"[cyan]{step.instruction}[/cyan]")
    console.print()
    console.print(f"[bold white]{step.prompt}[/bold white]")
    if step.example:
        console.print(f"[dim]Example: [green]{step.example}[/green][/dim]")
    console.print()


def render_response(response: TutorialResponse) -> None:
    """Render tutorial response."""
    if response.success:
        console.print(f"[green]{response.message}[/green]")
    else:
        console.print(f"[red]{response.message}[/red]")


def render_graph(graph: Optional[CausalGraph]) -> None:
    """Render current graph state as Pearl-style ASCII diagram."""
    if not graph:
        console.print("[dim]No graph yet.[/dim]")
        return

    nodes = graph.get_nodes()

    if not nodes:
        console.print("[dim]Empty graph.[/dim]")
        return

    console.print()

    # Build ASCII diagram
    diagram = _build_ascii_diagram(graph)
    console.print(Panel(diagram, title="[bold]Causal Graph[/bold]", border_style="dim"))
    console.print()


def _build_ascii_diagram(graph: CausalGraph) -> str:
    """Build Pearl-style ASCII diagram of the graph."""
    nodes = graph.get_nodes()
    edges = graph.get_edges()

    if not edges:
        # Just isolated nodes
        return "  ".join(f"[cyan]({n})[/cyan]" for n in sorted(nodes))

    # Identify layers (topological ordering)
    layers = _get_layers(graph)
    edge_set = set(edges)

    # Build the diagram
    lines = []

    # Track which edges we've shown
    shown_edges: set[tuple[str, str]] = set()

    # Draw nodes layer by layer with arrows between
    for i, layer in enumerate(layers):
        # Node line
        node_line = "    ".join(f"[cyan]({n})[/cyan]" for n in layer)
        lines.append(f"  {node_line}")

        # Arrow lines to next layer
        if i < len(layers) - 1:
            arrow_lines, new_shown = _draw_arrows_with_tracking(
                layer, layers[i + 1], edge_set
            )
            shown_edges.update(new_shown)
            lines.extend(arrow_lines)

    # Show any edges that weren't displayed (cross-layer edges)
    missing_edges = edge_set - shown_edges
    if missing_edges:
        lines.append("")
        lines.append(
            "[dim]Also:[/dim] "
            + ", ".join(f"[yellow]{p}→{c}[/yellow]" for p, c in sorted(missing_edges))
        )

    return "\n".join(lines)


def _draw_arrows_with_tracking(
    from_layer: list[str], to_layer: list[str], edges: set[tuple[str, str]]
) -> tuple[list[str], set[tuple[str, str]]]:
    """Draw arrows and return which edges were shown."""
    shown: set[tuple[str, str]] = set()
    lines: list[str] = []

    # Find which edges connect these layers
    connections = []
    for f in from_layer:
        for t in to_layer:
            if (f, t) in edges:
                connections.append((f, t))
                shown.add((f, t))

    if not connections:
        return [""], shown

    # Check for diagonal arrows (cross connections)
    has_diagonal = any(
        from_layer.index(f) != to_layer.index(t) if t in to_layer else False
        for f, t in connections
        if f in from_layer
    )

    if has_diagonal and len(from_layer) <= 3 and len(to_layer) <= 3:
        lines.append(_draw_diagonal_arrows(from_layer, to_layer, edges))
    else:
        # Simple vertical arrows
        arrow_parts = []
        for f in from_layer:
            has_child = any((f, t) in edges for t in to_layer)
            arrow_parts.append("   ↓   " if has_child else "       ")
        lines.append("".join(arrow_parts))

    return lines, shown


def _get_layers(graph: CausalGraph) -> list[list[str]]:
    """Get nodes organized into layers (roots first, then children, etc.)."""
    nodes = set(graph.get_nodes())
    layers = []
    placed = set()

    # First layer: roots (no parents)
    roots = [n for n in nodes if not graph.get_parents(n)]
    if roots:
        layers.append(sorted(roots))
        placed.update(roots)
    elif nodes:
        # No roots (cycle?), just pick first alphabetically
        first = sorted(nodes)[0]
        layers.append([first])
        placed.add(first)

    # Subsequent layers: nodes whose parents are all placed
    while placed != nodes:
        next_layer = []
        for n in nodes - placed:
            parents = graph.get_parents(n)
            if parents <= placed:  # All parents are placed
                next_layer.append(n)

        if next_layer:
            layers.append(sorted(next_layer))
            placed.update(next_layer)
        else:
            # Remaining nodes have unplaceable dependencies, add them
            remaining = sorted(nodes - placed)
            layers.append(remaining)
            placed.update(remaining)

    return layers


def _draw_arrows(
    from_layer: list[str], to_layer: list[str], edges: set, graph: CausalGraph
) -> list[str]:
    """Draw arrows between two layers."""
    lines = []

    # Find which edges connect these layers
    connections = []
    for f in from_layer:
        for t in to_layer:
            if (f, t) in edges:
                connections.append((f, t))

    if not connections:
        return [""]

    # Simple arrow representation
    # For each node in from_layer, show arrows to its children in to_layer
    arrow_parts = []
    for f in from_layer:
        children_in_next = [t for t in to_layer if (f, t) in edges]
        if len(children_in_next) == 1:
            arrow_parts.append("   ↓   ")
        elif len(children_in_next) > 1:
            arrow_parts.append("  ↓ ↓  ")
        elif any((p, f) in edges for p in to_layer):
            # This node receives from next layer (shouldn't happen in DAG)
            arrow_parts.append("   ↑   ")
        else:
            arrow_parts.append("       ")

    # Check for diagonal arrows (cross connections)
    has_diagonal = False
    for i, f in enumerate(from_layer):
        for j, t in enumerate(to_layer):
            if (f, t) in edges and i != j:
                has_diagonal = True

    if has_diagonal and len(from_layer) <= 3 and len(to_layer) <= 3:
        # Try to show diagonal arrows for small graphs
        lines.append(_draw_diagonal_arrows(from_layer, to_layer, edges))
    else:
        lines.append("".join(arrow_parts))

    return lines


def _draw_diagonal_arrows(
    from_layer: list[str], to_layer: list[str], edges: set
) -> str:
    """Draw diagonal arrows for fork/collider patterns."""
    # Common patterns:
    # Fork (confounder): one node pointing to multiple in next layer
    # Collider: multiple nodes pointing to one in next layer

    if len(from_layer) == 1 and len(to_layer) == 2:
        # Fork pattern: Z -> X, Z -> Y
        f = from_layer[0]
        if (f, to_layer[0]) in edges and (f, to_layer[1]) in edges:
            return "    ↙   ↘"

    if len(from_layer) == 2 and len(to_layer) == 1:
        # Collider pattern: X -> Z, Y -> Z
        t = to_layer[0]
        if (from_layer[0], t) in edges and (from_layer[1], t) in edges:
            return "    ↘   ↙"

    if len(from_layer) == 1 and len(to_layer) == 1:
        return "      ↓"

    # Mixed - just show vertical arrows
    arrows = []
    for f in from_layer:
        has_child = any((f, t) in edges for t in to_layer)
        arrows.append("  ↓  " if has_child else "     ")
    return "".join(arrows)


def render_lesson_complete(lesson: Lesson) -> None:
    """Render lesson completion message."""
    console.print()
    console.print(
        Panel(
            f"[bold green]Congratulations![/bold green]\n\n"
            f"You completed: [cyan]{lesson.title}[/cyan]\n\n"
            f"[dim]Continue learning with 'archy learn --list'[/dim]",
            title="Lesson Complete",
            border_style="green",
        )
    )
    console.print()


def render_commands_help() -> None:
    """Render available commands during tutorial."""
    table = Table(title="Tutorial Commands", show_header=True)
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="white")

    commands = [
        ("add edge X Y", "Add causal edge X -> Y"),
        ("add node X", "Add isolated node X"),
        ("remove edge X Y", "Remove edge X -> Y"),
        ("show", "Display current graph"),
        ("parents X", "Show parents of X"),
        ("children X", "Show children of X"),
        ("dsep X Y", "Check if X and Y are d-separated"),
        ("dsep X Y given Z", "Check d-separation conditioning on Z"),
        ("paths X Y", "Find backdoor paths from X to Y"),
        ("hint", "Get a hint for current step"),
        ("skip", "Skip to next step"),
        ("quit", "Exit tutorial"),
    ]

    for cmd, desc in commands:
        table.add_row(cmd, desc)

    console.print(table)
    console.print()


def render_progress(state: TutorialState, total_steps: int) -> None:
    """Render progress indicator."""
    completed = len(state.completed_steps)
    pct = int((completed / total_steps) * 100) if total_steps > 0 else 0
    bar_width = 20
    filled = int(bar_width * completed / total_steps) if total_steps > 0 else 0
    bar = (
        "[green]"
        + "#" * filled
        + "[/green]"
        + "[dim]"
        + "-" * (bar_width - filled)
        + "[/dim]"
    )

    console.print(f"Progress: [{bar}] {pct}% ({completed}/{total_steps})")


def get_prompt() -> str:
    """Get user input with prompt."""
    try:
        return console.input("[bold cyan]>[/bold cyan] ")
    except (EOFError, KeyboardInterrupt):
        return "quit"
