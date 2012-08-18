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

global_decls = []
pregcc = False
sanity_check = [False, False, False, False]
enum_counter = 0
language = None

# cython doesnt understand struct and const so we simply remove this
def gpxd_cleanup_function_params (decl):
     t = ('%s' % decl)
     parm = '%s' % decl
     s = ''
     idx = parm.find ('struct')
     idy = parm.find ('const')
     if re.search ("\(\*.*\)", t):
          if decl.name:
               s = '%s' % decl.name
          else:
               print decl.name
               print decl.type.type
               print decl.type
     elif (idx >= 0) or (idy >= 0):
          s = parm
          s = s.replace ('struct', '')
          s = s.replace ('const', '')
          # cleanup any early whitespace:
          ns = ''
          first = True
          for c in s:
               if first and not c.isalpha ():
                    first = False
                    continue
               else:
                    ns = ns + c
          s = ns
     else:
          s = parm
     return s

def gpxd_generate_function (fd, decl, indent):
     fndeclt = '%s' % type (decl.type)
     if fndeclt == "<type 'gcc.MethodType'>":
          # with C++ when generating methods as part of a class
          # example class foo : void mymethod (void)
          # the mymethod inherits the function sig
          # void mymethod (Foo *) so this-> works etc...
          # this means we ignore the first paramter.
          for i in range (indent):
               fd.write ("\t")
          fd.write ("%(retype)s %(ident)s (" % \
                         { "retype": gpxd_cleanup_function_params \
                                (decl.type.type), "ident": decl.name})
          if len (decl.type.argument_types) > 0:
               count = 0
               for i in decl.type.argument_types:
                    if count >= 1:
                         s = gpxd_cleanup_function_params (i)
                         fd.write (s)
                         if count < (len (decl.type.argument_types) - 1):
                              fd.write (", ")
                    count = count + 1
          fd.write (")\n")    
     else:
          for i in range (indent):
               fd.write ("\t")
          fd.write ("%(retype)s %(ident)s (" % \
                         { "retype": gpxd_cleanup_function_params \
                                (decl.type.type), "ident": decl.name})
          if len (decl.type.argument_types) > 0:
               count = 0
               for i in decl.type.argument_types:
                    s = gpxd_cleanup_function_params (i)
                    fd.write (s)
                    if count < (len (decl.type.argument_types) - 1):
                         fd.write (", ")
                    count = count + 1
          fd.write (")\n")

def gpxd_generate_typedef_simple_types (fd, decl, indent):
     t = ('%s' % decl.type)
     if re.search ("\(\*.*\)", t):
          for i in range (indent):
               fd.write ("\t")
          fd.write ("ctypedef %(retype)s (*%(name)s) (" \
                         % { "retype": decl.type.type.type, \
                                  "name": decl.type.name})
          if len (decl.type.type.argument_types):
               count = 0
               for i in decl.type.type.argument_types:
                    s = gpxd_cleanup_function_params (i)
                    fd.write (s)
                    if count < (len (decl.type.type.argument_types) - 1):
                         fd.write (", ")
                    count = count + 1
          fd.write (")\n")
     # typedefs are annoying...
     elif ('%s' % type (decl.type)) == "<type 'gcc.IntegerType'>":
          ident = '%s' % decl
          fd.write ("\tctypedef int %s\n" % ident)
     elif ('%s' % type (decl.type)) == "<type 'gcc.PointerType'>":
          fd.write ("\tctypedef %(ptr)s %(ident)s\n" % \
                         { "ptr" : decl.type, \
                                "ident" : decl.name })
     # we need to add in all the other possible types here... 

def gpxd_generate_union (fd, decl, indent):
     for i in range (indent):
          fd.write ("\t")
     name = '%s' % decl.name
     if name == 'None':
          print "WARNING: union with no name"
          name = "<noname>"
     fd.write ("cdef union %(name)s:\n" % \
                    {'name':name})
     for field in decl.type.fields:
          gpxd_generate_field (fd, field, indent + 1)

def gpxd_generate_field (fd, decl, indent):
     decltype = '%s' % type (decl.type)
     if decltype == "<type 'gcc.UnionType'>":
          name = '%s' % decl.name
          if name != 'None':
               for i in range (indent):
                    fd.write ("\t")
               fd.write ("union %s:\n" % name)
               for field in decl.type.fields:
                    gpxd_generate_field (fd, field, indent + 1)
     else:
          for i in range (indent):
               fd.write ("\t") 
          fd.write ("%(type)s %(id)s\n" % { \
                    "type": gpxd_cleanup_function_params (decl.type),\
                         "id":decl.name })

