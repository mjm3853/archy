"""Main CLI entry point."""

from __future__ import annotations

import json
import sys
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from backend import CausalGraph, IntervenedGraph
from backend.tutorial import TutorialEngine
from backend.tutorial.content import get_all_lessons
from backend.tutorial import renderer as tutorial_renderer

console = Console()
err_console = Console(stderr=True)


def read_graph_from_stdin() -> Optional[dict]:
    """Read graph JSON from stdin if available."""
    if not sys.stdin.isatty():
        try:
            return json.load(sys.stdin)
        except json.JSONDecodeError:
            return None
    return None


def write_graph_to_stdout(graph: CausalGraph) -> None:
    """Write graph as JSON to stdout."""
    click.echo(json.dumps(graph.to_dict()))


def show_welcome() -> None:
    """Show welcome message with usage info."""
    from backend import __version__

    console.print(f"\n[bold cyan]archy[/bold cyan] v{__version__}", highlight=False)
    console.print(
        "[dim]Causal AI toolkit - do-calculus, interventions, counterfactuals[/dim]\n"
    )

    # Quick examples with meaningful names
    console.print("[bold]Quick Start:[/bold]")
    console.print(
        '  [green]archy graph -c "Smoking Tar Cancer"[/green]   Create a mediation chain'
    )
    console.print(
        "  [green]archy graph -e Age Treatment -e Age Outcome -e Treatment Outcome[/green]"
    )
    console.print(
        "                                           Create a confounded graph"
    )
    console.print("  [green]archy graph ... --json | archy do Treatment[/green]")
    console.print("                                           Apply intervention\n")

    # Command summary table
    table = Table(title="Commands", show_header=True, header_style="bold")
    table.add_column("Command", style="cyan")
    table.add_column("Description")
    table.add_row("graph", "Create a causal graph from edges")
    table.add_row("do", "Apply do-intervention (remove incoming edges)")
    table.add_row("info", "Display graph information")
    table.add_row("dsep", "Check d-separation between variables")
    table.add_row("paths", "Find backdoor paths between variables")
    table.add_row("examples", "Show example causal structures")
    table.add_row("[bold]learn[/bold]", "[bold]Interactive tutorial[/bold]")
    console.print(table)

    console.print("\n[dim]Use --json flag to pipe between commands.[/dim]")
    console.print("[dim]Run 'archy learn' for interactive tutorial.[/dim]\n")


