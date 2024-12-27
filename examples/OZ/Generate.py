#Add TAF path to system
#import sys
#sys.path.append('path_to_taf/src')

import Taf
import time

#instanciate a TAF Client
myTaf = Taf.CLI()
#myTaf.verbose = False

# calls to Taf functions
#myTaf.do_overwrite(None)
myTaf.do_parse_template()
start = time.time()
myTaf.do_generate()
end = time.time()

print("global_times: " + str(end-start))