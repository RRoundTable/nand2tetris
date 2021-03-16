
comp_table = {
    '0':'0101010',  '1':'0111111',  '-1':'0111010', 'D':'0001100', 
    'A':'0110000',  '!D':'0001101', '!A':'0110001', '-D':'0001111', 
    '-A':'0110011', 'D+1':'0011111','A+1':'0110111','D-1':'0001110', 
    'A-1':'0110010','D+A':'0000010','D-A':'0010011','A-D':'0000111', 
    'D&A':'0000000','D|A':'0010101',
    '':'xxxxxxx',   '':'xxxxxxx',   '':'xxxxxxx',   '':'xxxxxxx', 
    'M':'1110000',  '':'xxxxxxx',   '!M':'1110001', '':'xxxxxxx', 
    '-M':'1110011', '':'xxxxxxx',   'M+1':'1110111','':'xxxxxxx', 
    'M-1':'1110010','D+M':'1000010','D-M':'1010011','M-D':'1000111', 
    'D&M':'1000000', 'D|M':'1010101' 
}

dest_table = {
    'null0': '000',
    'M': '001',
    'D': '010',
    'MD': '011',
    'A': '100',
    'AM': '101',
    'AD': '110',
    'AMD': '111',
}

jump_table = {
    'null': '000',
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111',
}



class Code(object):
    def __init__(self) -> None:
        pass

    def dest(self, instruction: str) -> str:
        if "=" in instruction:
            dest = instruction.split('=')[0]
            dest = "".join(d for d in dest if d != " ")
            return dest_table[dest]
        return "000"

    def comp(self, instruction: str) -> str:
        if "=" in instruction:
            comp = instruction.split('=')[1].split("\n")[0]
        elif ";" in instruction:
            comp = instruction.split(';')[0]
        else:
            raise NotImplementedError
        comp = "".join(c for c in comp if c!= " ")
        return comp_table[comp]
        
    def jump(self, instruction: str) -> str:
        if ";" not in instruction: return "000"
        jump = instruction.split(';')[1].split("\n")[0]
        return jump_table[jump]

    def address(self, instruction: str) -> str:
        instruction = "".join([i for i in instruction if i != " "])
        instruction = instruction[1:].split("\n")[0]

        b = bin(int(instruction))[2:]
        address = "0" * (16 - len(b)) + b
        return address