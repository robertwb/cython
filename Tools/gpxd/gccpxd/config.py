# Config parameters for the pxd generation tool

output = "test.pxd" # output file name/location

headers = [ "t.h" ] # full path headers to work on

gccpython = "/home/redbrain/workspace/gcc-python-plugin/python.so"
# location of python.so can be found via: gcc --print-file-name=plugin
# if you make install from gcc or if you use the local build in the gcc-python-plugin

keep_generated_files = False # keep the generated lang file

compiler = "gcc" # Compiler to use

lang = "c" # language supported ones { "c", "c++" .... }

debug = True # Verbose debuging information
