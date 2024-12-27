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

###############################################################################
# --- Element --------------------------------------------------------------- #
###############################################################################
class Element(object):
	def __init__(self, n, d):
		"""
		:param n	: name
		:param d	: depth
		"""
		self.__check_name(n)
		self._name = n
		self._depth = d

	def __check_name(self, n):
		if len(n) < 1:
			misc.error("Element::__check_name() -> names must be at least one character long")
			raise NameError
		if not n[0].islower():
			misc.error("Element::__check_name() -> names must start by a lower case character")
			raise NameError
		for letter in n:
			if not letter.isalpha() and letter != "_" and letter != "#" and not letter.isdigit():
				misc.error("Element::__check_name() -> invalid character: \"" + letter + "\"")
				raise NameError

	def get_type(self):
		raise NotImplementedError

	def get_name(self):
		return self._name
	name = property(get_name)

	def get_depth(self):
		return self._depth
	depth = property(get_depth)
