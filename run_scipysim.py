#!/usr/bin/env python
'''
A launch script that should work on windows too.

Runs scipysim, either by executing a specified
model, or in the absence of a model by starting
the scipysim GUI.
'''

from runpy import run_module
from optparse import OptionParser

import scipysim

def main(modelname=None):
    if modelname is None:
        print "Starting scipysim GUI"
        run_module('scipysim.gui.gui')
    else:
        # TODO: Check if modelname is valid
        run_module('scipysim.models.' + modelname)

def test(verbose=False):
    print "Running tests (requires nose)"
    import nose
    nose.run()

if __name__ == "__main__":
    usage = "usage: %prog [options] [modelname]"
    parser = OptionParser(usage=usage)
    parser.add_option('--test', '-t', help="Run tests", action = "store_true")
    parser.add_option('--list', '-l', help="List scipy-sim models", action = "store_true")
    (options, args) = parser.parse_args()
    
    if options.test:
        test()
    
    if options.list:
        print "TODO: Import codegroup from scipysim.core"
    else:
        model = (len(args) > 0) and [args[0]][0] or None
        print "model = ", model
        main(model)

