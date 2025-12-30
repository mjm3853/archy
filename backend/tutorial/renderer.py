"""Rich terminal rendering for tutorials."""

from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

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
    console.print()


def render_response(response: TutorialResponse) -> None:
    """Render tutorial response."""
    if response.success:
        console.print(f"[green]{response.message}[/green]")
    else:
        console.print(f"[red]{response.message}[/red]")


def render_graph(graph: Optional[CausalGraph]) -> None:
    """Render current graph state."""
    if not graph:
        console.print("[dim]No graph yet.[/dim]")
        return

    nodes = graph.get_nodes()
    edges = graph.get_edges()

    if not nodes:
        console.print("[dim]Empty graph.[/dim]")
        return

    console.print()

    # Simple tree view
    tree = Tree("[bold]Causal Graph[/bold]")

    # Show edges
    if edges:
        edges_str = ", ".join(f"{p}->{c}" for p, c in edges)
        tree.add(f"[yellow]Edges:[/yellow] {edges_str}")
    else:
        tree.add("[dim]No edges[/dim]")

    # Show nodes with their relationships
    nodes_branch = tree.add("[yellow]Nodes:[/yellow]")
    for node in sorted(nodes):
        parents = graph.get_parents(node)
        children = graph.get_children(node)
        parent_str = f" <- {{{', '.join(sorted(parents))}}}" if parents else ""
        child_str = f" -> {{{', '.join(sorted(children))}}}" if children else ""
        nodes_branch.add(f"[cyan]{node}[/cyan]{parent_str}{child_str}")

    console.print(tree)
    console.print()


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
