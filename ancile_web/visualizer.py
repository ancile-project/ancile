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
    def __init__(self, id_num, content, args, children=None):
        self.id_num = id_num
        self.content = content
        self.children = children or []
        self.visited = False
        self.args = param_cell_to_str(args)

class SpecialNode():

    """
        A special node is a container node for
        loops, it saves the top and bottom nodes of
        the loop tree
    """
    def __init__(self, inner_tree, children=None):
        self.inner_tree = inner_tree
        self.leaves = get_bottom(inner_tree)
        self.children = children or []
        self.visited = False

def get_bottom(tree):
    """
        Returns the bottom elements of a tree.

        :param tree: Tree list
        :return List of nodes
    """
    children = []
    for node in tree:
        if node.children:
            children += get_bottom(node.children)
        else:
            children.append(node)
    return children

def traverse_tree(policy, count=0, children=None):
    """
        Traverses policy list and generates a tree.

        :param policy: Parsed policy list
        :param count: The current index of the node
        :param children: Children of the node
        :return List of nodes
    """

    operator, first = policy[:2]

    if operator == "exec":
        return [Node(count, first, policy[2], children)], count+1

    if operator == "concat":

        second_node, count = traverse_tree(policy[2], count, children)
        return traverse_tree(first, count, second_node)

    if operator == "union":

        first_node, count = traverse_tree(first, count, children)
        second_node, count = traverse_tree(policy[2], count, children)

        return first_node + second_node, count

    inner_tree, count = traverse_tree(first, count)
    return [SpecialNode(inner_tree, children)], count

def visualize_policies(tree):
    """
        Traverses a policy tree and generates
        a mermaid-friendly graph.

        :param tree: List of tree nodes
        :return MermaidJS Tree
    """
    content = "graph TD\n"
    connections = set()
    stack = tree.copy()
    while stack:
        node = stack.pop()


        if node.visited:
            continue

        node.visited = True

        if isinstance(node, SpecialNode):
            for leaf in node.leaves:
                for parent in node.inner_tree:
                    stack.append(parent)

                    connection = f"A{leaf.id_num} --> A{parent.id_num}"
                    connections.add(connection)

                for child in node.children:
                    stack.append(child)

                    connection = f"A{leaf.id_num} --> A{child.id_num}"
                    connections.add(connection)


        else:
            args = args = "<div class=args>" + "<br/>".join(node.args) + "</div>"
            content += f"A{node.id_num}[\"{node.content} {args}\"]\n"
            for child in node.children:

                stack.append(child)

                if isinstance(child, SpecialNode):
                    for sub_child in child.children:

                        connection = f"A{node.id_num} --> A{sub_child.id_num}"
                        connections.add(connection)

                    for sub_child in child.inner_tree:

                        connection = f"A{node.id_num} --> A{sub_child.id_num}"
                        connections.add(connection)

                else:
                    connection = f"A{node.id_num} --> A{child.id_num}"
                    connections.add(connection)


    return content + '\n'.join(connections)

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

    top_nodes, _ = traverse_tree(parsed_policy)
    mermaid_string = visualize_policies(top_nodes)

    return {
        "status": "ok",
        "parsed_policy": mermaid_string
    }

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
