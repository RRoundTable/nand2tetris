from vm_constant import *


class Parser:
    def __init__(self, filepath: str) -> None:
        self.lines = []
        self.idx = 0
        f = open(filepath, 'r')
        while True:
            line = f.readline()
            if not line: break
            if line == "\n": continue 
            if line[:2] == "//": continue
            self.lines.append(line)
        f.close()

        self.ins2com = {
            "add": C_ARITHMETIC,
            "sub": C_ARITHMETIC,
            "neg": C_ARITHMETIC,
            "eq": C_ARITHMETIC,
            "gt": C_ARITHMETIC,
            "lt": C_ARITHMETIC,
            "and": C_ARITHMETIC,
            "or": C_ARITHMETIC,
            "not": C_ARITHMETIC,

            "push": C_PUSH,
            "pop": C_POP,
            "label": C_LABEL,
            "goto": C_GOTO,
            "if": C_IF,
            "function": C_FUNCTION,
            "call": C_CALL,
            "return": C_RETURN
        }
        self.stack = []

    def hasMoreCommands(self) -> bool:
        return self.idx < len(self.lines) 

    def advance(self) -> None:
        self.idx += 1

    def commandType(self) -> str:
        front = self.curr.split(" ")[0].replace("\n", "")
        return self.ins2com[front]

    @property
    def curr(self):
        if self.hasMoreCommands():
            return self.lines[self.idx]
        else:
            print("Has no lines!")
            return None

    def arg1(self) -> str:
        first_arg = ""
        if len(self.curr.split(" ")) >= 2:
            first_arg = self.curr.split(" ")[1].replace("\n", "")
        return first_arg

    def arg2(self) -> int:
        second_arg = ""
        if len(self.curr.split(" ")) >= 2:
            second_arg = self.curr.split(" ")[2].replace("\n", "")
        return second_arg

    def arithmetic(self) -> str:
        arithmetic = self.curr.replace("\n", "")
        return arithmetic