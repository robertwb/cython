import sys

class CppParser:
    fd = source = data = p = None
    _OPEN = False
    TOKEN_STATE = { 'POUND':False, 'ID':False, 'EOF':False }

    def __init__ (self, infile):
        self.source = infile
        self.fd = open (self.source, 'r')
        self._OPEN = True
    
    def parser_close (self):
        if self._OPEN:
            self.fd.close ()
            self._OPEN = False
    
    def parser_pointer_incr (self):
        if self.p < len (self.data):
            self.p = self.p + 1
    
    def parser_pointer_decr (self):
        if self.p > 0:
            self.p = self.p - 1

    def parser_pointer_reset (self):
        self.p = 0

    def cppID_begin_valid (self, c):
        if c.isalpha () or c == '_':
            return True
        else:
            return False

    def cppID_valid (self, c):
        if c.isalpha () or c == '_' or c.isdigit ():
            return True
        else:
            return False
    
    def cppLex (self):
        TOKEN = None
        while self.p <= len (self.data):
            if self.p >= len (self.data):
                self.TOKEN_STATE['EOF'] = True
                TOKEN = 'EOF'
                break
            elif self.data[self.p] == '#':
                self.TOKEN_STATE['POUND'] = self.data[self.p]
                TOKEN = 'POUND'
                self.parser_pointer_incr ()
                break
            elif self.cppID_begin_valid (self.data[self.p]):
                identifier = self.data[self.p]
                self.parser_pointer_incr ()
                while self.cppID_valid (self.data[self.p]):
                    identifier += self.data[self.p]
                    self.parser_pointer_incr ()
                self.TOKEN_STATE['ID'] = identifier
                TOKEN = 'ID'
                break
            else:
                self.parser_pointer_incr ()
        return TOKEN
    
    def cppParse (self):
        t = self.cppLex ()
        while t != 'EOF':
            print t
            if t == 'ID':
                print self.TOKEN_STATE[t]
            t = self.cppLex ()
    
    def parse_macros (self):
        if self._OPEN == True:
            self.data = self.fd.read ()
            self.parser_pointer_reset ()
            self.cppParse ()

def cppmain (source):
    print "parsing: ", source
    parser = CppParser (source)
    macros = parser.parse_macros ()
    parser.parser_close ()
    
if __name__== "__main__":
    if len (sys.argv) > 1:
        cppmain (sys.argv[1])
