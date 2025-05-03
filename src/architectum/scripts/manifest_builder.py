import os
import ast
import yaml

# Directory to start from (app source)
ROOT_DIR = os.path.abspath('src/cryptotrader')

# Output manifest path inside architectum/project_overview
OUTPUT_PATH = os.path.abspath(os.path.join('src', 'architectum', 'project_overview', 'docs_manifest.yaml'))


def add_node(node_id, node_type, manifest, node_ids):
    """
    Add a node to the manifest if not already present.
    """
    if node_id not in node_ids:
        manifest['nodes'].append({'id': node_id, 'type': node_type})
        node_ids.add(node_id)


def build_manifest(root_dir):
    """
    Walk the source tree to build nodes, function definitions, and edges manifest.
    Returns the manifest dict.
    """
    manifest = {'nodes': [], 'edges': []}
    node_ids = set()
    # Map function names to their full IDs (file:func)
    defs_map = {}

    # First pass: collect folder, file, and function nodes
    for current_root, dirs, files in os.walk(root_dir):
        rel_root = os.path.relpath(current_root, root_dir).replace('\\', '/')
        folder_id = rel_root if rel_root != '.' else 'root'
        add_node(folder_id, 'folder', manifest, node_ids)

        # Subfolder edges
        for d in dirs:
            child_folder = os.path.join(rel_root, d).replace('\\', '/')
            add_node(child_folder, 'folder', manifest, node_ids)
            manifest['edges'].append({'from': folder_id, 'to': child_folder})

        # File nodes and file->function edges
        for fname in files:
            file_id = os.path.join(rel_root, fname).replace('\\', '/')
            add_node(file_id, 'file', manifest, node_ids)
            manifest['edges'].append({'from': folder_id, 'to': file_id})

            # Process Python files for functions
            if fname.endswith('.py'):
                file_path = os.path.join(current_root, fname)
                try:
                    with open(file_path, 'r', encoding='utf-8') as src_file:
                        tree = ast.parse(src_file.read(), filename=file_path)
                except Exception:
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_id = f"{fname}:{node.name}"
                        add_node(func_id, 'function', manifest, node_ids)
                        manifest['edges'].append({'from': file_id, 'to': func_id})
                        defs_map.setdefault(node.name, []).append(func_id)

    # Second pass: collect call edges (including cross-file)
    for current_root, dirs, files in os.walk(root_dir):
        rel_root = os.path.relpath(current_root, root_dir).replace('\\', '/')
        for fname in files:
            if not fname.endswith('.py'):
                continue
            file_id = os.path.join(rel_root, fname).replace('\\', '/')
            file_path = os.path.join(current_root, fname)
            try:
                with open(file_path, 'r', encoding='utf-8') as src_file:
                    tree = ast.parse(src_file.read(), filename=file_path)
            except Exception:
                continue

            class CallVisitor(ast.NodeVisitor):
                def __init__(self, current_func):
                    self.current = current_func
                    self.src_id = f"{fname}:{current_func}"
                def visit_Call(self, call_node):
                    if isinstance(call_node.func, ast.Name):
                        callee_name = call_node.func.id
                        if callee_name in defs_map:
                            for dst in defs_map[callee_name]:
                                manifest['edges'].append({'from': self.src_id, 'to': dst})
                    self.generic_visit(call_node)

            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    visitor = CallVisitor(node.name)
                    visitor.visit(node)

    return manifest


def main():
    manifest = build_manifest(ROOT_DIR)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as out_file:
        yaml.dump(manifest, out_file, sort_keys=False)
    print(f"Generated manifest with {len(manifest['nodes'])} nodes and {len(manifest['edges'])} edges at {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
