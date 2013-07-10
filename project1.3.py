#Alexander Starr
#22C:016:A01
#00567613

def driver(filename):
    # "Drives" the program.  Takes a filename, opens and reads the file.
    f = open(filename, "r")
    in_stanza = False
    line = f.readline()
    while line:
        # While line is non-empty, the program will trim new-line characters,
        # then determine if the line is instructions, encrypted text, or
        # the end of a stanza.  It will then direct flow based on this.
        tline = trim_line(line)
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
            for keychar in ["r","-","+","d","s","x","m","a","o"]:
                if keychar in tline:
                    instructions = parse_instructions(tline)
                    #print instructions  # Debug statement
                    in_stanza = True
                    break
        line = f.readline()
    f.close()
    
def trim_line(line):
    chars_to_trim = 1
    if line[len(line)-2] in ['\n','\r']:
        chars_to_trim = chars_to_trim + 1
    tline = line[:-chars_to_trim]
    return tline
        
    
# Breaks instruction lines up into a list of instruction lists.
# Each instruction is its own list, with element 0 being the instruction
# and the following elements being the parameters.
# It then returns this list.
def parse_instructions(s):
    instructions = []
    index = 0
    while index < len(s):
        # Runs through the string, looking for key characters.
        # When it encounters one, it picks apart the parameters to store in i.
        if s[index] in ["-", "+"]:
            # If it finds the instruction + or -, it builds the trailing digit.
            digit, index = build_num(s, index)
            instructions.append(["+", digit])
        elif s[index] == "r":
            instructions.append(["r"])
        elif s[index] == "d":
            # If the instruction is d, and the following character is a number,
            # then we have a special case of d, d<n>\<string>.  So we must get
            # <n>, and then the <n>-length <string>.
            if 48 <= ord(s[index + 1]) <= 57:
                d_n, index = build_num(s, index)
                index = index + 2
                d_s = s[index:(index + d_n)]
                index = index + d_n - 1
            else:
                index = index + 1
                d_s = s[index]
            instructions.append(["d", d_s])
        elif s[index] == "s":
            # If the instruction is s, then we must determine if it is a multi-
            # char substitution or not.  If the character following the s is
            # a number, then it is a multi-char substitution and the strings
            # must be built.  Otherwise, the strings are simply the two chars
            # that follow the s.  Then the index must be advanced accordingly.
            if 48 <= ord(s[index + 1]) <= 57:
                n1, index = build_num(s, index)
                index = index + 2
                str1 = s[index:(index + n1)]
                index = index + n1
                n2, index = build_num(s, index)
                index = index + 2
                str2 = s[index:(index + n2)]
                index = index + n2 - 1
            else:
                str1 = s[index + 1]
                str2 = s[index + 2]
                index = index + 2
            instructions.append(["s", str1, str2])
        elif s[index] == "x":
            instructions.append(["x", s[index + 1]])
            index = index + 1
        elif s[index] in ["m", "a", "o"]:
            # If we have a special instruction, then all characters from that
            # character to the end of the line are the string associated with
            # the instruction.  So we save that and the instruction to the list.
            # Then the index must be advanced accordingly.
            trailing_str = s[index + 1:]
            instructions.append([s[index], trailing_str])
            index = len(s)
        if index < len(s):
            index = index + 1
    return instructions

# This function takes a string and current index as arguments.  The current
# index should be before the start of the number.  This is used to make the
# number negative, if necessary.  It then builds the number until the current
# character is no longer a digit.  It then returns the number and the new index.
# This allows what called the function to pick up after the number.
def build_num(s, i):
    num = ""
    if s[i] == "-":
        num = num + "-"
    while i + 1 < len(s) and 48 <= ord(str(s[i + 1])) <= 57:
        # Whenever the current character is a digit within bounds of s, 
        # it will add that digit and advance the index of the string.
        i = i + 1
        num = num + s[i]
    return int(num), i

# Receives a single line as a string s, and the instruction list i.
# Performs the instructions in the proper order on that string.
# Then returns the string.
def decrypt_text(s, i):
    decrypted_string = s
    index = 0
    while index < len(i):
        command = i[index][0]
        if command == "+":
            shift_by = i[index][1]
            decrypted_string = shift(decrypted_string, shift_by)
        if command == "r":
            decrypted_string = flip(decrypted_string)
        if command == "d":
            decrypted_string = flush(decrypted_string, i[index][1])
        if command == "s":
            decrypted_string = swap(decrypted_string, i[index][1], i[index][2])
        if command == "x":
            decrypted_string = trim(decrypted_string, i[index][1])
        if command == "m":
            decrypted_string = mono_cipher(decrypted_string, i[index][1])
        if command == "a":
            decrypted_string = auto_cipher(decrypted_string, i[index][1])
        if command == "o":
            decrypted_string = one_time_pad(decrypted_string, i[index][1])
        index = index + 1
    return decrypted_string

