"""
    Utilities for visualizing policies using MermaidJS.
"""
from enum import Enum
import traceback
from ancile.core.primitives.policy import PolicyParser
from ancile.utils.errors import ParseError

class NodeType(Enum):
    STAR = 1
    NEG = 2
    INTERSECT = 3
    UNION = 4

OPERATORS = {
    NodeType.NEG: "NOT",
    NodeType.INTERSECT: "AND",
    NodeType.UNION: "OR"
}

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

    def __repr__(self):
        return f"Node(A{self.id_num}, {self.content}, {self.args})"


class SpecialNode():

    """
        A special node is a container node for
        loops, it saves the top and bottom nodes of
        the loop tree
    """
    def __init__(self, inner_tree, children, node_type):
        self.inner_tree = inner_tree
        self.leaves = get_bottom(inner_tree)
        self.children = children or []
        self.visited = False
        self.node_type = node_type
    
    def __repr__(self):
        return str(self.inner_tree)

def get_bottom(tree):
    """
        Returns the bottom elements of a tree.

        :param tree: Tree list
        :returns List of nodes
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
        :returns List of nodes
    """

    operator, first = policy[:2]

    if operator == "exec":
        return [Node(count, first, policy[2], children)], count+1

    if operator == "concat":

        second_node, count = traverse_tree(policy[2], count, children)
        return traverse_tree(first, count, second_node)

    if operator == "union":

        first_node, count = traverse_tree(first, count)
        second_node, count = traverse_tree(policy[2], count)

        return [SpecialNode(first_node + second_node, children, NodeType.UNION)], count

    if operator == "intersect":
        first_side, count = traverse_tree(first, count)
        second_side, count = traverse_tree(policy[2], count)
        inner_tree = first_side + second_side
        return [SpecialNode(inner_tree, children, NodeType.INTERSECT)], count
    
    inner_tree, count = traverse_tree(first, count)

    if operator == "star":
        return [SpecialNode(inner_tree, children, NodeType.STAR)], count

    return [SpecialNode(inner_tree, children, NodeType.NEG)], count

def visualize_policies(tree, start="graph TD\n"):
    """
        Traverses a policy tree and generates
        a mermaid-friendly graph.

        :param tree: List of tree nodes
        :returns MermaidJS Tree
    """
    content = start
    connections = set()
    stack = tree.copy()
    while stack:
        node = stack.pop()


        if node.visited:
            continue

        node.visited = True

        if isinstance(node, SpecialNode):
            if node.node_type == NodeType.STAR:
                for leaf in node.leaves:
                    for parent in node.inner_tree:
                        stack.append(parent)

                        connection = connect_to(leaf, parent)
                        connections.add(connection)

                    for child in node.children:
                        stack.append(child)

                        connection = connect_to(leaf, child)
                        connections.add(connection)
            else:
                operator = OPERATORS[node.node_type]
                connection_string = f"subgraph {operator}" + "\n"
                connection_string += visualize_policies(node.inner_tree, start="\n")
                connection_string += "\nend\n"
                for leaf in node.leaves:
                    for child in node.children:
                        stack.append(child)

                        connection = connect_to(leaf, child)
                        connections.add(connection)
                connections.add(connection_string)

        else:
            args = args = "<div class=args>" + "<br/>".join(node.args) + "</div>"
            content += f"A{node.id_num}[\"{node.content} {args}\"]\n"
            for child in node.children:

                stack.append(child)

                if isinstance(child, SpecialNode):
                    if child.node_type == NodeType.STAR:
                        for sub_child in child.children:

                            connection = connect_to(node, sub_child)
                            connections.add(connection)

                    for sub_child in child.inner_tree:

                        connection = connect_to(node, sub_child)
                        connections.add(connection)

                else:
                    connection = connect_to(node, child)
                    connections.add(connection)


    return content + '\n'.join(connections)

def connect_to(node, child_node):
    """
        Connects one node to another.

        :param node: The parent Node or SpecialNode Object
        :param node: The child Node or SpecialNode Object
        :returns String representing node connections
    """
    output = ""
    if isinstance(node, SpecialNode):
        tree = node.leaves
    else:
        tree = [node]
    
    if isinstance(child_node, SpecialNode):
        bottom_tree = child_node.inner_tree
    else:
        bottom_tree = [child_node]
    
    for node in tree:
        for child in bottom_tree:
            if isinstance(child, SpecialNode) or isinstance(node, SpecialNode):
                output += connect_to(node, child)
            else:
                output += f"A{node.id_num} --> A{child.id_num}" + "\n"
    
    return output
        

def parse_policy(policy):
    """
        Parses the policy using the parser in ancile_core and returns
        a JSON with either an error status and a traceback, or a mermaid-ready
        graph representation.

        :param policy: Policy string
        :returns Dictionary with status and parsed_policy (or traceback)
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
        :returns List of ParamCell string representations.
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
