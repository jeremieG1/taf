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

import Miscellaneous as misc
#from Taf import SETTINGS
from Element import Element

###############################################################################
# --- Parameter ------------------------------------------------------------- #
###############################################################################
class Parameter(Element):
	"""
	A Parameter object hold an array of variables and everything required to generate them
	"""
	counter = 0

	def __init__(self, n, d, nb, attribs):
		"""
		:param n	: name
		:param d	: depth
		:param nb	: nb_instances
		:param attribs : xml_attribs
		"""
		Element.__init__(self, n, d)

		self.__check_nb_instances(nb)
		self._nb_instances = nb
		self._identifier = "var_" + str(Parameter.counter)
		self._values = [None]*self._nb_instances
		self._locks = [False]*self._nb_instances
		self._nb_instances_lock = False
		#######
		self._attribs = attribs
		Parameter.counter += 1

	def __check_nb_instances(self, nb):
		from Taf import SETTINGS
		if not 0 <= nb <= SETTINGS.get("parameter_max_nb_instances"):
			misc.error("Parameter::__check_nb_instances() -> " + self._name + ": nb_instances parameter is out of range [0 ; " + str(SETTINGS.get("parameter_max_nb_instances")) + "]")
			raise ValueError

	def change_nb_instances(self, nb):
		if not self._nb_instances_lock:
			self.__check_nb_instances(nb)

			while self._nb_instances > nb:
				self._values.pop()
				self._locks.pop()
				self._nb_instances -= 1
			while self._nb_instances < nb:
				self._values.append(None)
				self._locks.append(False)
				self._nb_instances += 1

	def lock_nb_instances(self):
		self._nb_instances_lock = True

	def lock_i(self, i):
		self._locks[i] = True

	def lock_all(self):
		for i in range(self._nb_instances):
			self.lock_i(i)

	def unlock_nb_instances(self):
		self._nb_instances_lock = False

	def unlock_i(self, i):
		self._locks[i] = False

	def unlock_all(self):
		for i in range(self._nb_instances):
			self.unlock_i(i)

	def reset_i(self, i):
		if not self._locks[i]:
			self._values[i] = None

	def reset_all(self):
		for i in range(self._nb_instances):
			self.reset_i(i)

	def _random_gen(self):
		"""
		Generate a parameter content according to the selected method
		:return: the parameter content
		"""
		raise NotImplementedError

	def set_value_i(self, i, val):
		"""
		Set the parameter i content according to val.
		val can be "r" for random or a specific value.
		The function will do nothing if the parameter is locked (locks[i] == True)
		:param i	: the parameter index
		:param val	: "r" or a specific value
		:return		: None
		"""
		raise NotImplementedError

	def set_all_values(self, val):
		for i in range(self._nb_instances):
			self.set_value_i(i, val)
	
	def duplicate(self):
		"""
		Create a new instance of the parameter with the same initial settings
		:return: A parameter object
		"""
		raise NotImplementedError

	def __repr__(self):
		return "name: " + self._name +\
			   "\nidentifier: " +str(self._identifier) +\
			   "\ndepth: " + str(self._depth) +\
			   "\nnb_instances: " + str(self._nb_instances) +\
			   "\nvalues: " + str(self._values) +\
			   "\nlocks: " + str(self._locks) +\
			   "\nattribs: " + str(self._attribs)

	def get_type(self):
		raise NotImplementedError

	def get_values(self):
		return self._values
	values = property(get_values)

	def get_identifier(self):
		return self._identifier
	identifier = property(get_identifier)

	def get_nb_instances_lock(self):
		return self._nb_instances_lock
	nb_instances_lock = property(get_nb_instances_lock)

	def get_locks(self):
		return self._locks
	locks = property(get_locks)

	def get_nb_instances(self):
		return self._nb_instances
	nb_instances = property(get_nb_instances)