# Returns a new string that is equivalent to the argument string
# shifted by n ASCII values, where n may be a positive or negative int.
def shift(string, n):
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

# Returns a new string that is a copy of the string provided but in 
# reverse order. 
def flip(string):
    r_string = ""
    for i in range(len(string) - 1, -1, -1):
        r_string = r_string + string[i]
    return r_string
    
# Returns a new string that is a copy of the string provided but with 
# all characters in the target string removed. 
def flush(string, target):
    f_string = ""
    for i in range(0, len(string)):
        if string[i] not in target:
            f_string = f_string + string[i]
    return f_string
    
# Returns a new string that is a copy of the string provided but with 
# every occurrence of the substring s1 replaced with the substring s2. 
def swap(string, s1, s2):
    # The function starts with an empty string.
    s_string = ""
    i = 0
    while i < len(string):
        # It will iterate through the characters in string, looking for the
        # first character of s1.
        if string[i] != s1[0]:
            # If a character does not match the first character of s1, then
            # the current character is added to the growing string
            s_string = s_string + string[i]
        else:
            # If a character does match the first character of s1, the function
            # checks the trailing characters to see if they match s1.
            # If so, it inserts s2 and increments the count accordingly
            # to skip the rest of the characters of s1 in string.
            # If it does not match s1, then that character is added to s_string.
            if string[i:(i + len(s1))] == s1:
                s_string = s_string + s2
                i = i + len(s1) - 1
            else:
                s_string = s_string + string[i]
        i = i + 1
    return s_string
    
# Returns a new string that is a copy of the string provided but with 
# multiple consecutive occurrences of character c reduced to a single 
# character c. 
def trim(string, c):
    # The function builds a new string, checking each character against
    # several variables to determine if it is a repeated character
    # which is designated to be removed.
    t_string = ""
    char_detected = False
    char = ""
    for i in range(len(string)):
        if string[i] in c:
            if char_detected:
                if string[i] != char:
                    t_string = t_string + string[i]
                    char_detected = True
                    char = string[i]
            else:
                t_string = t_string + string[i]
                char_detected = True
                char = string[i]
        else:
            t_string = t_string + string[i]
            char_detected = False
            char = ""
    return t_string

# Returns a new string decoded with the monoalphabetic cipher.
# Takes two strings as arguments.  The first is the string to decode, the 
# second is the filename of the file to access for the cipher.
def mono_cipher(string, filename):
    f = open(filename, "r")
    cipher = f.readline()
    f.close()
    decrypted_string = ""
    for char in string:
        # The index of a given character in the cipher string will be the index
        # of the decoded character in the ordered list of all ASCII characters.
        # We don't have to make a list of ASCII characters though, we can just
        # just add the index of the character in cipher to 32 and use chr().
        index = cipher.index(char)
        decrypted_string = decrypted_string + chr(index + 32)
    return decrypted_string

# Returns a new string decoded with the auto-key cipher.
# Takes two strings.  The first is the string to decode, and the second is
# the keyword to be used.  
def auto_cipher(string, keyword):
    decrypted_string = ""
    i1 = 0
    i2 = 0
    while i1 < len(keyword):
        decrypted_string = decrypted_string + decrypt_char(string[i1], keyword[i1])
        i1 = i1 + 1
    while i1 < len(string):
        decrypted_string = decrypted_string + decrypt_char(string[i1], decrypted_string[i2])
        i1 = i1 + 1
        i2 = i2 + 1
    return decrypted_string

# Returns a new string decoded with the one time pad cipher.  The first
# argument is a string to be decoded, and the second is the filename of the 
# one-time pad to use.
def one_time_pad(string, filename):
    f = open(filename, "r")
    key = f.readline()
    f.close()
    decrypted_string = ""
    i = 0
    while i < len(string):
        decrypted_string = decrypted_string + decrypt_char(string[i], key[i])
        i = i + 1
    return decrypted_string

def decrypt_char(char, key_char):
    new_char = chr(((ord(char) - ord(key_char)) % 95) + 32)
    return new_char