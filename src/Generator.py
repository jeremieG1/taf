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

import z3 as z3
import Miscellaneous as misc
import numpy as np
#from Taf import SETTINGS

###############################################################################
# --- Generator ------------------------------------------------------------- #
###############################################################################
class Generator:
	"""
	The Generator class ...
	"""

	def __init__(self, t, v):
		"""
		:param t: tree
		"""
		self.__tree = t
		self.__constraints = [[]]
		self.__set_constraints()
		self.__verbose = v

	def __set_constraints(self):
		constraints = self.__tree.get_all_constraints()
		
		for constraint in constraints:
			depth = constraint.var_depth
			while len(self.__constraints) <= depth:
				self.__constraints.append([])
			self.__constraints[depth].append(constraint)

	def generate(self):
		from Taf import SETTINGS
		depth = 0
		counter = 0
		nodes, parameters = self.__tree.get_depth_elements(depth)
		#debug
		# for i in range(10):
		# 	print("*************************************************" + str(i))
		# 	nodes, parameters = self.__tree.get_depth_elements(i)
		# 	for node in nodes:
		# 		print("node -> " + node.name)
		# 		node.change_nb_instances(1)
		# 	for parameter in parameters:
		# 		print("parameter -> " + parameter.name)

		# for i, constraint in enumerate(self.__constraints):
		# 	print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$" + str(i))
		# 	for c in constraint:
		# 		print(c.raw_expressions)
		
		
		# print("on print avant generator - tout est ok")
		# self.__tree.print_current_node()
		while True:
			if counter == int(SETTINGS.get("max_backtracking")):
				print("--> false")
				return False
			if not(parameters or nodes):
				return True
			if len(self.__constraints) > depth:
				constraints = self.__constraints[depth]
			else:
				constraints = []
			if self.__generate_depth(nodes, parameters, constraints):
				depth += 1
			elif depth > 0:
				counter += 1
				depth -= 1
				self.__reset_depth(nodes, parameters)
			else:
				misc.error("Generator::generate() -> unable to generate the current template")
				return False	
			self.__tree.build_constraints()
			nodes, parameters = self.__tree.get_depth_elements(depth)
			self.__constraints = [[]]
			self.__set_constraints()

	def __reset_depth(self, nodes, parameters):
		for node in nodes:
			node.local_reset()
		for parameter in parameters:
			parameter.reset_all()

	def __generate_depth(self, nodes, parameters, constraints):
		if constraints and not self.__partial_solver(constraints):
			print("Constraints not satisfied.")
			self.__tree.print_current_node()
			return False

		for node in nodes:
			if not node.nb_instances_lock and not node.is_done:
				node.change_nb_instances("r")
				node.do()

		for parameter in parameters:
			for i, v in enumerate(parameter.values):
				if v is None:
					parameter.set_value_i(i, "r")

		return True


	def __partial_solver(self, constraints):
		from Taf import SETTINGS
		s = SMT_Interface()
		variables = {}

		cpt = 0
		for constraint in constraints:
			# print("\ngenerator constraint")
			# print(constraint)
			cpt += 1
			constraint.process()
			self.__add_variables_to_solver(s, constraint)
			self.__add_constraint_to_solver(s, constraint)
			variables.update(constraint.variables)
			# print(f"nb contraintes : {len(constraint.variables)}")			
		# print(f"\nnb variables totales : {len(variables)}")
		
		if not s.check():
			print("\tnot check")
			return False

		# print("début de partial solver, tout est ok")
		# self.__tree.print_current_node()

		max_additional_constraints = []
		for i in range(int(SETTINGS.get("max_diversity"))):
			s.push()
			additional_constraints = self.__add_randomness(s, variables, i)
			if len(additional_constraints) > len(max_additional_constraints):
				max_additional_constraints = additional_constraints
			s.pop()
			if len(max_additional_constraints) == len(variables):
				break

		if self.__verbose:
			print(misc.get_separator())
			print("additional contraint(s): ")
			print(max_additional_constraints)
			print(misc.get_separator())
		
		for constraint in max_additional_constraints:
			s.add_constraint(constraint)
		self.__assign_solver_results(s, variables)

		# print("fin de partial solver")
		# self.__tree.print_current_node()
		return True

	def __add_variables_to_solver(self, s, constraint):
		variables = constraint.variables

		for name in variables.keys():
			variable = variables[name]
			variable_type = variable.get_type()

			if variable_type == "node":
				if not variable.nb_instances_lock:
					range_undefined = s.add_int_variable(name)
					if range_undefined:
						nb_instances_parameter = variable.get_nb_instances_parameter()
						s.add_constraint(name + " >= " + str(nb_instances_parameter.m))
						s.add_constraint(name + " <= " + str(nb_instances_parameter.M))
			else:
				if not variable.locks[int(name[name.rfind("_") + 1:])]:
					if variable_type == "boolean":
						s.add_bool_variable(name)
					elif variable_type == "string":
						range_undefined = s.add_int_variable(name)
						if range_undefined:
							s.add_constraint(name + " >= 0")
							s.add_constraint(name + " <= " + str(len(variable.values_array) - 1))
					else:
						if variable_type == "integer":
							range_undefined = s.add_int_variable(name)
						else:  # variable_type == "real"
							range_undefined = s.add_real_variable(name)
						if range_undefined:
							s.add_constraint(name + " >= " + str(variable.m))
							s.add_constraint(name + " <= " + str(variable.M))

	def __add_constraint_to_solver(self, s, constraint):
		expressions = constraint.expressions
		for expr in expressions:
			s.add_constraint(expr)

	def __add_randomness(self, s, variables, i):
		additional_constraints = []
		names = []
		for key in variables:
			names.append(key)
		np.random.shuffle(names)

		while len(names) > 0:
			name = names.pop()
			selected_variable = variables[name]
			if name[0] == "_": #nb_instances
				if selected_variable.get_type() == "node":
					tmp = selected_variable.get_nb_instances_parameter()
					tmp.set_value_i(0, "r")
					additional_constraints.append(name + " == " + str(tmp.values[0]))
					tmp.reset_i(0)
				else: #selected_variable.get_type() == "parameter"
					additional_constraints.append(name + " == " + str(np.random.randint(51))) #setting max_parameter_nb_instances!
			else:
				index = int(name[name.rfind("_") + 1:])
				selected_variable.set_value_i(index, "r")

				if selected_variable.get_type() == "string":
					v = selected_variable.values_array.index(selected_variable.values[index])
				else:
					v = selected_variable.values[index]
				
				additional_constraints.append(name + " == " + str(v))
				selected_variable.reset_i(index)

			s.add_constraint(additional_constraints[-1])
			if not s.check():
				return additional_constraints[:-1]
		
		return additional_constraints

	def __assign_solver_results(self, s ,variables):
		s.increase_timeout()
		s.check()
		s.set_timeout()
		results = s.get_results()

		for name in variables:
			if name[0] == "_":
				if variables[name].get_type() == "node":
					variables[name].change_nb_instances(results[name])
					variables[name].do()
				else: #variables[name].get_type() == "parameter"
					variables[name].change_nb_instances(results[name])
			else:
				if variables[name].get_type() == "string":
					variables[name].set_value_i(int(name[name.rfind("_") + 1:]), variables[name].values_array[eval(results[name])])
				else:
					if name in results.keys():
						variables[name].set_value_i(int(name[name.rfind("_") + 1:]), eval(results[name]))
					else:
						variables[name].set_value_i(int(name[name.rfind("_") + 1:]), "r")

	def __find_connected_component(self):
		for v in self.__variables:
			sub_group = self.__explore(v)
			if len(sub_group) > 0:
				self.__groups.append(sub_group)

		for i in range(len(self.__groups)):
			print("group " + str(i))
			print(self.__groups[i])

	def __explore(self, v):
		sub_group = []
		if not v.flag:
			sub_group.append(v)
			v.set_flag()
			for n in v.get_neighbors():
				sub_group += self.__explore(n)
		return sub_group

	def __debug(self):
		tmp = len(self.__constraints)
		print("len constraints: " + str(tmp))

		for i in range(tmp):
			print("depth: " + str(i))
			for c in self.__constraints[i]:
				print(c.name)