###############################################################################
# --- Categorical-Parameter ------------------------------------------------- #
###############################################################################
class Categorical_Parameter(Parameter):
	def __init__(self, n, d, v, w, nb, attribs):
		"""
		:param n	: name
		:param d	: depth
		:param v	: values
		:param w	: weights
		:param nb	: nb_instances
		"""
		Parameter.__init__(self, n, d, nb, attribs)

		self._check_values(v)
		self._values_array = v
		self.__check_weights(w)
		self._weights_array = w

	def _check_values(self, v):
		raise NotImplementedError

	def __check_weights(self, w):
		if w:
			if len(self._values_array) != len(w):
				misc.error("Categorical_Parameter::__check_weights() -> " + self._name + ": values array size and weights array size must be equal")
				raise ValueError

	def _random_gen(self):
		if self._weights_array:
			return self._discrete_distribution_selection()
		else:
			return self._values_array[np.random.randint(0, len(self._values_array))]

	def _discrete_distribution_selection(self):
		r = round(np.random.randint(sum(self._weights_array)))

		counter = 0
		for i in range(len(self._weights_array)):
			if counter <= r < (counter + self._weights_array[i]):
				return self._values_array[i]
			counter += self._weights_array[i]

	def get_values_array(self):
		return self._values_array
	values_array = property(get_values_array)

	def get_weights_array(self):
		return self._weights_array
	weights_array = property(get_weights_array)

	def __repr__(self):
		return Parameter.__repr__(self) +\
				"\nvalues_possibles: " + str(self._values_array) +\
				"\nweights: " + str(self._weights_array)

###############################################################################
# --- Boolean_Parameter ----------------------------------------------------- #
###############################################################################
class Boolean_Parameter(Categorical_Parameter):
	def __init__(self, n, d, v, w, nb, attribs):
		"""
		:param n	: name
		:param d	: depth
		:param v	: values
		:param w	: weights
		:param nb	: nb_instances
		"""
		Categorical_Parameter.__init__(self, n, d, v, w, nb, attribs)

	def _check_values(self, v):
		pass

	def set_value_i(self, i, val):
		if not self._locks[i]:
			if val == 'r':
				self._values[i] = self._random_gen()
			elif val in [True, "True", 1, "1"]:
				self._values[i] = True
			elif val in [False, "False", 0, "O"]:
				self._values[i] = False
			else:
				misc.error("Boolean_Parameter::set_value_i() -> " + self._name + ": unknow value parameter \"" + val + "\"")
				raise ValueError

	def duplicate(self):
		return Boolean_Parameter(self._name, self._depth, self._values_array, self._weights_array, self._nb_instances, self._attribs)

	def get_type(self):
		return "boolean"

	def __repr__(self):
		return misc.color("--- Boolean_Parameter ---", "yellow") + "\n" + Categorical_Parameter.__repr__(self)

###############################################################################
# --- String_Parameter ------------------------------------------------------ #
###############################################################################
class String_Parameter(Categorical_Parameter):
	def __init__(self, n, d, v, w, nb,attribs):
		"""
		:param n	: name
		:param d	: depth
		:param v	: an array that contains all possible values as a string
		:param w	: an array (int) that contains a weight corresponding to the associated value
		:param nb	: nb_instances
		"""
		self._attribs = attribs
		Categorical_Parameter.__init__(self, n, d, v, w, nb, attribs)

	def _check_values(self, v):
		from Taf import SETTINGS
		if not 1 <= len(v) <= SETTINGS.get("string_parameter_max_size"):
			misc.error("Categorical_Parameter::__check_values() -> " + self._name + ": values array size is out of range [1 ;" + str(SETTINGS.get("string_parameter_max_size")) + "]")
			raise ValueError

	def set_value_i(self, i, val):
		if not self._locks[i]:
			if val == "r":
				self._values[i] = self._random_gen()
			elif val == "first":
				self._values[i] = self._values_array[0]
			elif val == "last":
				self._values[i] = self._values_array[-1]
			elif val == "wmin":
				self._values[i] = self.__get_wmin()
			elif val == "wmax":
				self._values[i] = self.__get_wmax()
			elif val in self._values_array:
				self._values[i] = val
			else:
				misc.error("String_Parameter::set_value_i() -> " + self._name + ": invalid parameter: " + str(self._values_array))
				raise NameError

	def __get_wmin(self):
		wmin = 999
		wmin_index = 0
		for w, i in enumerate(self._weights_array):
			if w < wmin:
				wmin = w
				wmin_index = i
		return self._values_array[wmin_index]

	def __get_wmax(self):
		wmax = 0
		wmax_index = 0
		for w, i in enumerate(self._weights_array):
			if w > wmax:
				wmax = w
				wmax_index = i
		return self._values_array[wmax_index]

	def duplicate(self):
		return String_Parameter(self._name, self._depth, self._values_array, self._weights_array, self._nb_instances, self._attribs)

	def get_type(self):
		return "string"

	def __repr__(self):
		return misc.color("--- String_Parameter ---", "yellow") + "\n" + Categorical_Parameter.__repr__(self)

