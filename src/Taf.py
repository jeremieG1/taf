#!/usr/bin/env python3

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

import cmd
import os
import sys
import xml.etree.ElementTree as ET

from Export_Generator import create_minimal_export
create_minimal_export()
import Miscellaneous as misc
from Tree import *
from Generator import *

import time

###############################################################################
# --- CLI ------------------------------------------------------------------- #
###############################################################################
class CLI(cmd.Cmd, object):
	def __init__(self):
		super(CLI, self).__init__()

		main_color = "cyan"
		shadow_color = "magenta"
		self.intro = misc.color(u"\n       \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588", main_color) +\
					misc.color(u"\u2557  ", shadow_color) + \
					misc.color(u"\u2588\u2588\u2588\u2588\u2588\u2588", main_color) + \
					misc.color(u"\u2557  ", shadow_color) + \
					misc.color(u"\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588", main_color) + \
					misc.color(u"\u2557\n", shadow_color) + \
					misc.color(u"       \u255A\u2550\u2550", shadow_color) + \
					misc.color(u"\u2588\u2588", main_color) + \
					misc.color(u"\u2554\u2550\u2550\u255D ", shadow_color) + \
					misc.color(u"\u2588\u2588", main_color) + \
					misc.color(u"\u2554\u2550\u2550\u2550", shadow_color) + \
					misc.color(u"\u2588\u2588", main_color) + \
					misc.color(u"\u2557 ", shadow_color) + \
					misc.color(u"\u2588\u2588", main_color) + \
					misc.color(u"\u2554\u2550\u2550\u2550\u2550\u2550\u255D\n", shadow_color) + \
					misc.color(u"   \u2588\u2588\u2588", main_color) + \
					misc.color(u"\u2557", shadow_color) + \
					misc.color(u"   \u2588\u2588", main_color) + \
					misc.color(u"\u2551    ", shadow_color) + \
					misc.color(u"\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588", main_color) + \
					misc.color(u"\u2551 ", shadow_color) + \
					misc.color(u"\u2588\u2588\u2588\u2588\u2588", main_color) + \
					misc.color(u"\u2557   ", shadow_color) + \
					misc.color(u"\u2588\u2588\u2588", main_color) + \
					misc.color(u"\u2557\n", shadow_color) + \
					misc.color(u"   \u255A\u2550\u2550\u255D", shadow_color) + \
					misc.color(u"   \u2588\u2588", main_color) + \
					misc.color(u"\u2551    ", shadow_color) + \
					misc.color(u"\u2588\u2588", main_color) + \
					misc.color(u"\u2554\u2550\u2550\u2550", shadow_color) + \
					misc.color(u"\u2588\u2588", main_color) + \
					misc.color(u"\u2551", shadow_color) + \
					misc.color(u" \u2588\u2588", main_color) + \
					misc.color(u"\u2554\u2550\u2550\u255D   ", shadow_color) + \
					misc.color(u"\u255A\u2550\u2550\u255D\n", shadow_color) + \
					misc.color(u"          \u2588\u2588", main_color) + \
					misc.color(u"\u2551    ", shadow_color) + \
					misc.color(u"\u2588\u2588", main_color) + \
					misc.color(u"\u2551   ", shadow_color) + \
					misc.color(u"\u2588\u2588", main_color) + \
					misc.color(u"\u2551 ", shadow_color) + \
					misc.color(u"\u2588\u2588", main_color) + \
					misc.color(u"\u2551\n", shadow_color) + \
					misc.color(u"          \u255A\u2550\u255D    \u255A\u2550\u255D   \u255A\u2550\u255D \u255A\u2550\u255D\n",shadow_color)

		self.prompt = "TAF > "

		self.p = Path()
		self.tree = None
		self.overwrite = False
		self.verbose = True
		self.auto = False

	def emptyline(self):
		pass

	def help_help(self):
		print(" - print some help. The same command can be executed using \"" + misc.underline("?") + "\".")

	def do_exit(self, arg):
		return True

	def help_exit(self):
		print("exit taf interpreter")

	def do_quit(self, arg):
		return True

	def help_quit(self):
		print("quit taf interpreter")

	def do_shell(self, arg):
		os.system(arg)

	def help_shell(self):
		print(" - run a shell command. The same command can be executed using \"" + misc.underline("!") + "\".")

	def do_set(self, arg):
		arg = arg.split(" ")
		if len(arg) != 2:
			print(misc.color("Usage: set setting_parameter value", "red"))
		else:
			key = arg[0]
			value = arg[1]
			skip_flag = False
			if value[-1] == "!":
				skip_flag = True
				value = value[:-1]
			SETTINGS.set(key, value, skip_flag)

	def help_set(self):
		print(" - set the value of the setting parameter given as argument.\n - Usage: set setting_parameter value\n - Add a \"" + misc.underline("!") + "\" after the value to skip the confirmation")

	def do_display(self, arg):
		SETTINGS.display(arg)

	def help_display(self):
		print(" - print the value of the setting parameter given as argument.\n - Use \"" + misc.underline("all") + "\" to print every setting parameter.")

	def do_overwrite(self, arg=None):
		self.overwrite = True

	def help_overwrite(self):
		print(" - set overwrite to True. Existing file in the generated structure will be overwritten during generation.")

	def do_silent(self, arg):
		self.verbose = False

	def help_silent(self):
		print(" - set verbose to True. Details will be printed during generation.")

	def do_parse_template(self,args=None): #Args default set to None to abe able to call the function with no args
		path = SETTINGS.get("template_path") + SETTINGS.get("template_file_name")
		print("parsing template: " + misc.color(path, "cyan"))
		if not misc.check_file(path, True):
			return
		self.tree = Tree(path)
		# self.tree.print_current_node()

		if self.tree.is_parsed:
			self.tree.generate_export_functions()

	def help_parse_template(self):
		print(" - parse the template pointed by the setting parameters.\n - current path: " + SETTINGS.get("template_path") + SETTINGS.get("template_file_name"))

	def do_generate(self,args=None): #Args default set to None to abe able to call the function with no args
		if self.tree is None:
			print("A template must be parsed first")
			return

		if not self.p.check_path(self.auto, self.verbose):
			print("file hierarchy is incomplete!")
			return

		times=[]
		for i in range(1, int(SETTINGS.get("nb_test_cases") + 1)):
			start = time.time()	
			self.__generate_test_case()			
			end = time.time()
			times.append(end - start)
				
			with open(self.p.get_experiment_path() + "time", "a") as f:
				f.write(str(end-start) + "\n")
				if(i == int(SETTINGS.get("nb_test_cases"))):
					avg_time = sum(times) / len(times)
					f.write("Average time: " + str(avg_time) + "\n")
			print("time: " + str(end-start))
				
			while True:
				if self.verbose:
					print("generate test artifact")
				
				self.__generate_test_artifact()			

				if not self.p.next_test_artifact():
					if not self.p.next_path():
						return
					break	
			self.tree = Tree(SETTINGS.get("template_path") + SETTINGS.get("template_file_name"))
				

	def __generate_test_case(self):
		tmp_path = self.p.get_current_test_case_path() + SETTINGS.get("test_case_folder_name") + "_" + str(self.p.get_current_test_case_nb()) + ".xml"
		if self.verbose:
			print("Current path: " + misc.color(self.p.get_current_test_case_path(), "cyan"))
		if misc.check_file(tmp_path, self.verbose):
			if self.verbose:
				print("Parsing existing test case: " + misc.color(tmp_path, "cyan"))
			if not self.overwrite:
				self.tree.read_test_case(tmp_path)
		else:
			if self.verbose:
				print("Create new test case: " + misc.color(SETTINGS.get("test_case_folder_name") + ".xml", "cyan"))

		while not self.tree.generate(self.verbose):
			counter = 0
			print(counter)
			self.tree = Tree(SETTINGS.get("template_path") + SETTINGS.get("template_file_name"))
			counter += 1
		if self.verbose:
			self.tree.print_current_node()
		self.tree.write_test_case(tmp_path)
		

	def __generate_test_artifact(self):
		if self.verbose:
			print("Current path: " + misc.color(self.p.get_current_test_artifact_path(), "cyan"))
		
		self.tree.export(self.p.get_current_test_artifact_path()) # normalement à la fin de la fonction
		if os.listdir(self.p.get_current_test_artifact_path()):
			if self.overwrite:
				print(self.p.get_current_test_artifact_path() + " already exists . Overwrite!")
			else:
				return

	def help_generate(self):
		print(" - Generate test case and test artifact.\n - A template must be parsed first")

	def do_print_test_case(self, arg):
		self.tree.print_current_node()

	def help_print_test_case(self):
		print(" - print the current test case.")

	def do_stat(self, arg):
		stat_path = self.p.get_experiment_path() + "stat.cvs"
		if misc.check_file(stat_path, self.verbose):
			if self.overwrite:
				print(stat_path + " already exists . Overwrite!")
			else:
				return
		if self.verbose:
			print("Creating stat: " + misc.color(stat_path, "cyan"))

		final_stat_array = self.tree.get_empty_stat_array()
		while True:
			tmp_path = self.p.get_current_test_case_path() + SETTINGS.get("test_case_folder_name") + "_" + str(self.p.get_current_test_case_nb()) + ".xml"
			print("dans do stat")
			self.tree.read_test_case(tmp_path)

			if self.verbose:
				print("Adding to stat: " + misc.color(tmp_path, "cyan"))
			current_stat_array = self.tree.get_stat_array()
			for i in range(len(final_stat_array)):
				final_stat_array[i].append(current_stat_array[i])
			if not self.p.next_test_case():
				break
			self.tree.reset()

		self.__write_stat(final_stat_array)

	def __write_stat(self, stat_array):
		s = ""
		for line in stat_array:
			for element in line:
				s += str(element) + ";"
			s = s[:-1]
			s += "\n"

		with open(self.p.get_experiment_path() + "stat.cvs", "w") as f:
			f.write(s)

	def preloop(self):
		if len(sys.argv) > 1:
			self.auto = True
			print(misc.color("* ---------------- *", "magenta"))
			print(misc.color("|  ", "magenta") +\
				  misc.color("XXX: mode auto", "cyan") + \
				  misc.color("  |", "magenta"))
			print(misc.color("* ---------------- *", "magenta"))

			args = sys.argv[1:]
			i = 0
			while i < len(args):
				if args[i] == "set":
					self.do_set(args[i+1] + " " + args[i+2] + "!")
					i += 2
				else:
					self.onecmd(args[i])
					i += 1
			exit()

