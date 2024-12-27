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

import Miscellaneous as misc
#from Taf import SETTINGS

from Element import Element

###############################################################################
# --- Container ------------------------------------------------------------- #
###############################################################################
class Container():
	"""
	A Container object holds a dictionary of Node, Parameter and Constraint.
	It is used to build a tree structure and organise the parameters
	"""
	def __init__(self):
		self.__children = {} #[]
		self.__parameters = {}

	def add_child(self, new_child):
		"""
		:param new_child: Node object
		"""
		self.__children[new_child.name] = new_child
		#self.__children.append(new_child)

	def add_parameter(self, new_parameter):
		"""
		:param new_parameter: Parameter object
		"""
		self.__parameters[new_parameter.name] = new_parameter

	def get_child_n(self, n):
		"""
		:param n: the name (string) of the child
		:return: the corresponding child
		"""
		if n in self.get_children():
			return self.__children[n]
		else:
			return None

	def get_parameter_n(self, n):
		"""
		:param n	: the name (string) of the parameter
		:return	: the corresponding parameter
		"""
		if n in self.get_parameters():
			return self.__parameters[n]
		else:
			return None

	def get_children(self):
		"""
		:return: an array filled with the children names
		"""
		return self.__build_name_array(self.__children)
	children = property(get_children)

	def get_parameters(self):
		"""
		:return: an array filled with the parameters names
		"""
		return self.__build_name_array(self.__parameters)
	parameters = property(get_parameters)

	def __build_name_array(self, elements):
		element_name_array  = []
		#for element in elements:
		for n in elements.keys():
			#if elements[n].nb_instances != 0 or elements[n].nb_instances is None:
			element_name_array.append(n)
			#element_name_array.append(element)
		return element_name_array

	def build(self):
		for child in self.__children.values():
			child.build()

	def get_all_constraints(self):
		constraints = []
		for child in self.__children.values():
			for constraint in child.get_all_constraints():
				constraints.append(constraint)
		return constraints

	def build_constraints(self):
		for child in self.__children.values():
			child.build_constraints()

	def duplicate(self):
		container = Container()

		for parameter in self.__parameters.values():
			container.add_parameter(parameter.duplicate())

		for child in self.__children.values():
			container.add_child(child.duplicate())

		return container

	def print_structure(self, tabs):
		parameters_string = misc.color("parameters: ", "blue")

		if self.__parameters:
			for parameter in self.__parameters.values():
				if parameter.nb_instances > 0:
					parameters_string += parameter.name + " (" + str(parameter.values) + "), "
				else:
					parameters_string += misc.color(parameter.name + " ([]), ", "red")

			parameters_string = parameters_string[:-2]
			print (tabs + parameters_string)

		for child in self.__children.values():
			child.print_structure(tabs)


	def __repr__(self):
		s = "\tchildren    : " + str(self.get_children()) + "\n"
		s += "\tparameters  : " + str(self.get_parameters()) + "\n"
		return s


