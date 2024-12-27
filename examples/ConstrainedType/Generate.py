#import sys
#sys.path.append('path_to_taf/src')

import Taf
import time

start = time.time()

myTaf = Taf.CLI()
# myTaf.do_display("all")
# myTaf.help_parse_template()
# myTaf.do_overwrite(None)
myTaf.do_parse_template()
myTaf.do_generate()

end = time.time()
with open("time", "a") as f:
	f.write(str(end-start) + "\n")
	print("time: " + str(end-start))