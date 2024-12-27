class Node():
	def __init__(self, n, f, d):
		self.nb = n
		self.father = f
		self.depth = d
		self.children = []
		
	def __repr__(self):
		return "\n\n--- Node ---" +\
			"\nnb: " + str(self.nb) +\
			"\nfather: " + str(self.father) +\
			"\ndepth: " + str(self.depth)

def export(root_node, path):
	path="1"
