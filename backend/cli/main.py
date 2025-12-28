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

    # Quick examples
    console.print("[bold]Quick Start:[/bold]")
    console.print(
        "  [green]archy graph -e X Y -e Y Z[/green]        Create a causal graph"
    )
    console.print(
        "  [green]archy graph -e X Y --json | archy do X[/green]  Apply intervention"
    )
    console.print(
        "  [green]archy --help[/green]                     Show all commands\n"
    )

    # Command summary table
    table = Table(title="Commands", show_header=True, header_style="bold")
    table.add_column("Command", style="cyan")
    table.add_column("Description")
    table.add_row("graph", "Create a causal graph from edges")
    table.add_row("do", "Apply do-intervention (remove incoming edges)")
    table.add_row("info", "Display graph information")
    table.add_row("dsep", "Check d-separation between variables")
    table.add_row("paths", "Find backdoor paths between variables")
    console.print(table)

    console.print("\n[dim]Use --json flag to pipe between commands.[/dim]")
    console.print("[dim]Run 'archy COMMAND --help' for command details.[/dim]\n")


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


if __name__ == "__main__":
    cli()
