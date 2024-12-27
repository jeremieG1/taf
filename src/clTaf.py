import shutil
import os
from os.path import basename
from pathlib import Path

#set the new template
for txt_path in Path("../templates").glob("*.template"):
    templ=basename(txt_path)
os.system("python3 Taf.py set template_file_name {}".format(templ))

#check of the export and the template files from the user
test=str(input('Does the export file is in the "src" folder and does the template \
file associated is in the "templates" folder ? \nYes/No (y/n):'))

if test.upper()=='Y':
    #delete the older experiment folder
    if os.path.exists('../experiment'):
        shutil.rmtree('../experiment')

#use TAF without the GUI, directly from this python file
    os.system("python3 Taf.py silent overwrite parse_template generate")
    os.system('xdg-open ../experiment') #open the experiment folder
else :
    print('Please make sure all is good before start TAF.')  
                                                                      