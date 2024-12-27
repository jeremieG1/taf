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
# --- Miscellaneous module -------------------------------------------------- #
###############################################################################
import os

def color(s, c):
	if c == "red":
		s = "\033[31m" + s
	elif c == "green":
		s = "\033[32m" + s
	elif c == "yellow":
		s = "\033[33m" + s
	elif c == "blue":
		s = "\033[34m" + s
	elif c == "magenta":
		s = "\033[35m" + s
	elif c == "cyan":
		s = "\033[36m" + s
	else:
		s = "\033[37m" + s
	return s + "\033[0m"


def underline(s):
	return "\033[38;4m" + s + "\033[0m"


def check_file(f, verbose, err=False):
	if os.path.isfile(f):
		return True
	else:
		s = "Miscellaneous::file_check() -> \"" + f + "\" does not exist"
		if err:
			error(s)
		else:
			if verbose:
				print(s)
			return False


def check_folder(f, err=False):
	if os.path.isdir(f):
		return True
	else:
		s = "Miscellaneous::folder_check() -> \"" + f + "\" does not exist"
		if err:
			error(s)
		else:
			print(s)
			return False


def error(s):
	print (color("ERROR -> " + s, "red"))


def warning(s):
	print (color("WARNING -> " + s, "yellow"))


def check_letter(l, err=False):
	if len(l) == 1 and str.isalpha(l):
		return True
	else:
		if err:
			error("Miscellaneous::check_letter() -> \"" + l + "\" is not a letter")
			raise ValueError
		return False


def check_number(n, err=False):
	try:
		n = float(n)
		return True
	except ValueError:
		if err:
			error("Miscellaneous::check_number() -> \"" + n + "\" is not a number")
			raise ValueError
		return False


def check_integer(n, err=False):
	try:
		n = int(n)
		return True
	except ValueError:
		if err:
			error("Miscellaneous::check_integer() -> \"" + n + "\" is not an integer")
			raise ValueError
		return False


def remove_heading_zero(n):
	if n[0] == "-":
		n = n[1:]

	head = True
	while head:
		if len(n) > 1 and n[0] == "0" and n[1] != ".":
			n = n[1:]
		else:
			head = False
	return n


def remove_starting_and_ending_space(s):
	if s:
		while s[0] == " ":
			s = s[1:]
		while s[-1] == " ":
			s = s[:-1]
	return s


def adler32(s):
	s1 = 1
	s2 = 0
	for c in s:
		c = ord(c)
		s1+= c
		s2+= s1
	s1%= 65521
	s2%= 65521
	return 65536*s2 + s1


def get_separator():
	return color("--------------------------------------------------------------------------------", "yellow")