###############################################################################
# --- Numerical_Parameter --------------------------------------------------- #
###############################################################################
class Numerical_Parameter(Parameter):
	def __init__(self, n, d, m, M, dis, mea, var, r, w, nb, attribs):
		"""
		:param n	: name
		:param d	: depth
		:param m	: min value
		:param M	: max value
		:param dis	: distribution -> "u" for a uniform | "n" for a normal | i for an interval
		:param mea	: mean
		:param var	: variance
		:param r	: ranges
		:param w	: weights
		:param nb	: nb_instances
		"""
		Parameter.__init__(self, n, d, nb, attribs)

		self._min = m
		self._max = M
		self._check_min_max_order()

		self._mean = None
		self._variance = None
		self._ranges = None
		self._intervals = None

		self.__check_distribution(dis)
		self._distribution = dis
		self.__set_mean_and_variance(mea, var)
		self.__check_ranges(r)
		self._ranges = r
		self.__set_intervals(r, w)

	def __check_distribution(self, dis):
		if dis not in ["u", "n", "i"]:
			misc.error("Numerical_Parameter::__check_distribution() -> " + self._name + ": invalid distribution [\"u\", \"n\" ,\"i\"]")
			raise NameError

	def _check_min_max_order(self):
		if self._min > self._max:
			misc.error("Numerical_Parameter::__check_min_max_order() -> " + self._name + ": max value should be greater than min value")
			raise ValueError

	def _check_value(self, val):
		if not self._min <= val <= self._max:
			print("VAL")
			print(val)
			misc.error("Numerical_Parameter::_check_value() -> " + self._name + ": value parameter out of range[" + str(self._min) + ";" + str(self._max) + "]")
			raise ValueError

	def __check_ranges(self, ranges):
		if ranges:
			for r in ranges:
				for i in range(2):
					if not self._min <= r[i] <= self._max:
						misc.error("Numerical_Parameter::_check_ranges() -> " + self._name + ": invalid range value [" + str(self._min) + ";" + str(self._max) + "]")
						raise ValueError
				if r[1] < r[0]:
					misc.error("Numerical_Parameter::_check_ranges() -> " + self._name + ": invalid range value [" + str(self._min) + ";" + str(self._max) + "]")
					raise ValueError

	def __set_mean_and_variance(self, mea, var):
		if mea is None and var is None:
			self._mean = round((self._max + self._min)/2.0, 5)
			self._variance = round((self._max - self._min)/4.0, 5)
		else:
			if not self._min <= mea <= self._max:
				misc.error("Numerical_Parameter::__set_mean_and_variance() -> " + self._name + ": mean value must be between min and max")
				raise ValueError
			self._mean = round(mea, 5)
			if var < 0:
				misc.error("Numerical_Parameter::__set_mean_and_variance() -> " + self._name + ": variance value must be positive or null")
				raise ValueError
			self._variance = round(var, 5)

	def __set_intervals(self, r, w):
		if r:
			v = []
			for i in range(len(r)):
				v.append(str(i))
			self._intervals = String_Parameter("interval", -1, v, w, 1)

	def _random_gen(self):
		if self._distribution == "u":
			val = (self._max - self._min)*np.random.rand() + self._min
		elif self._distribution == "n":
			if self._variance == 0:
				val = self._mean
			else:
				val = np.random.normal(self._mean, self._variance, 1)[0]
				while not self._min <= val <= self._max:
					val = np.random.normal(self._mean, self._variance, 1)[0]
		else:
			self._intervals.set_value_i(0, "r")
			index = int(self._intervals.values[0])
			val = (self._ranges[index][1] - self._ranges[index][0])*np.random.rand() + self._ranges[index][0]
		return val

	def set_value_i(self, i, val):
		if val == "r":
			self._values[i] = self._random_gen()
			return True
		elif val == "min":
			self._values[i] = self._min
			return True
		elif val == "max":
			self._values[i] = self._max
			return True
		elif val == "mean":
			self._values[i] = self._mean
			return True
		else:
			return False

	def __repr__(self):
		return Parameter.__repr__(self) +\
				"\nmin: " + str(self._min) +\
				"\nmax: " + str(self._max) +\
				"\ngenerator: " + str(self._distribution) +\
				"\nmean: " + str(self._mean) +\
				"\nvariance: " + str(self._variance) +\
			    "\nranges: " + str(self._ranges) + \
			    "\nweights: " + str(self.get_weights())

	def get_m(self):
		return self._min
	m = property(get_m)

	def get_M(self):
		return self._max
	M = property(get_M)

	def get_distribution(self):
		return self._distribution
	distribution = property(get_distribution)

	def get_mean(self):
		return self._mean
	mean = property(get_mean)

	def get_variance(self):
		return self._variance
	variance = property(get_variance)

	def get_ranges(self):
		return self._ranges
	ranges = property(get_ranges)

	def get_weights(self):
		w = []
		if self._intervals:
			w = self._intervals.weights_array
		return w
	weights = property(get_weights)

