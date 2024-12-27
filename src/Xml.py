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
# --- Xml module ------------------------------------------------------------ #
###############################################################################
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import re
import random
import string
import Miscellaneous as misc
from Node import Node
from Parameter import Boolean_Parameter, String_Parameter, Integer_Parameter, Real_Parameter
from Constraint import Constraint
from XML_Syntax import *

def parse_xml(path):
	try:
		tree = ET.parse(path)
		return tree
	except ET.ParseError:
		misc.error("Xml::parse_xml() -> the template \"" + path + "\" does not respect xml format")
		return None


def read_template(path):
	xml = parse_xml(path)
	root_xml = xml.getroot()
	if root_xml is None:
		raise ValueError
	if root_xml.tag != "root":
		misc.error("Xml::read_xml() -> the template root tag must be \"root\"" + path + "\"")
		raise ValueError

	name = check_attribute(root_xml, "name", True)
	nb_instances = Integer_Parameter(name + "_nb_instances", -1, 1, 1, "u", None, None, None, None, 1, root_xml.attrib)
	nb_instances.set_value_i(0, 1)
	nb_instances.lock_i(0)
	root_node = Node(name, 0, None, None, nb_instances)
	read_node(root_xml, root_node,xml)
	return root_node


def read_node(node_xml, node, xml, d=0):
	max_depth_map = {}
	stack=[(node_xml, node, d)]
	while stack:
		current_node_xml, current_node, depth = stack.pop()
		for child in current_node_xml:
			name = check_attribute(child, "name", False)
			if child.tag  == TAF_PARAMETER:
				parameter=build_parameter(name, depth, child)
				current_node.add_parameter(parameter)
			
			elif child.tag  == TAF_CONSTRAINT:
				constraint=build_constraint(name, depth, current_node, child,xml)
				add_constraint_to_node(constraint,name, depth, current_node, child)
			
			elif child.tag == TAF_TYPE:
				child.attrib[TAF_NODE_NB_INSTANCES] = 0
				if not current_node.get_child_n(name):
					child_node = build_node(name, depth+1 , current_node, child)
					current_node.add_child(child_node)
				stack.append((child, current_node.get_child_n(name), depth + 1))
				
			elif child.tag == TAF_NODE:
				#check xml attribute ref and type
				ref = check_attribute(child, TAF_REFERENCED_NODE, False)
				ref_type = check_attribute(child, TAF_TYPE, False)

				#reference
				if(ref is not None):
					elem = find_refered_node(xml,node,ref,TAF_REFERENCE)
					#child.attrib[TAF_IDENTIFIER] = elem.attrib[TAF_IDENTIFIER]
					
					name = child.attrib[TAF_IDENTIFIER]
					
					#Treat depth and branching parameters and init max_depth
					max_depth = build_reference(child)

					#Stop condition
					if depth <= max_depth:
					#read and build reference as a node
						if not current_node.get_child_n(name):
							child_node=build_node(name, depth+1, current_node, child)
							current_node.add_child(child_node)
						stack.append((child, child_node, depth + 1))
					stack.append((elem, current_node.get_child_n(name), depth +1))
				
				
				
				elif(ref_type is not None):
					elem = find_refered_node(xml,node,ref_type,TAF_TYPE)
					elem_type = check_attribute(elem, TAF_TYPE, False)


					while elem_type is not None :					
						elem = find_refered_node(xml,node,elem_type,TAF_TYPE)
						if elem is None : 
							break
						elem_type = check_attribute(elem, TAF_TYPE, False)

					#child.attrib[TAF_IDENTIFIER] = elem.attrib[TAF_IDENTIFIER]
					name = child.attrib[TAF_IDENTIFIER]
					#Treat depth and branching parameters and init max_depth
					max_depth = build_reference(child)
					#Stop condition
					if depth <= max_depth:
						if not current_node.get_child_n(name):
							child_node=build_node(name, depth+1, current_node, child)
							current_node.add_child(child_node)
						stack.append((child, child_node, depth + 1))
					if current_node.get_child_n(name) is not None:
						stack.append((elem, current_node.get_child_n(name), depth +1))

				else:
						if not current_node.get_child_n(name):
							child_node = build_node(name, depth+1 , current_node, child)
							current_node.add_child(child_node)
						stack.append((child, current_node.get_child_n(name), depth + 1))

			else:
				misc.error("Xml::read_node() -> \"" + child.tag + "\" unknown xml TAF tag")
				raise NameError	

