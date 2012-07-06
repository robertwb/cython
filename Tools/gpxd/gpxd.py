from pycpp import PyCppParser
import gcc
import re
import inspect
from gccutils import get_src_for_loc, cfg_to_dot, invoke_dot

function_decls = []
block_decls = []
sanity_check = [False, False, False]
headers = [ "t.h" ]
outpxd = "test.pxd"

def gpxd_generate (fdecls, bdecls, out, headers):
    header_dict = { }
    header_macros = [ ]
    for h in headers:
        cpp = PyCppParser (h)
        header_macros.append (cpp.parse_macros ())
        cpp.parser_close ()
    for h in headers:
        for i in fdecls:
            loc = i.decl.location
            print loc
    fd = open (out, 'w')
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
    if p.name == '*warn_unused_result':
        function_decls.append (fn)
        sanity_check[0] = True
    elif p.name == '*rest_of_compilation':
        print '#######'
        print fn
        print '#######'
    elif p.name == '*free_lang_data':
        if not sanity_check[1]:
            for u in gcc.get_translation_units ():
                for decl in u.block.vars:
                    block_decls.append (decl)
            sanity_check[1] = True
    if sanity_check[0] and sanity_check[1] and not sanity_check[2]:
        sanity_check[2] = True
        block_decls = gpxd_cleanup_decls (block_decls, headers)
        gpxd_generate (function_decls, block_decls, outpxd, headers)

gcc.register_callback(gcc.PLUGIN_PASS_EXECUTION, gpxd_on_pass_execution)
