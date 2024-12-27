import Taf
import shutil
import os

#delete the experiment folder
if os.path.exists('../experiment'):
    shutil.rmtree('../experiment')

#create the TAF object
cli=Taf.CLI()
#set parameters to remove GUI and manual validation for generate 
cli.verbose = False
cli.auto = True

#set the new template as "bmp.template"
cli.do_set("template_file_name bmp.template!")

#use TAF to parse and generate
cli.do_parse_template(cli)
cli.do_generate(cli)

os.system('xdg-open "../experiment"') #open the experiment folder