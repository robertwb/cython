import sys

class PyCppParser:
    fd = source = data = p = None
    _OPEN = False
    TOKEN_STATE = { 'POUND':False, 'DEFINE':False, 'ENDIF':False,
                    'IFDEF':False, 'ID':False, 'EOF':False }

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
    
    def PyCppLex (self):
        TOKEN = None
        while self.p <= len (self.data):
            if self.p >= len (self.data):
                TOKEN = 'EOF'
                self.TOKEN_STATE[TOKEN] = True
                break
            elif self.data[self.p] == '#':
                TOKEN = 'POUND'
                self.TOKEN_STATE[TOKEN] = self.data[self.p]
                self.parser_pointer_incr ()
                break
            elif self.data[self.p] == 'd':
                string = self.data[self.p]
                self.parser_pointer_incr ()
                while self.cppID_valid (self.data[self.p]):
                    string += self.data[self.p]
                    self.parser_pointer_incr ()
                if string == 'define':
                    TOKEN = 'DEFINE'
                    self.TOKEN_STATE[TOKEN] = True
                elif string == 'defined':
                    TOKEN == 'DEFINED'
                    self.TOKEN_STATE[TOKEN] = True
                else:
                    TOKEN = 'ID'
                    self.TOKEN_STATE[TOKEN] = True
                break
            elif self.data[self.p] == 'i':
                string = self.data[self.p]
                self.parser_pointer_incr ()
                while self.cppID_valid (self.data[self.p]):
                    string += self.data[self.p]
                    self.parser_pointer_incr ()
                if string == 'include':
                    TOKEN = 'INCLUDE'
                    self.TOKEN_STATE[TOKEN] = True
                elif string == 'if':
                    TOKEN = 'IF'
                    self.TOKEN_STATE[TOKEN] = True
                elif string == 'ifdef':
                    TOKEN = 'IFDEF'
                    self.TOKEN_STATE[TOKEN] = True
                else:
                    TOKEN = 'ID'
                    self.TOKEN_STATE[TOKEN] = True
                break
            elif self.data[self.p] == 'e':
                string = self.data[self.p]
                self.parser_pointer_incr ()
                while self.cppID_valid (self.data[self.p]):
                    string += self.data[self.p]
                    self.parser_pointer_incr ()
                if string == 'endif':
                    TOKEN = 'ENDIF'
                    self.TOKEN_STATE[TOKEN] = True
                else:
                    TOKEN = 'ID'
                    self.TOKEN_STATE[TOKEN] = True
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

    def PyCppLexNextChar (self):
        c = None
        if self.p <= len (self.data):
            c = self.data[self.p]
            self.parser_pointer_incr ()
        return c

    def PyCppLexDefintion (self):
        run = False
        definition = c = self.PyCppLexNextChar ()
        while c != None:
            if c == '\\':
                run = True
            if c == '\n':
                if run == False:
                    break
                run = False
            definition += c
            c = self.PyCppLexNextChar ()
        return definition
    
    def PyCppParse (self):
        MACROS = { 'DEFINE':[], 'INCLUDE':[], 'CONDITIONAL':[] }
        token = self.PyCppLex ()
        while token != 'EOF':
            if token == 'POUND':
                token = self.PyCppLex ()
                if token == 'DEFINE':
                    definition = self.PyCppLexDefintion ()
                    MACROS[token].append (definition)
                # parse include / idefs....
            token = self.PyCppLex ()
        return MACROS
    
    def parse_macros (self):
        if self._OPEN == True:
            self.data = self.fd.read ()
            self.parser_pointer_reset ()
            return self.PyCppParse ()

def pycppmain (source):
    print "parsing: ", source
    parser = PyCppParser (source)
    macros = parser.parse_macros ()
    parser.parser_close ()
    
if __name__== "__main__":
    if len (sys.argv) > 1:
        pycppmain (sys.argv[1])
