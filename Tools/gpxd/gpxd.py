#!/usr/bin/env python

# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Cython Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Author Philip Herron <redbrain@gcc.gnu.org>

from gccpxd import config
from config import gccpython, output, headers, \
    keep_generated_files, compiler, lang, debug
from subprocess import Popen, PIPE
import sys

def debug (msg):
    if debug:
        print "DEBUG: %s" % msg

def fatal (msg):
    print "FATAL: %s" % msg
    sys.exit (1)

__GEN_FILE = None
if lang == "c":
    __GEN_FILE = "__gpxd.c"
elif lang == "c++":
    __GEN_FILE = "__gpxd.cc"
else:
    fatal ("Invalid language selection")

def generate_source_file ():
    fd = open (__GEN_FILE ,'w')
    for i in headers:
        data = ("#include \"%s\"\n" % i)
        fd.write (data)
    fd.write ("\nint main (void) { return 0; }\n")
    return fd

def run_gcc_pxd ():
    if debug:
        cmd = ('%(compiler)s --version' % { "compiler": compiler })
        debug ("executing <%s>" % cmd)
        pipe = Popen (cmd, shell = True)
        if pipe.wait () != 0:
            fatal ("There were some errors running gcc")
    # now to run the tool
    cmd = (('%(compiler)s -fplugin=%(plugin_path)s -fplugin-arg-python-script=\"' \
                + './gccpxd/gccpxd.py\" -O0 -c %(gen_path)s') % \
               { "compiler": compiler, "plugin_path" : gccpython, "gen_path" \
                     :__GEN_FILE })
    debug ("executing <%s>" % cmd)
    pipe = Popen (cmd, shell = True)
    if pipe.wait () != 0:
        fatal ("There were some errors running gcc")

def main ():
    fd = generate_source_file ()
    assert fd
    fd.close ()
    run_gcc_pxd ()
    if not keep_generated_files:
        pass # delete the file 

if __name__== "__main__":
    main ()