# find and return the refered node in a reference (take into account references pointing on references)
def find_refered_node(xml, node, refered, tag):
	for elem in xml.getroot().iter():
		refered_node = check_attribute(elem, TAF_IDENTIFIER, False)
		if refered_node == refered:
			if elem.tag == TAF_NODE or elem.tag == TAF_TYPE:
				return elem
			else:
				return find_refered_node(xml, elem, check_attribute(elem, tag, True))


# pre_build a reference node and return depth asked (from template attributes)
def build_reference(child):
	# Get depth attributes from template
	depth_attrib = check_attribute(child,TAF_REFERENCE_DEPTH)
	max_depth_attrib = check_attribute(child,TAF_REFERENCE_MAX_DEPTH)
	# Get branching attributes from template
	branching_attrib = check_attribute(child,TAF_REFERENCE_BRANCHING)
	max_branching_attrib = check_attribute(child,TAF_REFERENCE_MAX_BRANCHING)

	if depth_attrib is None and max_depth_attrib is None:
	#depth=0 by default	
		depth_asked = 1
		#Treat branching
		if branching_attrib is not None:
			child.attrib[TAF_NODE_NB_INSTANCES] = int(branching_attrib)
		elif max_branching_attrib is not None:
			child.attrib[TAF_NODE_MIN] = "0"
			child.attrib[TAF_NODE_MAX] = int(max_branching_attrib)
		else:
			child.attrib[TAF_NODE_NB_INSTANCES] = 1
	
	
	elif branching_attrib is None and max_branching_attrib is None:
	#branching=1 by default
		child.attrib[TAF_NODE_NB_INSTANCES] = 1
		#Treat depth
		if depth_attrib is None and max_depth_attrib is None:
			depth_asked=1
		elif depth_attrib is not None:
			depth_asked = int(depth_attrib)
		elif max_depth_attrib is not None:
			depth_asked = int(max_depth_attrib)

	##ERRORS		
	elif depth_attrib is not None and max_depth_attrib is not None:
		misc.error("Xml::" + TAF_REFERENCE + " cannot have " + TAF_REFERENCE_DEPTH + " and "+ TAF_REFERENCE_MAX_DEPTH + " attributes alongside")
	elif branching_attrib is not None and max_branching_attrib is not None:
		misc.error("Xml::" + TAF_REFERENCE + " cannot have " + TAF_REFERENCE_BRANCHING + " and "+ TAF_REFERENCE_MAX_BRANCHING + " attributes alongside")
	elif branching_attrib is not None and max_depth_attrib is not None:
		misc.error("Xml::" + TAF_REFERENCE + " cannot have" + TAF_REFERENCE_BRANCHING + " and " + TAF_REFERENCE_MAX_DEPTH + " attributes alongside, please use " + TAF_REFERENCE_DEPTH + "attribute instead")
	elif depth_attrib is not None and max_branching_attrib is not None:
		misc.error("Xml::" + TAF_REFERENCE + " cannot have " + TAF_REFERENCE_MAX_BRANCHING + " and " + TAF_REFERENCE_DEPTH + " attributes alongside, please use " + TAF_REFERENCE_MAX_DEPTH + "attribute instead")
	
	#Treat branching
	elif branching_attrib is not None:
		child.attrib[TAF_NODE_NB_INSTANCES] = int(branching_attrib)
		#Treat depth
		if depth_attrib is not None:
			depth_asked = int(depth_attrib)
		else: 
			depth_asked = 1
	
	#Treat branching
	elif max_branching_attrib is not None:
		child.attrib[TAF_NODE_MIN] = "0"
		child.attrib[TAF_NODE_MAX] = int(max_branching_attrib)
		#Treat depth
		if max_depth_attrib is not None:
			depth_asked = int(max_depth_attrib)
		else: 
			depth_asked = 1
	
	return depth_asked

