"""
    Utilities for visualizing policies using MermaidJS.
"""
import traceback
from ancile_core.policy import PolicyParser
from ancile_core.policy_sly import ParseError

class Node:

    """
        Simple structure to hold information on each node
        of the policy.
    """
    def __init__(self, name, content, args):
        self.name = name
        self.content = content
        self.children = []
        self.visited = False
        self.args = param_cell_to_str(args)

def parse_policy(policy):
    """
        Parses the policy using the parser in ancile_core and returns
        a JSON with either an error status and a traceback, or a mermaid-ready
        graph representation.

        :param policy: Policy string
        :return Dictionary with status and parsed_policy (or traceback)
    """
    try:
        parsed_policy = PolicyParser.parse_it(policy)
    except ParseError:
        return {
            "status": "error",
            "error": traceback.format_exc()
        }

    top_nodes = generate_tree(parsed_policy, "", 0)
    mermaid_string = visualize_nodes(top_nodes)

    return {
        "status": "ok",
        "parsed_policy": mermaid_string
    }

def return_lowest(nodes):
    """
        Finds the lowest node when given a list of nodes.

        :param nodes: List of nodes
        :return List of lowest nodes in tree
    """
    stack = nodes.copy()
    already_visited = set()
    children = []
    while stack:
        current_node = stack.pop()
        if current_node.name in already_visited:
            continue

        if not current_node.children or [current_node] == current_node.children:
            children.append(current_node)

        add_self = False

        for child in current_node.children:
            if child.name in already_visited:
                add_self = True
                if child not in children:
                    children.append(child)

        if add_self:
            children.append(current_node)

        already_visited.add(current_node.name)

    return children

def visualize_nodes(nodes):
    """
        Generates MermaidJS tree using a policy tree.

        :param nodes: List of nodes.
        :return MermaidJS-ready string.
    """
    stack = nodes.copy()
    content = "graph TD\n"
    connected = set()
    while stack:
        node = stack.pop()
        if node.visited:
            continue

        params = '<br />' + '<br />'.join(node.args)

        content += f"{node.name}[{node.content}{params}]\n"
        node.visited = True

        for child in node.children:
            stack.append(child)

            connection = f"{node.name} --> {child.name}\n"

            if connection not in connected:
                content += connection
                connected.add(connection)

    return content

def generate_tree(policy_list, branch, node_id):
    """
        Generates policy tree from a policy list.

        :param policy_list: Policy list given by the user.
        :param branch: Current branch (in case of unions)
        :param node_id: Current ID (increments as we move along the list)
    """

    operator, first = policy_list[:2]

    if operator == "exec":
        node = Node(f"{branch}{node_id}", first, policy_list[2])
        return [node]

    if operator == "concat":
        nodes = generate_tree(first, branch, node_id)
        children = return_lowest(nodes)

        second_node = generate_tree(policy_list[2], branch, node_id+1)

        for child in children:
            child.children += second_node

        if first[0] == "star":
            return nodes + second_node

        return nodes

    if operator == "union":
        nodes = generate_tree(first, branch+"A", node_id)
        second_node = generate_tree(policy_list[2], branch+"B", node_id)
        return nodes + second_node

    if operator == "star":

        nodes = generate_tree(first, branch, node_id)
        children = return_lowest(nodes)

        for child in children:
            child.children += nodes

        return nodes + children

    return []

def param_cell_to_str(param_cells):
    """
        Generates a string representation of ParamCells.

        :param param_cells: ParamCell dictionary.
        :return List of ParamCell string representations.
    """
    params = []
    for param_cell in param_cells.values():
        operator = param_cell.op
        string = f"{param_cell.name}"

        if operator(1, 1):
            if operator(1, 2):
                string += " <= "
            elif operator(2, 1):
                string += " >= "
            else:
                string += " = "
        elif operator(1, 2) and operator(2, 1):
            string += " != "
        elif operator(2, 1):
            string += " > "
        else:
            string += " < "
        string += str(param_cell.value)
        params.append(string)
    return params
