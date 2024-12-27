from graphviz import Source
from graphviz import Digraph

class Node():
    def __init__(self, id, p, k, c):
        self.id = id
        self.parent = p
        self.key = k
        self.color = c
        self.depth = 0 
        self.children = []
        
    def __repr__(self):
        return f"\n\nkey: {self.key}\ncolor: {self.color}\nid: {self.id}\nparent: {self.parent}\ndepth: {self.depth}\nchildren: {self.children}"

def generate_node_list(node_xml, nodes, parent):
    if node_xml is not None:
        key = node_xml.get_parameter_n("key").values[0]
        if key is not None:
            color = False
            new_node = Node(len(nodes), parent, key, color)
            nodes.append(new_node)
            if parent is not None:
                parent.children.append(new_node)
            left_son = node_xml.get_child_n("leftSon")
            right_son = node_xml.get_child_n("rightSon")
            generate_node_list(left_son, nodes, new_node)
            generate_node_list(right_son, nodes, new_node)

def set_depth(node, depth):
    node.depth = depth
    for child in node.children:
        set_depth(child, depth + 1)

def export(root_node, path):
	nodes = []
	node_xml = root_node.get_child_n("typeNode")
	generate_node_list(node_xml, nodes, None)
	set_depth(nodes[0], 0)

	with open(path + "tree.csv", "w") as f:
		for n in nodes:
			children_ids = ";".join(str(child.id) for child in n.children)
			if children_ids:
				f.write(f"{n.id};{n.parent.id if n.parent else -1};{n.depth};{children_ids}\n")
			else:
				f.write(f"{n.id};{n.parent.id if n.parent else -1};{n.depth}\n")

	graph = Digraph(comment='Arbre')
	for n in nodes:
		graph.node(str(n.id), str(n.key), color='red' if n.color else 'black')

	for n in nodes:
		if n.parent is not None:
			graph.edge(str(n.parent.id), str(n.id))

	graph.render(path + 'tree', format='png')