def build_node(n, d, p, node_xml):
	minimum = check_attribute(node_xml, TAF_NODE_MIN)
	maximum = check_attribute(node_xml, TAF_NODE_MAX)
	nb = check_attribute(node_xml, TAF_NODE_NB_INSTANCES)

	if nb is not None and check_nb_instances(nb):
		nb = int(nb)
		# Need to be fixed somehow else because it make recursion(reference) works uncorrectly  
		#if minimum is not None or maximum is not None:
		#	misc.error("Xml::build_node() -> \"" + n + "\" TAF_NODE_MIN  "+TAF_NODE_MIN +" and TAF_NODE_MAX  "+TAF_NODE_MAX +" should not be specified along with TAF_NODE_NB_INSTANCES "+ TAF_NODE_NB_INSTANCES +" attribute")
		#	raise ValueError
		node_xml.attrib[TAF_NODE_MIN] = nb
		node_xml.attrib[TAF_NODE_MAX] = nb
		nb_instances = build_integer_parameter(n + "_nb_instances", d-1, node_xml, 1)
		nb_instances.set_value_i(0, nb)
		nb_instances.lock_i(0)

	elif minimum is not None or maximum is not None:
		if minimum is None and maximum is not None:
			misc.error("Xml::build_node() -> \"" + n + "\" missing TAF_NODE_MIN "+ TAF_NODE_MIN +" attribute")
			raise ValueError
		elif maximum is None and minimum is not None:
			misc.error("Xml::build_node() -> \"" + n + "\" missing TAF_NODE_MAX "+ TAF_NODE_MAX +" attribute")
			raise ValueError
		nb_instances = build_integer_parameter(n + "_nb_instances", d-1, node_xml, 1)
		if nb_instances.m < 0:
			misc.error("Xml::build_node() -> \"" + n + "\" TAF_NODE_MIN "+ TAF_NODE_MIN +" and TAF_NODE_MAX "+ TAF_NODE_MAX +" attributes must be positive integers")
			raise ValueError

	else: 	#not nb_instances and not minimum and not maximum
		default = 1
		if node_xml.tag == TAF_TYPE:
			default = 0
		node_xml.attrib[TAF_NODE_MIN] = default
		node_xml.attrib[TAF_NODE_MAX] = default
		nb_instances = build_integer_parameter(n + "_nb_instances", d-1, node_xml, 1)
		nb_instances.set_value_i(0, default)
		nb_instances.lock_i(0)

	return Node(n, d, p, None, nb_instances)


def build_parameter(n, d, node_xml):
	parameter_type = check_attribute(node_xml, TAF_PARAMETER_TYPE, True)
	nbi = check_attribute(node_xml, TAF_NODE_NB_INSTANCES)
	to_lock = False
	if nbi and check_nb_instances(nbi):
		nbi = int(nbi)
		to_lock = True
	else:
		nbi = 1

	if parameter_type == "boolean":
		p = build_boolean_parameter(n, d, node_xml, nbi)
	elif parameter_type == "string":
		p = build_string_parameter(n, d, node_xml, nbi)
	elif parameter_type == "integer":
		p = build_integer_parameter(n, d, node_xml, nbi)
	elif parameter_type == "real":
		p = build_real_parameter(n, d, node_xml, nbi)
	else:
		misc.error("Xml::build_parameter() -> \"" + parameter_type + "\" unknown TAF_PARAMETER_TYPE "+ TAF_PARAMETER_TYPE +" type must be boolean, string, integer or real")
		raise NameError

	if to_lock:
		p.lock_nb_instances()
	return p


def build_categorical_parameter(node_xml):
	values = []
	tmp = check_attribute(node_xml, TAF_PARAMETER_VALUES, False)
	if tmp:
		tmp = tmp.split(";")
		for v in tmp:
			values.append(misc.remove_starting_and_ending_space(v))
	else:
		values = [True, False]
	return values, build_weights(check_attribute(node_xml, TAF_PARAMETER_WEIGHTS, False))


def build_weights(str_weights):
	weights = []
	if str_weights:
		str_weights = str_weights.split(";")
		for w in str_weights:
			w = misc.remove_starting_and_ending_space(w)
			if misc.check_integer(w, True):
				w = int(w)
				if w >= 0:
					weights.append(int(w))
				else:
					misc.error("Xml::build_weights() -> TAF_PARAMETER_WEIGHTS "+ TAF_PARAMETER_WEIGHTS +" must be positive or null")
		if sum(weights) == 0:
			misc.error("Xml::build_weights() -> at least one TAF_PARAMETER_WEIGHTS "+ TAF_PARAMETER_WEIGHTS +" must be positive")
			raise ValueError
	return weights


