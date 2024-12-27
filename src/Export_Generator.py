'''
Copyright or © or Copr.

This software is a computer program whose purpose is to generate random
test case from a template file describing the data model.

This software is governed by the CeCILL-B license under French law and
abiding by the rules of distribution of free software.  You can  use,
modify and/ or redistribute the software under the terms of the CeCILL-B
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info".

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and,  more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL-B license and that you accept its terms.
'''

###############################################################################
# --- Export_Generator module ----------------------------------------------- #
###############################################################################
import os
import Miscellaneous as misc


def create_minimal_export():
	if not misc.check_file("Export.py", True):
		with open("./Export.py", "w") as f:
			f.write("def export(root_node, path):\n\tpass")


def create_export(root_node):
	if os.path.getsize("./Export.py") == 22:
		with open("./Export.py", "w") as f:
			f.write("def export(root_node, path):\n")
			f.write("\t\"\"\"\n\tEntry point for the export function\n")
			f.write("\tThe default calls go to the root node. It can be changed below\n\t\"\"\"\n")
		create_export_calls(root_node, root_node.name)
		with open("./Export.py", "a") as f:
			f.write("\n\n")
		
		create_node_export(root_node)
		return True
	else:
		return False


def create_export_calls(node, tree_path):
	with open("./Export.py", "a") as f:
		if not "[" in tree_path:
			f.write("\texport_" + node.name + "(root_node)\n")
		else:
			f.write("\t#export_" + node.name + "(root_node.get_element_from_current_node(\"" + tree_path + "\"))\n")
	for child in node.children:
		tree_path += "[0]\\" + child
		create_export_calls(node.get_element_from_current_node(node.name + "[0]\\" + child), tree_path)


def create_node_export(node):
	with open("./Export.py", "a") as f:
		f.write("def export_" + node.name + "(node, arg=None):\n")
		f.write("\t\"\"\"\n\tExport function of \"" + node.name + "\" node (nb instances= " + str(node.nb_instances) + ")\n")
		f.write("\tEvery child nodes are accessible from the current node -> child_node = node.get_child_n(child_node_name, node_instance_index)\n")
		f.write("\tNote that parameters are store in arrays               -> parameter[index]\n")
		f.write("\tEvery node/parameter can be accessed using tree path   -> current_node.get_element_from_current_node(\"..\\node_name[index]\")\n\t\"\"\"\n\n")

		nb_instances = node.nb_instances
		if nb_instances == 0:
			f.write("\tpass #there is no instances of this node\n\n")
			return
		elif nb_instances is None:
			f.write("\ti = 0\t#range of i -> [0, node.nb_instances - 1]\n\n")
		else:
			f.write("\ti = 0\t#range of i -> [0, " + str(nb_instances - 1) + "]\n\n")

		f.write("\t#\"" + node.name + "\" child node(s):\n")
		for child in node.children:
			f.write("\t" + child + " = " + "node.get_child_n(\"" + child + "\", i)\n")
		if len(node.children) == 0:
			f.write("\t#None\n")

		f.write("\n")

		f.write("\t#\"" + node.name + "\" child parameter(s):\n")
		for parameter in node.parameters:
			f.write("\t" + parameter + " = " + "node.get_parameter_n(\"" + parameter + "\", i).values\n")
		if len(node.parameters) == 0:
			f.write("\t#None\n")

		f.write("\n\t####################################\n")
		f.write("\t#          YOUR CODE HERE          #\n")
		f.write("\t####################################\n")
		f.write("\n\n")

	for child in node.children:
		create_node_export(node.get_child_n(child))
