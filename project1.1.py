#Alexander Starr
#22C:016:A01
#00567613

keychars = ["r","-","+","d","s","x","m","a","o"]

def driver(filename):
    # "Drives" the program.  Takes a filename, opens and reads the file.
    f = open(filename, "r")
    in_stanza = False
    line = f.readline()
    while line:
        # While line is non-empty, the program will trim new-line characters,
        # then determine if the line is instructions, encrypted text, or
        # the end of a stanza.  It will then direct flow based on this.
        tline = line[0:len(line)-1]
        if in_stanza:
            # If in_stanza == True, then the current line is either encrypted
            # text, or it is a blank line, which signals the end of the stanza.
            # So we must test and see if there are non-space characters.
            # If there are, then we are still in a stanza, and must decrypt
            # the line (which is handled by the function decrypt_text).
            line_is_blank = True
            for char in tline:
                if char != " ":
                    line_is_blank = False
            if line_is_blank:
                in_stanza = False
            else:
                print decrypt_text(tline, instructions)
        else:
            # If in_stanza == False, then the next line contains instructions.
            # Just in case, the program checks for a keychar in tline,
            # to make sure it isn't blank or something silly.
            for keychar in keychars:
                if keychar in tline:
                    instructions = parse_instructions(tline)
                    #print instructions  # Debug statement
                    in_stanza = True
                    break
        line = f.readline()
    f.close()
    
def parse_instructions(s):
    # Breaks instruction lines up into a list of instructions and parameters.
    # Then returns this list.
    i = []
    index = 0
    while index < len(s):
        # Runs through the string, looking for key characters.
        # When it encounters one, it picks apart the parameters to store in i.
        if s[index] == "-" or s[index] == "+":
            # + and - work exactly the same, so why code it twice?
            # This just adds the appropriate instruction to i, builds the
            # digit following it, and then adds that digit to i.
            i.append(s[index])
            digit = ""
            while index != len(s) - 1 and 48 <= ord(s[index + 1]) <= 57:
                # Whenever the next character is a digit within bounds of s, 
                # it will add that digit and advance the index of 
                # the instruction string.
                index = index + 1
                digit = digit + s[index]
            i.append(int(digit))
        index = index + 1
    return i

def decrypt_text(s, i):
    # Receives a single line as a string s, and the instruction list i.
    # Performs the instructions in the proper order on that string.
    # Then returns the string.
    index = 0
    while index < len(i):
        if i[index] == "-" or i[index] == "+":
            # If the instruction is "-" or "+", then the next digit is
            # the magnitude of the shift.  This passes the string s and
            # the magnitude (as well as direction) of the shift to the function.
            shift_by = i[index + 1]
            if i[index] == "-":
                # Changes direction if necessary.
                shift_by = -shift_by
            s = shift(s, shift_by)
            index = index + 1
        index = index + 1
    return s

def shift(string, n):
    # Returns a new string that is equivalent to the argument string
    # shifted by n ASCII values, where n may be a positive or negative int.
    shifted_string = ""
    for char in string:
        # The character must be converted to its ASCII value, then shifted
        # by -32.  At this point, the value must be between 0 and 94, inclusive.
        # Then this value is shifted by n, using arithmetic mod 95.
        # Then the value is shifted back +32, converted to a character,
        # and concatenated to the end of shifted_string.
        value = ord(char) - 32
        value = (value + n) % 95
        value = value + 32
        shifted_char = chr(value)
        shifted_string = shifted_string + shifted_char
    return shifted_string