###############################################################################
# --- Node ------------------------------------------------------------------ #
###############################################################################
class Node(Element):
	def __init__(self, n, d, p, c, nb):
		"""
		:param n	: name
		:param d	: depth
		:param p	: parent
		:param c	: model container
		:param nb	: nb_instances
		:param attribs : xml_attribs
		"""
		Element.__init__(self, n, d)

		if nb.values[0] is not None:
			self.__check_nb_instances(nb.values[0])
		self.__nb_instances = nb
		self.__constraints = {}
		self.__parent = p
		self.__is_done = False
		#self.__attribs = attribs #or {}

		self.__containers = []
		if c is None:
			self.__containers.append(Container())
		else:
			self.__containers.append(c)

	def __check_nb_instances(self, nb):
		from Taf import SETTINGS
		if not 0 <= nb <= SETTINGS.get("node_max_nb_instances"):
			misc.error("Node::__check_nb_instances() -> " + self._name + ": nb_instances is out of range [0;" + str(SETTINGS.get("node_max_nb_instances")) + "]")

	def lock_nb_instances(self):
		self.__nb_instances.lock_i(0)

	def unlock_nb_instances(self):
		self.__nb_instances.unlock_i(0)

	def change_nb_instances(self, val):
		self.__nb_instances.set_value_i(0, val)
		self.__check_nb_instances(self.__nb_instances.values[0])

		while len(self.__containers) > self.__nb_instances.values[0] and len(self.__containers) > 1:
			self.__containers.pop()
		while len(self.__containers) < self.__nb_instances.values[0]:
			self.__containers.append(self.__containers[0].duplicate())

	def reduce_nb_instances_interval(self, m):
		self.__nb_instances.reduce_interval(m)

	def local_reset(self):
		self.change_nb_instances(self.__nb_instances.m)
		self.undo()
		self.__nb_instances.reset_all()

	def add_child(self, new_child):
		"""
		:param new_child: node object
		Add a new child node to the the current node
		"""
		self.__containers[0].add_child(new_child)

	def add_parameter(self, new_parameter):
		"""
		:param new_parameter: Parameter object
		Add a new parameter to the current node
		"""
		self.__containers[0].add_parameter(new_parameter)

	def add_constraint(self, new_constraint):
		"""
		:param new_constraint: Constraint object
		Add a new constraint to the current node
		"""
		self.__constraints[new_constraint.name] = new_constraint

	def __check_nb_instances_range(self, i):
		if i < len(self.__containers):
			return True
		else:
			return False

	def get_element_from_current_node(self, tp):
		if tp[-1] == "\\":
			tp = tp[:-1]

		if "\\" in tp:
			index = tp.find("\\")
			head = tp[0:index]
			tail = tp[(index + 1):]
			name, index = self.__extract_head_data(head)

			sub_tail = ""
			if "\\" in tail:
				sub_index = tail.find("\\")
				sub_head = tail[0:sub_index]
				sub_tail = tail[(sub_index + 1):]

				sub_name, sub_index = self.__extract_head_data(sub_head)
			else:
				sub_name, sub_index = self.__extract_head_data(tail)

			if name in [self._name, "."]:
				if sub_name == ".":
					return self.get_element_from_current_node(tail)
				elif sub_name == "..":
					return self.get_element_from_current_node(tail)
				if sub_name in self.children:
					c = self.get_child_n(sub_name, index)
					if c is not None:
						return c.get_element_from_current_node(tail)
					else:
						return None
				elif sub_name in self.parameters:
					return self.get_parameter_n(sub_name, index)
				elif sub_name in self.constraints:
					return self.get_constraint_n(sub_name)
				else:
					return None
			elif name == "..":
				return self.__get_element_from_parent(".\\" + tail)
		else:
			name, index = self.__extract_head_data(tp)
			if name == "..":
				if self.__parent is not None:
					return self.__parent
				else:
					misc.error("Node::get_element_from_current_node() -> \"" + self._name + "\" has no parent node")
					raise ValueError
			elif name in [".", self._name]:
				return self
			else:
				return None
				#misc.error("Node::get_element_from_current_node() -> \"" + name + "\" non coherent tree path")
				#raise ValueError

	def __get_element_from_parent(self, tp):
		if self.__parent is not None:
			return self.__parent.get_element_from_current_node(tp)
		else:
			misc.error("Node::get_element_from_parent() -> \"" + self._name + "\" has no parent node")
			raise ValueError

	def __extract_head_data(self, head):
		if "[" in head:
			if head[-1] != "]":
				misc.error("Tree::extract_head_data() -> \"" + head + "\" missing \"]\"")
			split_index = head.find("[")
			name = head[0:split_index]
			string_index = head[(split_index+1):-1]
			if misc.check_number(string_index, True):
				return name, int(string_index)
		else:
			return head, 0

	def get_children(self):
		return self.__containers[0].children
	children = property(get_children)

	def get_child_n(self, n, i=0):
		if self.__check_nb_instances_range(i):
			return self.__containers[i].get_child_n(n)
		else:
			return None

	def get_parameters(self):
		return self.__containers[0].parameters
	parameters = property(get_parameters)

	def get_parameter_n(self, n, i=0):
		if self.__check_nb_instances_range(i):
			return self.__containers[i].get_parameter_n(n)
		else:
			return None

	def get_constraints(self):
		return self.__constraints.keys()
	constraints = property(get_constraints)

	def get_constraint_n(self, n):
		if n in self.__constraints:
			return self.__constraints[n]
		else:
			misc.error("Node::get_constraint_n() -> constraint name does not exist \"" + n + "\"")

	def get_all_constraints(self):
		constraints = []
		for constraint in self.__constraints.values():
			constraints.append(constraint)
		for container in self.__containers:
			for constraint in container.get_all_constraints():
				constraints.append(constraint)
		return constraints

	def build(self):
		if self.__nb_instances.values[0] is not None:
			while len(self.__containers) < self.__nb_instances.values[0]:
				self.__containers.append(self.__containers[0].duplicate())
		else:
			while len(self.__containers) < self.__nb_instances.m:
				self.__containers.append(self.__containers[0].duplicate())
		for container in self.__containers:
			container.build()

	def duplicate(self):
		nb = self.__nb_instances.duplicate()
		if self.__nb_instances.values[0] is not None:
			nb.set_value_i(0, self.__nb_instances.values[0])
			if self.__nb_instances.locks[0]:
				nb.lock_i(0)
		n = Node(self._name, self._depth, self.__parent, self.__containers[0].duplicate(), nb)
		for constraint in self.__constraints.values():
			c = constraint.duplicate()
			c.set_parent(n)
			n.add_constraint(c)
		return n

	def build_constraints(self):
		for c in self.__constraints.values():
			c.build_constraint()
		for container in self.__containers:
			container.build_constraints()

	def do(self):
		self.__is_done = True

	def undo(self):
		self.__is_done = False

	def get_is_done(self):
		return self.__is_done
	is_done = property(get_is_done)

	def get_container_i(self, i):
		return self.__containers[i]

	def get_nb_instances(self):
		return self.__nb_instances.values[0]
	nb_instances = property(get_nb_instances)

	def get_nb_containers(self):
		return len(self.__containers)
	nb_containers = property(get_nb_containers)

	def get_nb_instances_parameter(self):
		return self.__nb_instances

	def get_type(self):
		return "node"

	def get_parent(self):
		return self.__parent

	#def get_attribs(self):
	#	return " ".join([f'{cle}="{valeur}"' for cle, valeur in self.__attribs.items()])

	def get_nb_instances_lock(self):
		return self.__nb_instances.locks[0]
	nb_instances_lock = property(get_nb_instances_lock)

	def __build_constraints_string(self):
		constraints_string = ""
		for constraint in self.__constraints.keys():
			constraints_string += constraint + ", " 
		if not constraints_string:
			constraints_string = "None"
		else:
			constraints_string = constraints_string[:-2]
		return constraints_string

	def get_empty_stat_array(self, current_path):
		empty_stat_array = [[current_path + " (nb_instances)"]]
		for i in range(self.get_nb_instances_parameter().M):
			indexed_path = current_path + "[" + str(i) + "]" + "\\"
			for p in self.get_parameters():
				empty_stat_array.append([indexed_path + p + " (nb_instances)"])
				for j in range(self.get_parameter_n(p).nb_instances):
					empty_stat_array.append([indexed_path + p + ".values[" + str(j) + "]"])
			for c in self.get_children():
				empty_stat_array = empty_stat_array + self.get_child_n(c).get_empty_stat_array(indexed_path + c)
		return empty_stat_array

	def get_stat_array(self):
		stat_array = [len(self.__containers)]
		for i in range(self.get_nb_instances_parameter().M):
			if i < len(self.__containers):
				for p in self.get_parameters():
					parameter = self.get_parameter_n(p, i)
					stat_array.append(parameter.nb_instances)
					stat_array = stat_array + parameter.values
				for c in self.get_children():
					stat_array = stat_array + self.get_child_n(c, i).get_stat_array()
			else:
				for p in self.get_parameters():
					stat_array.append(None)
					for j in range(self.get_parameter_n(p).nb_instances):
						stat_array.append(None)
					for c in self.get_children():
						for j in range(len(self.get_child_n(c).get_empty_stat_array(""))):
							stat_array.append(None)
		return stat_array


	def print_structure(self, tabs=""):
		if self.__nb_instances.values[0] is None or self.__nb_instances.values[0] > 0:
			print (tabs + misc.color("--- " + self._name + " ---", "cyan") +\
				  " (nb_instances: " + str(self.__nb_instances.values[0]) +\
				  " / depth: " + str(self._depth) +\
				  " / constraints: " + self.__build_constraints_string() + ")")
			for index, container in enumerate(self.__containers):
				print (tabs + misc.color("\t#" + str(index), "magenta"))
				container.print_structure(tabs + "\t")

		else:
			print (tabs + misc.color("--- " + self._name + " ---" + " (nb_instances: 0 / depth: " + str(self._depth) +\
									 " / constraints: " + self.__build_constraints_string() + ")", "green"))

	def __repr__(self):
		return misc.color("--- " + self._name + " ---", "yellow") +\
			   " (nb_instances: " + str(self.__nb_instances.values[0]) +\
			   " / depth: " + str(self._depth) +\
			   " / constraints: " + self.__build_constraints_string() + ")\n" +\
			   repr(self.__containers[0])