def gpxd_generate_type (fd, decl, indent):
    gpxd_generate_typedef_simple_types (fd, decl, indent)
    decltype = '%s' % type (decl.type)
    if ('%s' % type (decl.type)) == "<type 'gcc.RecordType'>":
         if len (decl.type.methods) > 0:
              for i in range (indent):
                   fd.write ("\t")
              fd.write ("cdef cppclass %(name)s:\n" % \
                             { 'name': decl.type.name })
              if len (decl.type.fields) == 0:
                   for i in range (indent + 1):
                        fd.write ("\t")
                   fd.write ("pass\n")
              else:
                   for field in decl.type.fields:
                        declt = '%s' % type (field)
                        if declt == "<type 'gcc.TypeDecl'>":
                             continue
                        gpxd_generate_field (fd, field, indent + 1)
              for method in decl.type.methods:
                   gpxd_generate_function (fd, method, indent + 1)
         else:
              for i in range (indent):
                   fd.write ("\t")
              fd.write ("cdef struct %(name)s:\n" % \
                             { 'name': decl.type.name })
              if len (decl.type.fields) == 0:
                   for i in range (indent + 1):
                        fd.write ("\t")
                   fd.write ("pass\n")
              else:
                   for field in decl.type.fields:
                        declt = '%s' % type (field)
                        if declt == "<type 'gcc.TypeDecl'>":
                             continue
                        gpxd_generate_field (fd, field, indent + 1)
    elif decltype == "<type 'gcc.UnionType'>":
         gpxd_generate_union (fd, decl, indent)

def gpxd_generate_decl (fd, decl, indent):
     decltype = '%s' % type (decl)
     if decltype == "<type \'gcc.TypeDecl\'>":
          gpxd_generate_type (fd, decl, indent)
          fd.write ("\n")
     elif decltype == "<type \'gcc.NamespaceDecl\'>":
          for x in range (indent):
               fd.write ("\t")
          fd.write ("cdef namespace \"%(namespaceid)s\":\n" \
                         % { 'namespaceid': decl.name})
          for i in decl.declarations:
               gpxd_generate_decl (fd, i, indent + 1)
          fd.write ("\n")
     elif decltype == "<type \'gcc.FunctionDecl\'>":
          gpxd_generate_function (fd, decl, indent)
          fd.write ("\n")
     elif decltype == "<type 'gcc.VarDecl'>":
          tt = '%s' % type (decl.type)
          if tt != "<type 'gcc.RecordType'>":
               gpxd_generate_decl (fd, decl.type, indent)
          init = '%s' % decl.initial
          if init != 'None':
               for i in range (indent):
                    fd.write ("\t")
               fd.write ("%(type)s %(id)s\n" % {'type':decl.type,\
                                                     'id':decl.name})

def gpxd_generate_cxx (decls, out, headers):
     header_dict = []
     for h in headers:
          # lets cleanup the ordering of decls so functions
          # are the last in the list
          newdecls = []
          fndecls = []
          for d in decls:
               t = '%s'  % type (d)
               if t == "<type \'gcc.FunctionDecl\'>":
                    fndecls.append (d)
               else:
                    newdecls.append (d)
          for f in fndecls:
               newdecls.append (f)
          decls = newdecls
          cpp = PyCppParser (h)
          macros = cpp.parse_macros ()
          cpp.parser_close ()
          entry = { 'HEADER':h, 'DECLS':[], 'MACROS':[] }
          entry['MACROS'] = macros['DEFINE']
          for decl in decls:
               loc = ('%r' % decl.location)
               if loc.find (h) > -1:
                    entry['DECLS'].append (decl)
          header_dict.append (entry)
     fd = open (out, "w")
     for header in header_dict:
          header_context = ('cdef extern from \"%(header)s\":\n'\
              % { 'header' : header['HEADER'] })
          fd.write (header_context)
          for decl in header['DECLS']:
               gpxd_generate_decl (fd, decl, 1)
          if len (header['MACROS']) > 0:
               fd.write ("\n\'\'\'\n")
               for macro in header['MACROS']:
                    fd.write ('%(macro)s\n' % {'macro':macro})
               fd.write ("\'\'\'\n")
     fd.close ()

def gpxd_on_pass_execution (p, fn):
     global language, global_decls
     namespaces = []
     decls = []
     if p.name == '*free_lang_data':
          if not sanity_check[0]:
               for u in gcc.get_translation_units ():
                    language = u.language
                    if u.language == 'GNU C++':
                         gns = gcc.get_global_namespace ()
                         for ns in gns.namespaces:
                              if ns.is_builtin == False:
                                   namespaces.append (ns)
                         for decl in gns.declarations:
                              found = False
                              if (decl.is_builtin == False):
                                   for ns in namespaces:
                                        for i in ns.declarations:
                                             if i == decl:
                                                  found = True
                                   if found == False:
                                        if decl.name != 'main':
                                             decls.append (decl)
                         for i in namespaces:
                              global_decls.append (i)
                         for i in decls:
                              global_decls.append (i)
                    else:
                         for decl in u.block.vars:
                              if pregcc:
                                   global_decls.append (decl)
                              else:
                                   found = False
                                   for x in global_decls:
                                        if x == decl:
                                             found = True
                                   if not found:
                                        global_decls.append (decl)
                         sanity_check[1] = True
               sanity_check[0] = True
     if sanity_check[0] and sanity_check[1] and not sanity_check[2]:
          sanity_check[2] = True
          gpxd_generate_cxx (global_decls, output, headers)

def on_finish_decl(*args):
     decl = args[0]
     if decl.is_builtin == False:
          global_decls.append (decl)
     sanity_check[1] = True

gcc.register_callback(gcc.PLUGIN_PASS_EXECUTION, gpxd_on_pass_execution)

# Hook for GCC 4.7 and later:
if hasattr(gcc, 'PLUGIN_FINISH_DECL'):
    gcc.register_callback(gcc.PLUGIN_FINISH_DECL, on_finish_decl)
else:
     pregcc = True
