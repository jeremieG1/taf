#Add TAF path to system
#import sys
#sys.path.append('path_to_taf/src')

import Taf

#instanciate a TAF Client
myTaf = Taf.CLI()

# calls to Taf functions
#myTaf.do_overwrite(None)
myTaf.do_parse_template()
myTaf.do_generate()