def build_boolean_parameter(n, d, node_xml, nbi):
	values, weights = build_categorical_parameter(node_xml)

	if len(values) != 2:
		misc.error("Xml::build_boolean_parameter() -> wrong boolean parameter values")
		raise ValueError
	for i in range(2):
		if values[i] in [True, "True", "true", 1]:
			values[i] = True
		elif values[i] in [False, "False", "false", "0"]:
			values[i] = False
		else:
			misc.error("Xml::build_boolean_parameter() -> wrong boolean parameter values")
			raise ValueError
	return Boolean_Parameter(n, d, values, weights, nbi, node_xml.attrib)


def build_string_parameter(n, d, node_xml, nbi):
	values, weights = build_categorical_parameter(node_xml)
	return String_Parameter(n, d, values, weights, nbi, node_xml.attrib)

def add_constraint_to_node(c,name, depth, node, child):
	#constraints array that store the constraints expressions to build
	constraints = []
	#regex pattern to find \\\\
	pattern = r"(.+?)\\\\(.+?)(?:\\|\s|$)"

	#forall expression of the constraint
	for i, e in enumerate(c.raw_expressions):
		match = re.search(pattern, c.raw_expressions[i])

		## constraint with \\
		if match:
			#get left and right element of regex
			left_element = match.group(1)
			right_element = match.group(2)

			curr_node = node
			c.raw_expressions[i] = c.raw_expressions[i].replace("\\\\","\\")
			constraints.append(str(c.raw_expressions[i]))
			c.raw_expressions[i] = constraints[0]

			#Loop from right_element until left_element is met
			while curr_node.name not in left_element:
				if curr_node.get_parent() is not None:
					#build an array of new constraints
					new_consts = constraints.copy()
					#add current node before right element
					for l in range(len(new_consts)):
						new_consts[l] = new_consts[l].replace(right_element, curr_node.name  + "\\" + right_element )

					#for all new constraints, add nb_instances after curr_node name
					for indice in range(len(new_consts)):
						for nb in range(curr_node.nb_instances):
								to_write=new_consts[indice]
								to_write= new_consts[indice].replace(curr_node.name + "\\", curr_node.name + "[" + str(nb) + "]" + "\\")
								constraints.append(to_write)
					#move the curr_node up the tree of node
					curr_node = curr_node.get_parent()
				else:
					#curr_node does not have parent (root node)
					break

			#Build all constraints from constraints array
			id=0
			for constraint in constraints:
				id = id +1
				new_c=build_constraint(name+"#"+str(id), depth+1,curr_node, child)
				new_c.raw_expressions[i] = constraint
				node.add_constraint(new_c)
		
		#classic constraint
		else:
			node.add_constraint(c)


def build_numerical_parameter(node_xml):
	minimum = check_attribute(node_xml, TAF_PARAMETER_MIN, True)
	maximum = check_attribute(node_xml, TAF_PARAMETER_MAX, True)

	distribution = check_attribute(node_xml, TAF_PARAMETER_DISTRIBUTION)
	mean = check_attribute(node_xml, TAF_PARAMATER_MEAN, False)
	variance = check_attribute(node_xml, TAF_PARAMETER_VARIANCE, False)
	ranges = []

	if not distribution:
		distribution = "u"
	if mean and misc.check_number(mean, True):
		mean = float(mean)
	else:
		mean = None
	if variance and misc.check_number(variance, True):
		variance = float(variance)
	else:
		variance = None
	if ranges:
		pass

	tmp = check_attribute(node_xml, TAF_PARAMETER_RANGES, False)
	if tmp:
		tmp = tmp.split(";")
		for r in tmp:
			r = misc.remove_starting_and_ending_space(r)
			r = r[1:-1].split(",")
			if len(r) != 2:
				misc.error("Xml::build_numerical_parameter() -> invalid TAF_PARAMETER_RANGES "+TAF_PARAMETER_RANGES)
				raise ValueError
			for i in range(2):
				r[i] = misc.remove_starting_and_ending_space(r[i])
			ranges.append((r[0], r[1]))

	return minimum, maximum, distribution, mean, variance, ranges, build_weights(check_attribute(node_xml, TAF_PARAMETER_WEIGHTS, False))