###############################################################################
# --- Settings -------------------------------------------------------------- #
###############################################################################
class Settings():
	def __init__(self):
		self.__setting_parameters = {}
		self.__tree = ET.parse("./settings.xml")
		self.__xml_settings = self.__tree.getroot()

		for p in self.__xml_settings:
			if p.attrib["type"] == "integer":
				self.__setting_parameters[p.attrib["name"]] = int(p.attrib["value"])
			else:
				self.__setting_parameters[p.attrib["name"]] = p.attrib["value"]

	def set(self, key, value, skip_flag):
		if key in self.__setting_parameters.keys():
			if self.__setting_parameters[key] != None and not skip_flag:
				while True:
					print("Are you sure you want to replace " + misc.color(str(self.__setting_parameters[key]), "magenta") + " by " + misc.color(value, "cyan") + "?")
					print(misc.underline("(Y)") + "es/" + misc.underline("(N)") + "o: ", end="")
					yn = input().upper()
					if yn == "N":
						return
					elif yn == "Y":
						break
			self.__update(key, value)
		else:
			print("error: unknown parameter")

	def __check_integer(self, v):
		try:
			v = int(v)
		except ValueError:
			print("Could not convert data to an integer")
			return
		return v

	def __check_folder(self, v):
		if len(v) == 0:
			print("Folder names cannot be an empty string")
			return
		for letter in v:
			if letter not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789":
				print("The character \"" + letter + "\" is forbidden for folder names")
				return
		return v

	def __check_file(self, v):
		if len(v) == 0:
			print("File names cannot be an empty string")
			return
		for letter in v:
			if letter not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789.":
				print("The character \"" + letter + "\" is forbidden for file names")
				return
		if len(v.split(".")) != 2:
			print("File name extension is missing or not valid")
			return
		return v

	def __check_path(self, v):
		if v[-1] != "/":
			print("A path must point to a directory and end by a \"" + misc.underline("/") + "\"")
			while True:
				print("Autocomplete? " + misc.color(v + "/", "cyan"))
				print(misc.underline("(Y)") + "es/" + misc.underline("(N)") + "o: ",  end="")
				yn = input()
				if yn == "N":
					return
				elif yn == "Y":
					v+= "/"
					break
		return v

	def get(self, key):
		if key in self.__setting_parameters.keys():
			return self.__setting_parameters[key]
		else:
			return "unknown"

	def display(self, key):
		if key == "all":
			for k in self.__setting_parameters.keys():
				tmp = "                          "
				print(misc.color(k, "cyan") + tmp[0:(26-len(k))] + ": " + str(self.__setting_parameters[k]))
		else:
			print(misc.color(key, "cyan") + ": " + str(self.get(key)))

	def __update(self, key, value):
		for p in self.__xml_settings:
			if p.attrib["name"] == key:
				if p.attrib["type"] == "integer":
					value = self.__check_integer(value)
				elif p.attrib["type"] == "folder":
					value = self.__check_folder(value)
				elif p.attrib["type"] == "file":
					value = self.__check_file(value)
				elif p.attrib["type"] == "path":
					value = self.__check_path(value)

				if value != None:
					p.set("value", str(value))
					self.__setting_parameters[key] = value



		self.__tree.write("settings.xml")

	def get_setting_parameters(self):
		return self.__setting_parameters


