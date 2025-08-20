import re

def extract_code(code_graph):
    if code_graph.startswith('"') and code_graph.endswith('"'):
        piece = code_graph[1:-1]
        tidy_code = re.sub(r'\\', '', piece)
        snippet = tidy_code
    elif code_graph.startswith('```python'):
        expression = r"(import[\s\S]+?)(plot\s*=\s*create_chart\(data\))"
        search = re.search(expression, snippet)
        if search:
            extract = search.group(0)
            print("OUTPUT ++++++++++++++++++", extract)
        else:
            print("No search result")
    return snippet

def ensure_correct_format(snippet):
    elements = snippet.split('\n')
    formatted_lines = []
    format_level = None

    for line in elements:
        cut_line = line.lstrip()
        if cut_line.startswith('def '):
            format_level = 1
            formatted_lines.append(line)
        elif format_level is not None:
            if cut_line:
                formatted_lines.append(' ' * (format_level * 4) + cut_line)
            else:
                formatted_lines.append(line)
        else:
            formatted_lines.append(line)

    return '\n'.join(formatted_lines)