def build_integer_parameter(n, d, node_xml, nbi):
	minimum, maximum, distribution, mean, variance, str_ranges, weights = build_numerical_parameter(node_xml)
	misc.check_integer(minimum, True)
	minimum = int(minimum)
	misc.check_integer(maximum, True)
	maximum = int(maximum)

	ranges = []
	for r in str_ranges:
		if misc.check_integer(r[0], True) and misc.check_integer(r[1], True):
			ranges.append((int(r[0]), int(r[1])))
	return Integer_Parameter(n, d, minimum, maximum, distribution, mean, variance, ranges, weights, nbi, node_xml.attrib)


def build_real_parameter(n, d, node_xml, nbi):
	minimum, maximum, distribution, mean, variance, str_ranges, weights = build_numerical_parameter(node_xml)
	misc.check_number(minimum, True)
	minimum = float(minimum)
	misc.check_number(maximum, True)
	maximum = float(maximum)

	ranges = []
	for r in str_ranges:
		if misc.check_number(r[0], True) and misc.check_number(r[1], True):
			ranges.append((float(r[0]), float(r[1])))
	return Real_Parameter(n, d, minimum, maximum, distribution, mean, variance, ranges, weights, nbi, node_xml.attrib)



def build_constraint(n, d, node, node_xml,xml=None):
	save1 = node_xml.get(TAF_CONSTRAINT_TYPE)
	save2 = node_xml.get(TAF_CONSTRAINT_QUANTIFIERS)
	save3 = node_xml.get(TAF_CONSTRAINT_RANGES)
	expressions = []
	raw_expressions = check_attribute(node_xml, TAF_CONSTRAINT_EXPRESSIONS, True)
	raw_expressions = raw_expressions.split(";")
	types = []

	name = check_attribute(node_xml, "name", True)

	# Get expressions of the constraint
	for i in range(len(raw_expressions)):
		e = raw_expressions[i]

		##### Treat constraint for <type> ####

		# Get strings in the constraint that are followed by a \ and not ending with [i]
		pattern = r'([^\\\s]+)(?=\\)'
		matches = re.findall(pattern, e)
		filtered_matches = [match for match in matches if not re.search(r'\[\w+\]$', match)]
		# filtered_matches contains the string in the constraint corresponding to a type

		parent=node.get_parent()
		xml_depth = check_attribute(node_xml, "depth", False)

		for m in filtered_matches:
			node_type= m
			found = False
			for elem in xml.getroot().iter():
				# If there is an element in the xml with corresponding attribute type and wich name is same as the node being treated
				if TAF_TYPE in elem.attrib and elem.attrib[TAF_TYPE] == m:
					if node._name == elem.attrib[TAF_IDENTIFIER]:
						node_name = elem.attrib[TAF_IDENTIFIER]
						# Rewrite the constraint on type for the treated node, adding a forall and quantifier i

						#ICI le append
						forall = node_xml.get(TAF_CONSTRAINT_TYPE)
						quantif = node_xml.get(TAF_CONSTRAINT_QUANTIFIERS)
						rangess = node_xml.get(TAF_CONSTRAINT_RANGES)
						elem_depth = check_attribute(elem, "depth", False)
						letter = random.choice(string.ascii_lowercase)
						#letter = "a"

						if forall is None : 
							forall = "forall"		
						else:
							forall = forall + ";forall" 
						if quantif is None : 
							quantif = letter
						else: 
							quantif = quantif +";"+ letter
						if rangess is None : 
							rangess = "[0,"+ elem.attrib[TAF_IDENTIFIER] + ".nb_instances-1]"
						else: 
							rangess = rangess + ";[0,"+ elem.attrib[TAF_IDENTIFIER] + ".nb_instances-1]"

						e = e.replace(node_type, node_name + "["+letter+"]",1)

						if elem_depth is not None:
							if int(elem_depth) > node._depth :
								e = e
								letter2 = random.choice(string.ascii_lowercase)
								quantif = quantif +";"+ letter2
								rangess = rangess + ";[0,"+ elem.attrib[TAF_IDENTIFIER] + ".nb_instances-1]"
								forall = forall + ";forall" 
								e = e.replace(node_name, node_name + "["+letter2+"]\\"+node_name,1)
							else:
								e = e
						found=True

						node_xml.set(TAF_CONSTRAINT_TYPE,forall)
						node_xml.set(TAF_CONSTRAINT_QUANTIFIERS,quantif)
						node_xml.set(TAF_CONSTRAINT_RANGES,rangess)

			if (found != True) or parent.name == node.name:
				# If no matching node have been found, this mean we are treating the type node and the constraint is nullified
				e=e

		########################################
		raw_expressions[i] = e
		expressions.append(misc.remove_starting_and_ending_space(e))
	
	raw_constraint_types = check_attribute(node_xml, TAF_CONSTRAINT_TYPE, False)
	if raw_constraint_types is not None:
		raw_constraint_types = raw_constraint_types.split(";")
		for c in raw_constraint_types:
			c = misc.remove_starting_and_ending_space(c)
			if c in ["forall", "exist", "unique"]:
				types.append(c)
			else:
				misc.error("Xml::__build_constraint() -> unknown constraint type \"" + c + " must be forall, exists or unique "+ "\"")
				raise NameError

	quantifiers = []
	raw_quantifiers = check_attribute(node_xml, TAF_CONSTRAINT_QUANTIFIERS, False)

	if raw_quantifiers is not None:
		raw_quantifiers = raw_quantifiers.split(";")
		for l in raw_quantifiers:
			l = misc.remove_starting_and_ending_space(l)
			if misc.check_letter(l, True):
				quantifiers.append(l)

	ranges = []
	raw_ranges = check_attribute(node_xml, TAF_CONSTRAINT_RANGES, False)

	if raw_ranges is not None:
		raw_ranges = raw_ranges.split(";")
		for r in raw_ranges:
			r = misc.remove_starting_and_ending_space(r)
			if r == "all":
				ranges.append(r)
			elif r[0] == "[" and r[-1] == "]":
				boundaries = r[1:-1].split(",")
				if len(boundaries) != 2:
					misc.error("Xml::build_constraint() -> wrong ranges syntax")
					raise ValueError
				ranges.append((misc.remove_starting_and_ending_space(boundaries[0]), misc.remove_starting_and_ending_space(boundaries[1])))
			else:
				misc.error("Xml::build_constraint() -> wrong ranges syntax")
				raise ValueError

	if len(quantifiers) != len(ranges) or len(quantifiers) != len(types):
		misc.error("Xml::build_constraint() -> the number of quantifiers must equal the number of ranges and types : "+str(quantifiers)+str(ranges)+str(types))
		raise ValueError

	if parent is not None and node is not None and parent.name != node.name:
		node_xml.set(TAF_CONSTRAINT_TYPE,save1)
		node_xml.set(TAF_CONSTRAINT_QUANTIFIERS,save2)
		node_xml.set(TAF_CONSTRAINT_RANGES,save3)

	node_xml.set(TAF_CONSTRAINT_TYPE,save1)
	node_xml.set(TAF_CONSTRAINT_QUANTIFIERS,save2)
	node_xml.set(TAF_CONSTRAINT_RANGES,save3)

	return Constraint(n, d, node, expressions, types, quantifiers, ranges)


