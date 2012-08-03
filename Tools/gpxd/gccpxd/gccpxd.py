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

import sys, os, re
import gcc

# work around for having python.so outside of your working dir
# otherwise these next imports fail
sys.path.append (os.getcwd ()  + "/gccpxd")

from gpycpp import PyCppParser
from config import output, headers

function_decls = []
block_decls = []
global_decls = None
sanity_check = [False, False, False, False]
enum_counter = 0

def gpxd_generate_function (fd, decl):
    fmt = "%s" % decl.type
    ident = '%s' % decl
    if re.search ("<.*>", fmt):
        func = re.sub ("<.*>", ident, fmt)
        fd.write ('\t%s\n' % func)

def gpxd_generate_type (fd, decl):
    global enum_counter
    # print "%s" % type (decl.type)
    if ('%s' % type (decl.type)) == "<type 'gcc.RecordType'>":
        ident = '%s' % decl
        print ident
        fd.write ("\tctypedef struct %s:\n" % ident)
        for f in decl.type.fields:
            if ('%s' % type (f.type)) == "<type 'gcc.UnionType'>":
                uid = '%s' % f
                fd.write ("\t\tcdef union %s:\n" % uid)
                for x in f.type.fields:
                    fd.write ("\t\t\t%s %s\n" % (x.type, x.name))
            else:
                fd.write ("\t\t%s %s\n" % (f.type, f.name))
    elif ('%s' % type (decl.type)) == "<type 'gcc.EnumeralType'>":
        ident = '%s' % decl
        if 'struct' in ident:
            enum_counter = 1
            fd.write ('\tcdef enum %s:\n' % ident)
        else:
            fd.write ("\t\t%s = %i\n" % (ident, enum_counter))
            enum_counter = enum_counter + 1
    elif ('%s' % type (decl.type)) == "<type 'gcc.UnionType'>":
        ident = '%s' % decl
        if ident == "unionunion":
            fd.write ("\tcdef union %s:\n" % ident)
            for f in decl.type.fields:
                fd.write ("\t\t%s %s\n" % (f.type, f.name))

def gpxd_generate (fdecls, bdecls, out, headers):
    header_dict = { }
    for h in headers:
        header_dict[h] = { 'FUNCTIONS':[], 'TYPES':[], 'MACROS':[] }
        cpp = PyCppParser (h)
        header_dict[h]['MACROS'] = cpp.parse_macros ()
        cpp.parser_close ()
        for i in fdecls:
            loc = ('%r' % i.location)
            if h in loc:
                header_data = header_dict[h]
                header_data['FUNCTIONS'].append (i)
        for i in bdecls:
            loc = ('%r' % i.location)
            if h in loc:
                header_data = header_dict[h]
                header_data['TYPES'].append (i)
    fd = open (out, 'w')
    for i in header_dict:
        fd.write ("cdef extern from \"%s\":\n" % i)
        header_data = header_dict[i]
        funcs = header_data['FUNCTIONS']
        typesd = header_data['TYPES']
        macros = header_data['MACROS']
        for j in typesd:
            gpxd_generate_type (fd, j)
        fd.write ("\n")
        for j in funcs:
            gpxd_generate_function (fd, j)
        fd.write ("\n")
        if len (macros['DEFINE']) > 0:
            fd.write ("\'\'\'\n")
            for j in macros['DEFINE']:
                fd.write (j)
                fd.write ("\n")
            fd.write ("\n\'\'\'\n")
        fd.write ("\n")
    fd.close ()
    
def gpxd_cleanup_decls (decls, hlist):
    newdecls = []
    for i in decls:
        for h in hlist:
            loc = ('%r' % i.location)
            if loc.find (h) > -1:
                newdecls.append (i)
                break
    return newdecls

def gpxd_on_pass_execution(p, fn):
    global function_decls, block_decls, sanity_check
    if p.name == '*free_lang_data':
        if not sanity_check[0]:
            for u in gcc.get_translation_units ():
                for decl in u.block.vars:
                    block_decls.append (decl)
            sanity_check[0] = True
    if sanity_check[0] and sanity_check[1] and not sanity_check[2]:
        sanity_check[2] = True
        block_decls = gpxd_cleanup_decls (block_decls, headers)
        gpxd_generate (function_decls, block_decls, output, headers)

def on_finish_decl(*args):
    global global_decls
    global_decls = args
    decl = args[0]
    if isinstance (decl, gcc.FunctionDecl):
        function_decls.append (decl)
    sanity_check[1] = True

gcc.register_callback(gcc.PLUGIN_PASS_EXECUTION, gpxd_on_pass_execution)

# Hook for GCC 4.7 and later:
if hasattr(gcc, 'PLUGIN_FINISH_DECL'):
    gcc.register_callback(gcc.PLUGIN_FINISH_DECL, on_finish_decl)
