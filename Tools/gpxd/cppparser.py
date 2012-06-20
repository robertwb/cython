import sys

class CppParser:
    fd = source = data = p = None
    TOKEN_DATA = None
    TOKEN_STATE = { 'POUND':True, 'ID':False, 'EOF':False }

    def __init__ (self, infile):
        self.source = infile
        self.fd = open (self.source, 'r')

    def parser_close (self):
        self.fd.close ()

    def parse_lexme (self):
        c = data[p]
        p++
        if c == '#':
            TOKEN_STATE['POUND'] = True
            TOKEN_DATA = c
            
            

    def parse_macros (self):
        self.data = self.fd.read ()
        self.p = 0
            
def cppmain (source):
    print "parsing: ", source
    parser = CppParser (source)
    macros = parser.parse_macros ()
    parser.parser_close ()
    
if __name__== "__main__":
    if len (sys.argv) > 1:
        cppmain (sys.argv[1])