def check_nb_instances(nb):
	misc.check_integer(nb, True)
	if int(nb) >= 0:
		return True
	else:
		misc.error("Xml::check_nb_instances() -> nb_instances must be a positive integer value")
		raise ValueError


def check_attribute(node_xml, att, err=False):
	if att in node_xml.attrib:
		return node_xml.attrib[att]
	else:
		if err:
			misc.error("Xml::check_attribute() -> \"" + att + "\" attribute is missing")
			raise NameError
		else:
			return None


#########################################

### XML WRITE TEST CASE 

#########################################


def write_test_case(root_node, seed, path):
	root = ET.Element(root_node.name)
	root.append(ET.Element("seed", value=seed))
	current_container = root_node.get_container_i(0)
	write_data(current_container, root)
	xml_str = ET.tostring(root, encoding='utf-8')
	dom = minidom.parseString(xml_str)
	with open(path, "w") as f:
		f.write(dom.toprettyxml())
	

def write_data(current_container, parent):
	# print(f"Current container: {current_container}")
	for p in current_container.parameters:
		tmp_param = current_container.get_parameter_n(p)
		param_element = ET.SubElement(parent, p)
		for key, value in tmp_param._attribs.items():
			if key not in TAF_KEYS:
				param_element.set(key, value)
		values = ";".join(str(tmp_param.values[i]) for i in range(tmp_param.nb_instances))
		param_element.text = values

	for c in current_container.children:
		child_node = current_container.get_child_n(c)
		# print(f"Child node: {child_node}")
		# print("test écriture")
		# print(child_node.name, child_node.get_nb_instances())
		if child_node is None:
			continue
		for i in range(child_node.nb_instances):
			instance_str = f"{i}/{child_node.nb_instances - 1}"
			instance_attr = {"instance": instance_str}
			instance_element = ET.SubElement(parent, child_node.name, instance_attr)
			write_data(child_node.get_container_i(i), instance_element)