@click.group(invoke_without_command=True)
@click.version_option(package_name="archy")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Archy - Causal AI toolkit.

    Unix-style commands for causal graphs, interventions, and do-calculus.
    Commands can be piped together using JSON.

    \b
    Examples:
        archy graph -e X Y -e Y Z          # Create graph
        archy graph -e X Y | archy info    # Pipe to info
        archy graph -e X Y | archy do X    # Apply intervention
    """
    if ctx.invoked_subcommand is None:
        show_welcome()


@cli.command()
@click.option(
    "-e", "--edge", "edges", nargs=2, multiple=True, help="Add edge: -e FROM TO"
)
@click.option(
    "-c",
    "--chain",
    "chains",
    multiple=True,
    help='Add chain: -c "A B C" (creates A→B→C) - use quotes!',
)
@click.option("-n", "--node", "nodes", multiple=True, help="Add isolated node")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON for piping")
@click.argument("extra_args", nargs=-1)
def graph(
    edges: tuple, chains: tuple, nodes: tuple, as_json: bool, extra_args: tuple
) -> None:
    """Create a causal graph.

    \b
    Examples:
        archy graph -e X Y -e Y Z           # Two edges
        archy graph -c "X Y Z"              # Chain: X→Y→Z (use quotes!)
        archy graph -c "A B C" -e D B       # Chain + edge
        archy graph -e X Y --json | archy info
    """
    # Check for common mistake: unquoted chain arguments
    if extra_args and chains:
        err_console.print(
            f"[red]Error:[/red] Unexpected arguments: {' '.join(extra_args)}\n"
        )
        err_console.print(
            "[yellow]Hint:[/yellow] The -c/--chain option requires quotes around the node list:"
        )
        err_console.print(
            f'  [green]archy graph -c "{chains[0]} {" ".join(extra_args)}"[/green]\n'
        )
        sys.exit(1)
    elif extra_args:
        err_console.print(
            f"[red]Error:[/red] Unexpected arguments: {' '.join(extra_args)}\n"
        )
        err_console.print("Use -e for edges or -c for chains. See 'archy graph --help'")
        sys.exit(1)

    edge_list = [(e[0], e[1]) for e in edges]

    # Parse chains into edges
    for chain in chains:
        chain_nodes = chain.split()
        if len(chain_nodes) < 2:
            err_console.print(
                f"[red]Error:[/red] Chain '{chain}' needs at least 2 nodes.\n"
            )
            err_console.print(
                "[yellow]Hint:[/yellow] Use quotes around multiple nodes:"
            )
            err_console.print('  [green]archy graph -c "A B C"[/green]')
            sys.exit(1)
        for i in range(len(chain_nodes) - 1):
            edge_list.append((chain_nodes[i], chain_nodes[i + 1]))

    try:
        g = CausalGraph(edges=edge_list if edge_list else None)
        for node in nodes:
            if node not in g.get_nodes():
                g._graph.add_node(node)
    except ValueError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    if as_json:
        write_graph_to_stdout(g)
    else:
        _print_graph_visual(g)


@cli.command()
@click.argument("variables", nargs=-1)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON for piping")
def do(variables: tuple, as_json: bool) -> None:
    """Apply do-intervention on variables.

    Reads graph from stdin, removes incoming edges to intervened variables.

    \b
    Examples:
        archy graph -e X Y -e Z Y --json | archy do Y
        archy graph -e X Y --json | archy do X Y
    """
    data = read_graph_from_stdin()
    if not data:
        err_console.print(
            "[red]Error:[/red] No graph provided. Pipe a graph to this command."
        )
        sys.exit(1)

    if not variables:
        err_console.print(
            "[red]Error:[/red] Specify at least one variable to intervene on."
        )
        sys.exit(1)

    try:
        g = CausalGraph.from_dict(data)
        intervened = IntervenedGraph(g, set(variables))

        # Create new CausalGraph from intervened edges
        result = CausalGraph(
            edges=intervened.get_edges() if intervened.get_edges() else None
        )
        for node in intervened.get_nodes():
            if node not in result.get_nodes():
                result._graph.add_node(node)

    except ValueError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    if as_json:
        write_graph_to_stdout(result)
    else:
        var_str = ", ".join(variables)
        console.print(f"[bold]After do({var_str}):[/bold]")
        _print_graph_visual(result)


@cli.command()
def info() -> None:
    """Display graph information.

    \b
    Examples:
        archy graph -e X Y -e Z Y | archy info
    """
    data = read_graph_from_stdin()
    if not data:
        err_console.print(
            "[red]Error:[/red] No graph provided. Pipe a graph to this command."
        )
        sys.exit(1)

    try:
        g = CausalGraph.from_dict(data)
    except ValueError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    _print_graph_info(g)


@cli.command()
@click.argument("x")
@click.argument("y")
@click.option("-g", "--given", multiple=True, help="Conditioning variables")
def dsep(x: str, y: str, given: tuple) -> None:
    """Check d-separation between X and Y given Z.

    \b
    Examples:
        archy graph -e X Y -e Z Y | archy dsep X Z -g Y
    """
    data = read_graph_from_stdin()
    if not data:
        err_console.print(
            "[red]Error:[/red] No graph provided. Pipe a graph to this command."
        )
        sys.exit(1)

    try:
        g = CausalGraph.from_dict(data)
        result = g.is_d_separated({x}, {y}, set(given))
    except Exception as e:
        err_console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    given_str = f" | {', '.join(given)}" if given else ""
    symbol = "⫫" if result else "⫫̸"
    status = "[green]Yes[/green]" if result else "[red]No[/red]"

    console.print(f"{x} {symbol} {y}{given_str}: {status}")


@cli.command()
@click.argument("treatment")
@click.argument("outcome")
def paths(treatment: str, outcome: str) -> None:
    """Find backdoor paths between treatment and outcome.

    \b
    Examples:
        archy graph -e X Y -e Z X -e Z Y | archy paths X Y
    """
    data = read_graph_from_stdin()
    if not data:
        err_console.print(
            "[red]Error:[/red] No graph provided. Pipe a graph to this command."
        )
        sys.exit(1)

    try:
        g = CausalGraph.from_dict(data)
        backdoor = g.get_backdoor_paths(treatment, outcome)
    except Exception as e:
        err_console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    console.print(f"[bold]Backdoor paths from {treatment} to {outcome}:[/bold]")
    if backdoor:
        for path in backdoor:
            console.print(f"  [yellow]{'[/yellow] → [yellow]'.join(path)}[/yellow]")
    else:
        console.print("  [green]None (no confounding)[/green]")


# Example causal structures
CAUSAL_EXAMPLES = {
    "confounder": {
        "name": "Confounder (Common Cause)",
        "description": "Age affects both Treatment choice and Outcome, creating spurious correlation",
        "diagram": "Age → Treatment → Outcome\n  └──────────────↗",
        "command": "archy graph -e Age Treatment -e Age Outcome -e Treatment Outcome",
        "insight": "Must control for Age to estimate Treatment→Outcome effect",
    },
    "mediator": {
        "name": "Mediator (Causal Chain)",
        "description": "Smoking causes Cancer through Tar deposits in lungs",
        "diagram": "Smoking → Tar → Cancer",
        "command": 'archy graph -c "Smoking Tar Cancer"',
        "insight": "Tar mediates the effect; don't control for it when estimating total effect",
    },
    "collider": {
        "name": "Collider (Common Effect)",
        "description": "Both Talent and Luck affect Success; conditioning on Success creates bias",
        "diagram": "Talent → Success ← Luck",
        "command": "archy graph -e Talent Success -e Luck Success",
        "insight": "Never control for a collider - it opens a spurious path between causes",
    },
    "frontdoor": {
        "name": "Front-Door Criterion",
        "description": "Unmeasured Genotype confounds Smoking→Cancer, but Tar provides front-door path",
        "diagram": "Genotype → Smoking → Tar → Cancer\n    └──────────────────────↗",
        "command": "archy graph -e Genotype Smoking -e Genotype Cancer -e Smoking Tar -e Tar Cancer",
        "insight": "Can identify causal effect via Tar even with unmeasured confounding",
    },
    "instrumental": {
        "name": "Instrumental Variable",
        "description": "Price affects Demand only through Quantity (instrument for supply/demand)",
        "diagram": "Price → Quantity → Revenue\n             ↑\n          Demand",
        "command": "archy graph -e Price Quantity -e Quantity Revenue -e Demand Quantity -e Demand Revenue",
        "insight": "Price is an instrument: affects Revenue only through Quantity",
    },
    "m-bias": {
        "name": "M-Bias (Butterfly)",
        "description": "Controlling for M creates bias between Treatment and Outcome",
        "diagram": "U1 → Treatment    Outcome ← U2\n  ↘      ↓           ↑    ↙\n     →   M   ←────────",
        "command": "archy graph -e U1 Treatment -e U1 M -e U2 Outcome -e U2 M -e Treatment Outcome",
        "insight": "Don't control for M - it's a collider that induces bias",
    },
}


@cli.command()
@click.argument("structure", required=False)
@click.option("--run", is_flag=True, help="Run the example command and show the graph")
def examples(structure: Optional[str], run: bool) -> None:
    """Show example causal structures.

    \b
    Structures:
        confounder    - Common cause (Age→Treatment, Age→Outcome)
        mediator      - Causal chain (Smoking→Tar→Cancer)
        collider      - Common effect (Talent→Success←Luck)
        frontdoor     - Front-door criterion example
        instrumental  - Instrumental variable example
        m-bias        - M-bias/butterfly structure

    \b
    Examples:
        archy examples              # List all structures
        archy examples confounder   # Show confounder details
        archy examples mediator --run   # Show and run mediator example
    """
    if structure is None:
        # List all examples
        console.print("\n[bold cyan]Causal Structure Examples[/bold cyan]\n")

        table = Table(show_header=True, header_style="bold")
        table.add_column("Structure", style="cyan")
        table.add_column("Description")
        table.add_column("Pattern")

        for key, ex in CAUSAL_EXAMPLES.items():
            table.add_row(key, ex["name"], ex["diagram"].split("\n")[0])

        console.print(table)
        console.print("\n[dim]Run 'archy examples <structure>' for details[/dim]")
        console.print(
            "[dim]Run 'archy examples <structure> --run' to see the graph[/dim]\n"
        )
        return

    if structure not in CAUSAL_EXAMPLES:
        err_console.print(f"[red]Error:[/red] Unknown structure '{structure}'")
        err_console.print(f"Available: {', '.join(CAUSAL_EXAMPLES.keys())}")
        sys.exit(1)

    ex = CAUSAL_EXAMPLES[structure]

    console.print(f"\n[bold cyan]{ex['name']}[/bold cyan]\n")
    console.print(f"[dim]{ex['description']}[/dim]\n")

    console.print("[bold]Diagram:[/bold]")
    for line in ex["diagram"].split("\n"):
        console.print(f"  [yellow]{line}[/yellow]")
    console.print()

    console.print("[bold]Command:[/bold]")
    console.print(f"  [green]{ex['command']}[/green]\n")

    console.print("[bold]Insight:[/bold]")
    console.print(f"  {ex['insight']}\n")

    if run:
        console.print("[bold]Graph:[/bold]")
        # Parse and execute the command
        import shlex

        args = shlex.split(ex["command"])
        # Remove 'archy graph' prefix
        args = args[2:]

        # Parse the arguments manually
        edges = []
        chains = []
        i = 0
        while i < len(args):
            if args[i] in ("-e", "--edge"):
                edges.append((args[i + 1], args[i + 2]))
                i += 3
            elif args[i] in ("-c", "--chain"):
                chains.append(args[i + 1])
                i += 2
            else:
                i += 1

        edge_list = list(edges)
        for chain in chains:
            chain_nodes = chain.split()
            for j in range(len(chain_nodes) - 1):
                edge_list.append((chain_nodes[j], chain_nodes[j + 1]))

        try:
            g = CausalGraph(edges=edge_list)
            _print_graph_visual(g)
        except ValueError as e:
            err_console.print(f"[red]Error:[/red] {e}")


def _print_graph_visual(g: CausalGraph) -> None:
    """Print a visual representation of the graph."""
    nodes = g.get_nodes()
    edges = g.get_edges()

    if not nodes:
        console.print("[dim]Empty graph[/dim]")
        return

    # Build tree from roots
    roots = [n for n in nodes if not g.get_parents(n)]
    if not roots:
        roots = nodes[:1]  # Fallback if cyclic (shouldn't happen)

    tree = Tree("[bold]Causal Graph[/bold]")

    # Show edges
    edge_str = ", ".join(f"{p}→{c}" for p, c in edges) if edges else "none"
    tree.add(f"[dim]Edges:[/dim] {edge_str}")

    # Show nodes with their relationships
    for node in sorted(nodes):
        parents = g.get_parents(node)
        children = g.get_children(node)
        parent_str = f" ← {{{', '.join(sorted(parents))}}}" if parents else ""
        child_str = f" → {{{', '.join(sorted(children))}}}" if children else ""
        tree.add(f"[cyan]{node}[/cyan]{parent_str}{child_str}")

    console.print(tree)


def _print_graph_info(g: CausalGraph) -> None:
    """Print detailed graph information."""
    nodes = g.get_nodes()
    edges = g.get_edges()

    table = Table(title="Graph Information")
    table.add_column("Property", style="bold")
    table.add_column("Value")

    table.add_row("Nodes", str(len(nodes)))
    table.add_row("Edges", str(len(edges)))
    table.add_row("Node list", ", ".join(sorted(nodes)) if nodes else "-")

    # Find roots and leaves
    roots = [n for n in nodes if not g.get_parents(n)]
    leaves = [n for n in nodes if not g.get_children(n)]

    table.add_row("Roots (no parents)", ", ".join(sorted(roots)) if roots else "-")
    table.add_row("Leaves (no children)", ", ".join(sorted(leaves)) if leaves else "-")

    console.print(table)

    # Edge list
    if edges:
        console.print("\n[bold]Edges:[/bold]")
        for parent, child in edges:
            console.print(f"  {parent} → {child}")


@cli.command()
@click.argument("lesson", required=False)
@click.option("--list", "show_list", is_flag=True, help="List available lessons")
@click.option("--help-commands", is_flag=True, help="Show tutorial commands")
def learn(lesson: Optional[str], show_list: bool, help_commands: bool) -> None:
    """Interactive tutorial for learning causal inference.

    \b
    Start guided lessons to learn:
      - Level 1: Causal graphs and d-separation
      - Level 2: Interventions and do-calculus
      - Level 3: Counterfactuals and SCMs

    \b
    Examples:
        archy learn              # Show welcome and lesson list
        archy learn --list       # List all lessons
        archy learn graph-basics # Start specific lesson
        archy learn confounder   # Learn about confounders
    """
    # Initialize engine with all lessons
    engine = TutorialEngine()
    for lesson_obj in get_all_lessons():
        engine.register_lesson(lesson_obj)

    # Show commands help
    if help_commands:
        tutorial_renderer.render_commands_help()
        return

    # List lessons
    if show_list or lesson is None:
        tutorial_renderer.render_welcome()
        tutorial_renderer.render_lesson_list(engine.list_lessons())
        return

    # Start specific lesson
    if not engine.start_lesson(lesson):
        err_console.print(f"[red]Error:[/red] Unknown lesson '{lesson}'")
        err_console.print(
            f"Available: {', '.join(ls.id for ls in engine.list_lessons())}"
        )
        sys.exit(1)

    current_lesson = engine.current_lesson
    if not current_lesson:
        return

    tutorial_renderer.render_lesson_start(current_lesson)

    # Interactive loop
    while True:
        step = engine.get_current_step()
        if not step:
            # Lesson complete
            tutorial_renderer.render_lesson_complete(current_lesson)
            break

        # Show current step
        total_steps = len(current_lesson.steps)
        step_num = (engine.state.step_index if engine.state else 0) + 1
        tutorial_renderer.render_step(step, step_num, total_steps)

        # Get user input
        user_input = tutorial_renderer.get_prompt()

        if user_input.lower() in ("quit", "exit", "q"):
            console.print("[dim]Tutorial paused.[/dim]")
            break

        if user_input.lower() == "help":
            tutorial_renderer.render_commands_help()
            continue

        # Process input
        response = engine.handle_input(user_input)
        tutorial_renderer.render_response(response)

        if response.show_graph:
            tutorial_renderer.render_graph(engine.graph)


if __name__ == "__main__":
    cli()
