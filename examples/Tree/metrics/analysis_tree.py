import numpy as np
import sys

class Node():
	def __init__(self, n, f, d):
		self.nb = n
		self.father = f
		self.depth = d
		self.children = []
		self.is_terminal = None
		self.height = None
		self.size = None

	def __repr__(self):
		return "\n\n--- Node ---" +\
				 "\nnb: " + str(self.nb) +\
				 "\nfather: " + str(self.father) +\
				 "\ndepth: " + str(self.depth) +\
				 "\nchildren: " + str(self.children) +\
				 "\nis_terminal: " + str(self.is_terminal) +\
			     "\nheight: " + str(self.height) +\
				 "\nsize: " + str(self.size)

def print_nodes():
	for n in node:
		print(n)

def read_csv():
	with open(sys.argv[1] + "tree.csv", "r") as f:
		cptL= 0
		for line in f:
			cptL+=1
			tmp = line.split(";")
			tmp[-1] = tmp[-1][:-1] #enlève le \n
			n = Node(int(tmp[0]), int(tmp[1]), int(tmp[2]))
			for c in tmp[3:]:
				n.children.append(int(c))
			node.append(n)

def complete_node_attributes():
	for n in node:
		if n.children == []:
			n.is_terminal = True
			n.height = 0
			n.size = 1
		else:
			n.is_terminal = False
	complete_size_height(0)

def complete_size_height(n):
	s = 1
	h = 0
	for c in node[n].children:
		if node[c].height == None:
			complete_size_height(c)
		s += node[c].size
		if h < node[c].height+1:
			h = node[c].height+1
		node[n].size = s
		node[n].height = h

def return_interval(param, name):
	if 0.0 <= param < 0.33:
		return "True;False;False"
	elif 0.33 <= param <= 0.67:
		return "False;True;False"
	elif 0.67 < param <= 1:
		return "False;False;True"
	else:
		print(name + ": " + str(param))
		exit()

def analyse_size():
	return return_interval((len(node)-1)/((2**int(sys.argv[2])-1)), "size")

def analyse_height():
	return return_interval((node[0].height)/(int(sys.argv[2])-1), "height")

def analyse_height_vs_size():
	if node[0].size < 4:
		return "None;None;None"
	return return_interval((node[0].height-1)/(node[0].size-2), "height_vs_size")

def analyse_leafb():
	if node[0].height <= 2 or node[0].height >= node[0].size-1:
		return "None;None;None"
	
	nb_leaves = 0
	nb_leafb = 0
	
	for n in node:
		if n.is_terminal is True:
			nb_leaves += 1
			if n.depth == node[0].height or n.depth == node[0].height-1:
				nb_leafb += 1
	return return_interval((nb_leafb-1)/(nb_leaves-1), "leafb")

def analyse_heightb():
	if node[0].height < 2:
		return "None;None;None"
	nb_internal_node = 0
	nb_internal_node_with_heightb_subtree = 0
	
	for n in node:
		if n.is_terminal is False:
			nb_internal_node += 1
			first_child_height = node[n.children[0]].height
			if len(n.children) == 1:
				if first_child_height == 0:
					nb_internal_node_with_heightb_subtree += 1
			else:
				flag = True
				for c in n.children[1:]:
					if not first_child_height-1 <= node[c].height <= first_child_height+1:
						flag = False
				if flag:
					nb_internal_node_with_heightb_subtree += 1
	return return_interval((nb_internal_node_with_heightb_subtree-1)/(nb_internal_node-1), "heightb")

def analyse_sizeb():
	if node[0].height < 2:
		return "None;None;None"
	
	nb_internal_node = 0
	nb_internal_node_with_sizeb_subtree = 0

	for n in node:
		if n.is_terminal is False:
			nb_internal_node += 1
			
			first_child_size = node[n.children[0]].size
			if len(n.children) == 1:
				if first_child_size == 1:
					nb_internal_node_with_sizeb_subtree += 1
			else:
				flag = True
				for c in n.children[1:]:
					if not first_child_size-1 <= node[c].size <= first_child_size+1:
						flag = False
				if flag:
					nb_internal_node_with_sizeb_subtree += 1
	return return_interval((nb_internal_node_with_sizeb_subtree-1)/(nb_internal_node-1), "sizeb")

node = []
read_csv()
complete_node_attributes()

with open("treeh"+ sys.argv[2] + "/analysis.csv", "a") as f:
	f.write(analyse_size() + "/" + analyse_height() + "/" + analyse_height_vs_size() + "/" + analyse_leafb() + "/" + analyse_heightb() + "/" + analyse_sizeb() + "\n")


