
from typing import List
from code import Code
from symbol_table import SymbolTable
import os
from collections import deque


A = 'A_COMMAND'
C = 'C_COMMAND'
L = 'L_COMMAND'

class Parser:
    def __init__(self, assembly_path: str) -> None:
        self.coder = Code()
        self.symbol_table = SymbolTable()
        self.assembly = []
        self.idx = 0

        f = open(assembly_path, 'r')
        while True:
            line = f.readline()
            if not line: break
            if line[:2] == "//": continue
            if [e for e in line if e != " "] == ["\n"]:
                continue
            self.assembly.append(line)
        f.close()

    def reset_idx(self):
        self.idx = 0

    def hasMoreCommands(self) -> bool:
        return self.idx < len(self.assembly)

    def advance(self) -> None:
        if self.hasMoreCommands():
            self.idx += 1

    def commandType(self) -> str:
        if self.hasMoreCommands():
            curr = self.assembly[self.idx]
            
            if "@" in curr:
                print("A", curr)
                return A
            elif "=" in curr or ";" in curr:
                print("C", curr)
                return C
            elif "(" in curr:
                return L 
            else:
                return None

    def symbol(self) -> str:
        symbol = "".join([s for s in self.assembly[self.idx] if s != " "])
        symbol = symbol.split("\n")[0]
        if self.commandType() == A:
            symbol = symbol[1:]
            if not self.symbol_table.contains(symbol):
                try:
                    address = int(symbol)
                    self.symbol_table.addEntry(symbol, str(address))
                except:
                    self.symbol_table.addEntry(symbol, str(self.symbol_table.idx))
                    self.symbol_table.advance()
            self.assembly[self.idx] = "@" + self.symbol_table.getAddress(symbol)
        elif self.commandType() == L:
            symbol = symbol[1:-1]
            if not self.symbol_table.contains(symbol):
                self.symbol_table.addEntry(symbol, str(self.idx))
            self.assembly = self.assembly[:self.idx] + self.assembly[self.idx + 1: ]
        else:
            return ""
        
    
        return self.symbol_table.getAddress(symbol)

    def dest(self) -> str:
        if self.commandType() == C:
            return self.coder.dest(self.assembly[self.idx])
        else:
            raise NotImplementedError

    def comp(self) -> str:
        if self.commandType() == C:
            return self.coder.comp(self.assembly[self.idx])
        else:
            raise NotImplementedError
    
    def jump(self) -> str:
        if self.commandType() == C:
            return self.coder.jump(self.assembly[self.idx])
        else:
            raise NotImplementedError

    # def address(self) -> str:
    #     if self.commandType() == A:
    #         return self.coder.address(self.assembly[self.idx])
    #     else:
    #         raise NotImplementedError

    def address(self) -> str:
        instruction = self.assembly[self.idx]
        instruction = "".join([i for i in instruction if i != " "])
        instruction = instruction[1:].split("\n")[0]
        if self.symbol_table.contains(instruction):
            address = self.symbol_table.getAddress(instruction)
        else:
            address = instruction
        
        b = bin(int(address))[2:]
        address = "0" * (16 - len(b)) + b
        return address