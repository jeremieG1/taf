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

import numpy as np

from Export_Generator import create_export
from Export import export
from Generator import Generator
import Xml as xml
import Miscellaneous as misc

###############################################################################
# --- Tree ------------------------------------------------------------------ #
###############################################################################
class Tree():
	def __init__(self, path):
		self.__seed = None
		self.__root = None
		self.__current_node = None
		self.__is_parsed = False
		self.init_tree(path)

	def __set_seed(self, s):
		if s == "r":
			s = ""
			alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
			for i in range(10):
				s += alphabet[np.random.randint(len(alphabet))]
		
		self.__seed = (str(s), misc.adler32(s))

	def init_tree(self, path):
		try:
			self.__root = xml.read_template(path)
		except(ValueError, NameError):
			print("Unable to parse: " + misc.color(path, "cyan"))
			return
		self.__root.build()
		self.build_constraints()
		self.__current_node = self.__root
		self.__is_parsed = True

	def generate(self, verbose):
		if self.__seed is None:
			self.__set_seed("r")
		np.random.seed(self.__seed[1])
		g = Generator(self, verbose)
		# self.print_current_node()
		# self.__current_node.print_structure()
		return g.generate()

	def generate_export_functions(self):
		create_export(self.__root)

	def export(self, path):
		export(self.__root, path)

	def build_constraints(self):
		self.__root.build_constraints()

	def print_current_node(self):
		if self.__current_node.get_parent() is None and self.__seed is not None:
			print(misc.color("seed:", "yellow") + " " + self.__seed[0])
		self.__current_node.print_structure()

	def write_test_case(self, path):
		xml.write_test_case(self.__root, self.__seed[0], path)

	def read_test_case(self, path):
		seed = xml.read_test_case(path, self.__root)
		self.__set_seed(seed)

	def get_element_from_current_node(self, tp):
		try:
			return self.__current_node.get_element_from_current_node(tp)
		except ValueError:
			misc.error("Tree::get_element_from_current_node() -> \"" + tp + "\" is not well formed or does not match your structure")


	def get_depth_elements(self, desired_depth, node=None, current_depth=0):
		parameters = []
		nodes = []

		if node is None:
			node = self.__root

		if desired_depth == current_depth:
			for i in range(node.nb_instances):
				for n in node.get_container_i(i).parameters:
					parameters.append(node.get_parameter_n(n, i))
				for n in node.get_container_i(i).children:
					nodes.append(node.get_child_n(n, i))
		else:
			for i in range(node.nb_instances):
				for n in node.get_container_i(i).children:
					sub_n, sub_p = self.get_depth_elements(desired_depth, node.get_child_n(n, i), current_depth+1)
					nodes += sub_n
					parameters += sub_p

		return nodes, parameters

	def get_empty_stat_array(self):
		return self.__root.get_empty_stat_array(self.__root.name)

	def get_stat_array(self):
		return self.__root.get_stat_array()

	def get_all_constraints(self):
		return self.__root.get_all_constraints()

	def change_current_node(self, tp):
		try:
			self.__current_node = self.__current_node.get_element_from_current_node(tp)
		except ValueError:
			misc.error("Tree::change_current_node() -> \"" + tp + "\" is not well formed or does not match your structure")

	def print_constraints(self):
		for c in self.__root.constraints:
			print(self.__root.get_constraint_n(c))

	def get_current_node(self):
		return self.__current_node

	def get_is_parsed(self):
		return self.__is_parsed
	is_parsed = property(get_is_parsed)




