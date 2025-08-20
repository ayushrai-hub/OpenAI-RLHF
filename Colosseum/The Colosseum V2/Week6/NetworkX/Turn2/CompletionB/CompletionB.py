def l4(raw_input: str, plot: bool) -> str:
    lines = raw_input.strip().splitlines()
    n: int = int(lines.pop(0))

    output: list[str] = []

    graph_i = 0
    while lines:
        graph_i += 1
        lawn_width, lawn_height = map(int, lines.pop(0).split())
        lawn: list[list[str]] = [list(row) for row in lines[:lawn_height]]
        lines = lines[lawn_height:]

        # Create a Lattice object from the lawn
        lattice = Lattice.from_grid(lawn)
        
        unvisited = [n for n in lattice.graph.nodes if lattice.label_dict[n] == '.']
        if not unvisited:
            output.append("")
            continue
        
        source = unvisited[0]
        visited = set()
        
        def translate_to_wasd(path: list[Point]) -> str:
            wasd = ""
            for i in range(1, len(path)):
                dx, dy = path[i].x - path[i-1].x, path[i].y - path[i-1].y
                if dx == 1:
                    wasd += "D"
                elif dx == -1:
                    wasd += "A"
                elif dy == 1:
                    wasd += "S"
                elif dy == -1:
                    wasd += "W"
            return wasd

        for node in unvisited[1:]:
            if nx.has_path(lattice.graph, source, node):
                path = nx.shortest_path(lattice.graph, source, target=node)
                visited.update(path)
                output.append(translate_to_wasd(path))
        
        if plot:
            plt.title(f"Lawn {graph_i}")
            lattice.plot(node_color='cyan')
            plt.show()

    return "\n".join(output)
gfdgdfgfdg