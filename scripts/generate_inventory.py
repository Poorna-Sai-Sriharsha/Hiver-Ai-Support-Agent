import ast
import os


def get_imports(file_path: str) -> list[str]:
    """Extracts imports from a python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports
    except Exception as e:
        return [f"Error: {e}"]

def analyze_repository(root_dir: str):
    inventory = []

    for root, dirs, files in os.walk(root_dir):
        # Skip hidden dirs and artifacts for the source analysis
        if any(x in root for x in ['.git', '.claude', 'artifacts', '__pycache__', 'data']):
            continue

        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, root_dir)

            # Get file size and line count
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    line_count = len(lines)
            except Exception:
                line_count = 0

            imports = []
            if file.endswith('.py'):
                imports = get_imports(file_path)

            inventory.append({
                "file": rel_path,
                "type": os.path.splitext(file)[1],
                "lines": line_count,
                "imports": imports
            })

    return inventory

if __name__ == "__main__":
    ROOT = "C:/Users/perin/hiver-ai-support-agent"
    inventory = analyze_repository(ROOT)

    # Create Inventory MD
    with open("artifacts/REPOSITORY_INVENTORY.md", "w", encoding='utf-8') as f:
        f.write("# Repository Inventory\n\n")
        f.write("| File | Type | Lines | Imports |\n")
        f.write("|---|---|---|---|\n")
        for item in inventory:
            imports_str = ", ".join(item['imports']) if item['imports'] else "None"
            f.write(f"| {item['file']} | {item['type']} | {item['lines']} | {imports_str} |\n")

    # Create Dependency Graph MD
    with open("artifacts/DEPENDENCY_GRAPH.md", "w", encoding='utf-8') as f:
        f.write("# Dependency Graph\n\n")
        for item in inventory:
            if item['imports']:
                f.write(f"## {item['file']}\n")
                f.write("Imports:\n")
                f.writelines(f"- {imp}\n" for imp in item['imports'])
                f.write("\n")

    print("Inventory and Dependency Graph created successfully.")
