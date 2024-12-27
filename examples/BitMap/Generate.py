#Add TAF path to system
#import sys
#sys.path.append('/Users/guiochet/BOULOT/RECHERCHE/Dev-info/temp/taf/src')

import Taf

#instanciate a TAF Client
myTaf = Taf.CLI()

# calls to Taf functions
# myTaf.do_overwrite(None)
myTaf.do_parse_template()
myTaf.do_generate()