##################################################

### XML READING FOR PARTIAL INSTANCES          

##################################################

def read_test_case(path, root_node):
	root_xml = parse_xml(path)
	seed = "r"
	root_xml_element = root_xml.getroot()
	if root_node.name == root_xml_element.tag:
		if root_xml_element[0].tag == "seed": #s'il reste la seed
			if "value" in root_xml_element[0].attrib:
				seed = root_xml_element[0].attrib["value"] #on la récupère
				root_xml_element.remove(root_xml_element[0])
				# return seed
			else:
				misc.error("Xml::read_template() -> seed value is missing")
				raise ValueError
	else:
		misc.error("Xml::read_genotype() -> node name does not match")
		raise ValueError
	
	set_element(root_xml_element, root_node)
	#print("fin de read :")
	root_node.print_structure()
	#print(f"seed : {seed}")
	return seed



def set_element(node_xml, root_node, i=0):
	# print(" ***********set_element*********** ")
	# print(f"i : {i}")
	for child in node_xml:
		# print(f"\n{child} depuis {node_xml}")
		# print(child.tag, child.attrib, len(child), child.text)
		if len(child) == 0:
			set_parameter(child, root_node, i)
		else:
			set_node(child, root_node, i)
	# print(f"boucle set elem finie de {node_xml}")


def set_parameter(node_xml, root_node, i):
	name = node_xml.tag
	#print(f"\tset_parameter : {name}")
	#print(root_node.parameters)
	if name in root_node.parameters:
		param = root_node.get_parameter_n(name, i)
		if node_xml.text != None :
			values = node_xml.text.split(";")
		else :
			values = [0]
		length = len(values)
		# print(f"value = {values} et length = {length}")
		param.change_nb_instances(length)
		for i in range(length):
			if not values[i] in ["r", ""]:
				param.set_value_i(i, misc.remove_starting_and_ending_space(values[i]))
				param.lock_i(i)
	else:
		misc.error("Xml::set_parameter() -> parameter name \"" + name + "\" does not match")
		raise NameError

def set_node(node_xml, root_node, i):
	name = node_xml.tag
	# print(f"\tset_node {name} et i={i}")
	if name in root_node.children:
		elem = root_node.get_child_n(name, i)
		# print(elem)
		raw_identifier = check_attribute(node_xml, "instance")
		if raw_identifier is None:
			raw_identifier = "0"
		# print(f"raw identif : {raw_identifier}")

		identifier = raw_identifier.split("/")[0]  # Prends le nb d'instance
		if misc.check_integer(identifier, True):
			identifier = int(identifier)  # Le convertit en int
		if "/" in raw_identifier:
			max_identifier = raw_identifier.split("/")[1]
			if misc.check_integer(max_identifier, True):
				max_identifier = int(max_identifier)
				# print(f"max identif : {max_identifier}")
				if not elem.nb_instances_lock:
					# print(f"on change les nb instances en max id + 1 : {max_identifier + 1}")
					elem.change_nb_instances(max_identifier + 1)
					elem.lock_nb_instances()
					# print(elem)

		if elem.nb_instances is None or identifier + 1 > elem.nb_instances:
			# print("\t^^^^^^^^^^^^^^^^^^^on rentre là ?")
			elem.change_nb_instances(identifier + 1)
			set_element(node_xml, elem, identifier) 
			if not elem.nb_instances_lock:
				elem.reduce_nb_instances_interval(identifier)
		else:
			# print(f"\nidentifier : {identifier}")
			set_element(node_xml, elem, identifier)