###############################################################################
# --- Integer_Parameter ----------------------------------------------------- #
###############################################################################
class Integer_Parameter(Numerical_Parameter):
	def __init__(self, n, d, m, M, dis, mea, var, r, w, nb, attribs):
		"""
		:param n	: name
		:param d	: depth
		:param m	: min value
		:param M	: max value
		:param dis	: distribution -> "u" for a uniform | "n" for a normal | i for an interval
		:param mea	: mean
		:param var	: variance
		:param r	: ranges
		:param w	: weights
		:param nb	: nb_instances
		"""
		Numerical_Parameter.__init__(self, n, d, m, M, dis, mea, var, r, w, nb, attribs)

	def _random_gen(self):
		return int(round(super(Integer_Parameter, self)._random_gen(), 0))

	def set_value_i(self, i, val):
		if not self._locks[i] and not super(Integer_Parameter, self).set_value_i(i, val):
			if misc.check_integer(val):
				val = int(val)
				self._check_value(val)
				self._values[i] = val
			else:
				misc.error("Integer_Parameter::set_value_i() -> " + self._name + ": string value parameter unknown")
				raise NameError

	def duplicate(self):
		return Integer_Parameter(self._name, self._depth, self._min, self._max, self._distribution, self._mean, self._variance, self._ranges, self.get_weights(), self._nb_instances, self._attribs)

	def reduce_interval(self, m):
		if self._min <= m <= self._max:
			self._min = m
		elif m > self._max:
			misc.error("Integer_Parameter::reduce_interval() -> " + self._name + ": new minimal number of instances is out of range")
			raise ValueError

	def get_type(self):
		return "integer"

	def __repr__(self):
		return misc.color("--- Integer_Parameter ---", "yellow") + "\n" + Numerical_Parameter.__repr__(self)

###############################################################################
# --- Real_Parameter -------------------------------------------------------- #
###############################################################################
class Real_Parameter(Numerical_Parameter):
	def __init__(self, n, d, m, M, dis, mea, var, r, w, nb, attribs):
		"""
		:param n	: name
		:param d	: depth
		:param m	: min value
		:param M	: max value
		:param dis	: distribution -> "u" for a uniform | "n" for a normal | i for an interval
		:param mea	: mean
		:param var	: variance
		:param r	: ranges
		:param w	: weights
		:param nb	: nb_instances
		"""
		Numerical_Parameter.__init__(self, n, d, m, M, dis, mea, var, r, w, nb, attribs)

	def _random_gen(self):
		return round(super(Real_Parameter, self)._random_gen(), 5)

	def set_value_i(self, i, val):
		if not self._locks[i] and not super(Real_Parameter, self).set_value_i(i, val):
			if misc.check_number(val):
				val = round(float(val), 5)
				self._check_value(val)
				self._values[i] = val
			else:
				misc.error("Real_Parameter::set_value_i() -> " + self._name + ": string value parameter unknown")
				raise NameError

	def duplicate(self):
		return Real_Parameter(self._name, self._depth, self._min, self._max, self._distribution, self._mean, self._variance, self._ranges, self.get_weights(), self._nb_instances, self._attribs)

	def get_type(self):
		return "real"

	def __repr__(self):
		return misc.color("--- Real_Parameter ---", "yellow") + "\n" + Numerical_Parameter.__repr__(self)
