import gcc
import re
from pprint import pformat
from gccutils import get_src_for_loc, cfg_to_dot, invoke_dot

decls = []

def decl_location_get_file (decl):
    repr = ('%r' % decl.location)
    idx = repr.index ('file=')
    idy = repr.index ('line=')
    file_string = ""
    for i in range (idx+6, idy-3):
        file_string += repr[i]
    return file_string

def generate_pxd_decl_function (fd, decl):
    fmt = "%s" % decl.type
    ident = '%s' % decl
    if re.search ("<.*>", fmt):
        func = re.sub ("<.*>", ident, fmt)
        fd.write ("cdef extern from \"%s\":\n" % decl_location_get_file (decls[0]))
        fd.write ('\t%s\n' % func)

def decl_identifier_node_to_string (node):
    repr = ('%r' % node)
    idx = repr.index ('name=')
    idy = repr.index (')')
    retval = ""
    for i in range (idx+6, idy-1):
        retval += repr [i]
    return retval

def generate_pxd_decl_type (fd, decl):
    if ('%s' % type (decl.type)) == "<type 'gcc.RecordType'>":
        ident = decl_identifier_node_to_string (decl.type.name)
        fd.write ("\tctypedef struct %s:\n" % ident)
        for f in decl.type.fields:
            fd.write ("\t\t%s %s\n" % (f.type, f.name))

def generate_pxd_data (T, fd, decl):
    if T == "<type 'gcc.FunctionDecl'>":
        return generate_pxd_decl_function (fd, decl)
    elif T == "<type 'gcc.TypeDecl'>":
        return generate_pxd_decl_type (fd, decl)
    else:
        print "unhandled type <%s>!\n" % T

def walk_generate_pxd_decls ():
    if len (decls) > 0:
        fd = open ('out.pxd', 'w')
        for decl in decls:
            print('%r:%s:%s' % (decl.location, decl, decl.type)) 
            decl_type = '%s' % type (decl)
            generate_pxd_data (decl_type, fd, decl)
            fd.write ("\n")
        fd.close ()
        
def on_pass_execution (p, fn):
    if p.name == '*free_lang_data':
        for u in gcc.get_translation_units ():
            for decl in u.block.vars:
                f = decl_location_get_file (decl)
                if f != '<built-in>':
                    decls.append (decl)
        walk_generate_pxd_decls ()

gcc.register_callback (gcc.PLUGIN_PASS_EXECUTION, on_pass_execution)