###############################################################################
# --- Path ------------------------------------------------------------------ #
###############################################################################
class Path():
	def __init__(self):
		self.__current_test_case = 0
		self.__current_test_artifact = 0
		self.__setting_parameters = SETTINGS.get_setting_parameters()

	def next_test_case(self):
		if self.__current_test_case < self.__setting_parameters["nb_test_cases"] - 1:
			self.__current_test_artifact = 0
			self.__current_test_case += 1
			return True
		return False

	def next_test_artifact(self):
		if self.__current_test_artifact < self.__setting_parameters["nb_test_artifacts"] - 1:
			self.__current_test_artifact +=1
			return True
		return False

	def next_path(self):
		if self.next_test_artifact():
			return True
		if self.next_test_case():
			return True
		self.reset_path()
		return False

	def reset_path(self):
		self.set_path(0, 0)

	def set_path(self, g, p):
		if 0 <= g < self.__setting_parameters["nb_test_cases"]:
			self.__current_test_case = g
		if 0 <= p < self.__setting_parameters["nb_test_artifacts"]:
			self.__current_test_artifact = p

	def check_path(self, auto, verbose):
		if not misc.check_folder(self.get_experiment_path()):
			while(True):
				if auto:
					yn = "Y"
				else:
					print("Create " + misc.color(self.get_experiment_path(), "cyan") + "?")
					print(misc.underline("(Y)") + "es/" + misc.underline("(N)") + "o: ", end="")
					yn = input().upper()
					#yn = "Y" #for experimentations
				if yn == "N":
					return
				elif yn == "Y":
					os.system("mkdir -p " + self.get_current_test_artifact_path())
					while self.next_path():
						os.system("mkdir -p " + self.get_current_test_artifact_path())
					break
			return True
		else:
			yall = False
			if auto:
				yall = True
			complete = True
			while True:
				if not misc.check_folder(self.get_current_test_artifact_path()):
					if yall:
						os.system("mkdir -p " + self.get_current_test_artifact_path())
						if verbose:
							print("Create " + misc.color(self.get_current_test_artifact_path(), "cyan"))
					else:
						while True:
							print("Create " + misc.color(self.get_current_test_artifact_path(), "cyan") + "?")
							print(misc.underline("(Y)") + "es/" + misc.underline("(N)") + "o - " + misc.underline("Yall") + "/" + misc.underline("Nall") + ": ", end="")
							yn = input().upper()
							if yn == "N":
								complete = False
								break
							elif yn == "Y":
								os.system("mkdir -p " + self.get_current_test_artifact_path())
								break
							elif yn == "YALL":
								os.system("mkdir -p " + self.get_current_test_artifact_path())
								yall = True
								break
							elif yn == "NALL":
								self.reset_path()
								return False

				if not self.next_path():
					return complete

	def get_experiment_path(self):
		return 	self.__setting_parameters["experiment_path"] +\
				self.__setting_parameters["experiment_folder_name"] + "/"

	def get_current_test_case_path(self):
		return self.get_experiment_path() + \
			   self.__setting_parameters["test_case_folder_name"] + "_" + str(self.__current_test_case) + "/"

	def get_current_test_case_nb(self):
		return self.__current_test_case

	def get_current_test_artifact_path(self):
		return self.get_current_test_case_path() + \
			   self.__setting_parameters["test_artifact_folder_name"] + "_" + str(self.__current_test_artifact) + "/"

	def get_current_test_artifact_nb(self):
		return self.__current_test_artifact


SETTINGS = Settings()
if __name__ == '__main__':
	CLI().cmdloop()
