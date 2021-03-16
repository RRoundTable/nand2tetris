from parser import Parser
import argparse


A = 'A_COMMAND'
C = 'C_COMMAND'
L = 'L_COMMAND'


class BasicAssembler:
    def __init__(self, assembly_path: str) -> None:
        self._parser = Parser(assembly_path)
        self._save_path = "".join(assembly_path.split(".")[:-1]) + ".hack"

    def run(self):
        f = open(self._save_path, "w")

        # Build symbol table

        while self._parser.hasMoreCommands():
            if self._parser.commandType is not None:
                
                if self._parser.commandType() == L:
                    print(self._parser.idx, self._parser.assembly[self._parser.idx])
                    self._parser.symbol()
                else:  
                    self._parser.advance()
        
        self._parser.reset_idx()

        while self._parser.hasMoreCommands():
            if self._parser.commandType is not None:
                self._parser.symbol()
                self._parser.advance()

        self._parser.reset_idx()
        while self._parser.hasMoreCommands():
            machine_language = ""
            if self._parser.commandType() == C:
                dest = self._parser.dest()
                comp = self._parser.comp()
                jump = self._parser.jump()
                machine_language = f"111{comp}{dest}{jump}\n"
            elif self._parser.commandType() == A:
                machine_language = self._parser.address() + "\n"
            elif self._parser.commandType() == L:
                pass
            
            f.write(machine_language)
            self._parser.advance()
            


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='For Assembler')
    parser.add_argument("filename", type=str, default=None)
    args = parser.parse_args()
    Assembler = BasicAssembler(args.filename)
    Assembler.run()


    