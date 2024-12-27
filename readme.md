--- TAF: Testing Automation Framework ---
===============================

The purpose of TAF is to generate random test cases from a template, test model file (.xml) describing the data model of the system under test. TAF provides a command line interface 
When launched using command line interface, type "help" in the prompt to get a list of the available commands.
Type "help <command_name>" to get specific info on a command.
TAF can also be used as a python library, please refer to the user manual for installation.

Requirements:
-----------
 * Python 3.6
Packages:
 * Numpy 1.18.4
 * z3-solver 4.8.8.0

Installation:
-----------
Please refer to docs/TAF_USer_Manual


 Typical usage (Command Line Interface):
-----------

```
cd path/TAF/src
python3 Taf.py         %launch TAF
display all            %visualize the settings
parse_template         %parse the template
generate               %generate test cases
cat ../experiment/test_case_0/test_case_0.test_case %visualize the result
```

To change the default example (square) to another one:
- copy/paste the .template file from "examples/xxxExample/", into the "example" folder
- copy/paste the .export (Export.py) file from "examples/xxxExample/" into the "src" folder
- restart TAF

 Typical usage (Python Library):
-----------
Once you've installed TAF (see User Manual)
- got to "examples/xxxExample/" folder
- run the python script "Generate.py"


Contents of the repository:
-----------

 1. src: the source code and the default settings
 2. examples : Examples of templates and export files
 3. docs: Documentation and User Manual



This software is released under CeCILL-B license (similar to BSD, without copyleft)
with Copyright 2019.
 ______

		                 ______			
	        	         /     /\
		               /     /##\
		              /     /####\
	        	      /     /######\
		            /     /########\
		           /     /##########\
	        	   /     /#####/\#####\
		         /     /#####/++\#####\
		        /     /#####/++++\#####\
		       /     /#####/\+++++\#####\
		      /     /#####/  \+++++\#####\
		     /     /#####/    \+++++\#####\
		    /     /#####/      \+++++\#####\		
		   /     /#####/        \+++++\#####\
		  /     /#####/__________\+++++\#####\
		 /                        \+++++\#####\
		/__________________________\+++++\####/
		\+++++++++++++++++++++++++++++++++\##/
		 \+++++++++++++++++++++++++++++++++\/
		  ``````````````````````````````````