###############################################################################
# --- Var ------------------------------------------------------------------- #
###############################################################################
class Var():
	def __init__(self, n):
		self.__name = n
		self.__neighbors = []
		self.__flag = False

	def add_neighbor(self, v):
		self.__neighbors.append(v)

	def set_flag(self):
		self.__flag = True

	def get_name(self):
		return self.__name
	name = property(get_name)

	def get_neighbors(self):
		return self.__neighbors

	def get_flag(self):
		return self.__flag
	flag = property(get_flag)

	def __repr__(self):
		return self.__name


###############################################################################
# --- SMT_Interface --------------------------------------------------------- #
###############################################################################
class SMT_Interface:
	def __init__(self):
		self.__solver = z3.Solver()
		self.set_timeout()

		self.__variables = {}
		self.__constraints = {}
		self.__variables["z3"] = z3
	
	def increase_timeout(self):
		from Taf import SETTINGS
		self.__solver.set("timeout", 100*int(SETTINGS.get("z3_timeout")))
	
	def set_timeout(self):
		from Taf import SETTINGS
		self.__solver.set("timeout", int(SETTINGS.get("z3_timeout")))

	def add_int_variable(self, n):
		if n not in self.__variables:
			#print("add_int_variable -> " + n)
			self.__variables[n] = z3.Int(n)
			return True
		return False

	def add_real_variable(self, n):
		if n not in self.__variables:
			#print("add_real_variable -> " + n)
			self.__variables[n] = z3.Real(n)
			return True
		return False

	def add_bool_variable(self, n):
		if n not in self.__variables:
			#print("add_bool_variable -> " + n)
			self.__variables[n] = z3.Bool(n)
			return True
		return False

	def add_constraint(self, c):
		# print("add_constraint -> " + c)
		self.__solver.add(eval(c, self.__variables))

	def push(self):
		self.__solver.push()

	def pop(self):
		self.__solver.pop()

	def check(self):
		c = self.__solver.check()
		if c == z3.sat:
			return True
		elif c == z3.unknown:
			print("TIMEOUT!")
		return False

	def get_results(self):
		res = {}

		m = self.__solver.model()
		for d in m.decls():
			res[d.name()] = str(m[d])
		return res
