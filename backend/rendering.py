"""Graph rendering utilities for terminal output.

Provides reusable ASCII diagram rendering for causal graphs.
"""

from backend.graph import CausalGraph


def render_graph_ascii(graph: CausalGraph, use_rich: bool = True) -> str:
    """Render a causal graph as ASCII art.

    Args:
        graph: The causal graph to render
        use_rich: Whether to include Rich markup for colors

    Returns:
        ASCII string representation of the graph
    """
    nodes = graph.get_nodes()
    edges = graph.get_edges()

    if not nodes:
        return _style("Empty graph", "dim", use_rich)

    if not edges:
        # Just isolated nodes
        node_strs = [_style(f"({n})", "cyan", use_rich) for n in sorted(nodes)]
        return "  ".join(node_strs)

    # Detect common patterns and render appropriately
    pattern = _detect_pattern(graph)

    if pattern == "chain":
        return _render_chain(graph, use_rich)
    elif pattern == "collider":
        return _render_collider(graph, use_rich)
    elif pattern == "fork":
        return _render_fork(graph, use_rich)
    else:
        return _render_layered(graph, use_rich)


def _style(text: str, style: str, use_rich: bool) -> str:
    """Apply Rich markup if enabled."""
    if use_rich:
        return f"[{style}]{text}[/{style}]"
    return text


def _detect_pattern(graph: CausalGraph) -> str:
    """Detect common causal patterns."""
    nodes = graph.get_nodes()
    edges = graph.get_edges()

    if len(nodes) <= 1:
        return "simple"

    # Count in-degree and out-degree for each node
    in_degree: dict[str, int] = {n: 0 for n in nodes}
    out_degree: dict[str, int] = {n: 0 for n in nodes}

    for parent, child in edges:
        out_degree[parent] = out_degree.get(parent, 0) + 1
        in_degree[child] = in_degree.get(child, 0) + 1

    # Chain: linear sequence (each node has at most 1 parent and 1 child)
    if all(in_degree[n] <= 1 and out_degree[n] <= 1 for n in nodes):
        return "chain"

    # Collider: one node with multiple parents, no children from those parents
    for n in nodes:
        if in_degree[n] >= 2 and out_degree[n] == 0:
            parents = graph.get_parents(n)
            if all(out_degree[p] == 1 for p in parents):
                return "collider"

    # Fork: one node with multiple children, no parents
    for n in nodes:
        if out_degree[n] >= 2 and in_degree[n] == 0:
            children = graph.get_children(n)
            if all(in_degree[c] == 1 for c in children):
                return "fork"

    return "complex"


def _render_chain(graph: CausalGraph, use_rich: bool) -> str:
    """Render a chain pattern horizontally: X → Y → Z"""
    nodes = graph.get_nodes()

    # Find the root (no parents)
    roots = [n for n in nodes if not graph.get_parents(n)]
    if not roots:
        return _render_layered(graph, use_rich)

    # Build chain by following edges
    chain = [roots[0]]
    current = roots[0]

    while True:
        children = graph.get_children(current)
        if not children:
            break
        next_node = sorted(children)[0]
        chain.append(next_node)
        current = next_node

    # Render horizontally
    arrow = _style(" → ", "dim", use_rich)
    node_strs = [_style(n, "cyan", use_rich) for n in chain]
    return arrow.join(node_strs)


def _render_collider(graph: CausalGraph, use_rich: bool) -> str:
    """Render a collider pattern: X → Y ← Z"""
    nodes = graph.get_nodes()

    # Find the collider node (multiple parents)
    collider = None
    for n in nodes:
        if len(graph.get_parents(n)) >= 2:
            collider = n
            break

    if not collider:
        return _render_layered(graph, use_rich)

    parents = sorted(graph.get_parents(collider))
    arrow_in = _style(" → ", "dim", use_rich)
    arrow_back = _style(" ← ", "dim", use_rich)
    collider_styled = _style(collider, "cyan", use_rich)

    if len(parents) == 2:
        # Simple two-parent collider: X → Y ← Z
        left = _style(parents[0], "cyan", use_rich)
        right = _style(parents[1], "cyan", use_rich)
        return f"{left}{arrow_in}{collider_styled}{arrow_back}{right}"
    else:
        # Multiple parents: show as list
        parent_strs = [_style(p, "cyan", use_rich) for p in parents]
        return f"{', '.join(parent_strs)}{arrow_in}{collider_styled}"


def _render_fork(graph: CausalGraph, use_rich: bool) -> str:
    """Render a fork pattern: X ← Z → Y"""
    nodes = graph.get_nodes()

    # Find the fork node (multiple children, no parents)
    fork = None
    for n in nodes:
        if len(graph.get_children(n)) >= 2 and not graph.get_parents(n):
            fork = n
            break

    if not fork:
        return _render_layered(graph, use_rich)

    children = sorted(graph.get_children(fork))
    arrow_out = _style(" → ", "dim", use_rich)
    arrow_back = _style(" ← ", "dim", use_rich)
    fork_styled = _style(fork, "cyan", use_rich)

    if len(children) == 2:
        # Simple two-child fork: X ← Z → Y
        left = _style(children[0], "cyan", use_rich)
        right = _style(children[1], "cyan", use_rich)
        return f"{left}{arrow_back}{fork_styled}{arrow_out}{right}"
    else:
        # Multiple children: show as list
        child_strs = [_style(c, "cyan", use_rich) for c in children]
        return f"{fork_styled}{arrow_out}{', '.join(child_strs)}"


def _render_layered(graph: CausalGraph, use_rich: bool) -> str:
    """Render complex graphs with layers and edge list."""
    edges = graph.get_edges()
    layers = _get_layers(graph)

    lines = []

    # Show nodes by layer
    for i, layer in enumerate(layers):
        prefix = _style(f"L{i + 1}: ", "dim", use_rich)
        node_strs = [_style(n, "cyan", use_rich) for n in sorted(layer)]
        lines.append(prefix + "  ".join(node_strs))

    # Show edges
    if edges:
        lines.append("")
        arrow = _style("→", "yellow", use_rich)
        edge_strs = [f"{p} {arrow} {c}" for p, c in sorted(edges)]
        lines.append(_style("Edges: ", "dim", use_rich) + ", ".join(edge_strs))

    return "\n".join(lines)


def _get_layers(graph: CausalGraph) -> list[list[str]]:
    """Get nodes organized into layers (roots first, then children, etc.)."""
    nodes = set(graph.get_nodes())
    layers: list[list[str]] = []
    placed: set[str] = set()

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


def render_edges_list(graph: CausalGraph, use_rich: bool = True) -> str:
    """Render just the edges as a simple list."""
    edges = graph.get_edges()
    if not edges:
        return _style("No edges", "dim", use_rich)

    arrow = _style("→", "yellow", use_rich)
    return ", ".join(f"{p} {arrow} {c}" for p, c in sorted(edges))
